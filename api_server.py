"""
FastAPI server for Claude Viewer Frontend
"""
import os
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import logging
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from utils import extract_project_info
import time
import hashlib

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost:27017')
MONGODB_USER = os.getenv('MONGODB_USER')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'claude_prompts')

# Build MongoDB URI
if MONGODB_USER and MONGODB_PASSWORD:
    MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}/?authSource=admin&directConnection=true"
else:
    MONGODB_URI = os.getenv('MONGODB_URL', f"mongodb://{MONGODB_HOST}/?directConnection=true")

logger.info(f"Connecting to MongoDB at {MONGODB_HOST} with database {MONGODB_DATABASE}")

# Initialize MongoDB client
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.server_info()
    db = client[MONGODB_DATABASE]
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    db = None

# Simple in-memory cache
cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_cache_key(endpoint: str, params: dict = None) -> str:
    """Generate cache key from endpoint and parameters"""
    if params:
        params_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        return f"{endpoint}?{params_str}"
    return endpoint

def get_from_cache(cache_key: str):
    """Get data from cache if not expired"""
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
        else:
            del cache[cache_key]
    return None

def set_cache(cache_key: str, data):
    """Set data to cache with timestamp"""
    cache[cache_key] = (data, time.time())

def clear_cache():
    """Clear expired cache entries"""
    current_time = time.time()
    expired_keys = [k for k, (_, timestamp) in cache.items() 
                   if current_time - timestamp >= CACHE_DURATION]
    for key in expired_keys:
        del cache[key]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if db is not None:
        try:
            db.messages.create_index([('content', 'text')])
            logger.info("Text index created for messages collection")
        except Exception as e:
            logger.warning(f"Could not create text index: {e}")
    else:
        logger.error("MongoDB connection not available")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(title="Claude Viewer API", version="1.0.0", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ProjectResponse(BaseModel):
    id: str
    path: str
    sessions: List[str]
    created_at: datetime
    updated_at: datetime
    last_synced: datetime
    sessionCount: Optional[int] = 0
    messageCount: Optional[int] = 0
    workspace_type: Optional[str] = None
    branch_info: Optional[str] = None
    last_conversation_date: Optional[datetime] = None  # Most recent message timestamp

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionResponse(BaseModel):
    id: str
    project_id: str
    project_path: str
    first_message: Optional[str] = None
    message_timestamp: Optional[datetime] = None
    message_count: int
    todo_data: Optional[Any] = None  # Can be dict or list
    created_at: datetime
    updated_at: datetime
    last_synced: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageResponse(BaseModel):
    id: str = Field(alias="_id")
    session_id: str
    project_id: str
    message_index: int
    type: Optional[str] = None
    role: Optional[str] = None
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
    raw_data: Dict[str, Any]
    last_synced: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StatsResponse(BaseModel):
    total_projects: int
    total_sessions: int
    total_messages: int


class HealthResponse(BaseModel):
    status: str
    database: str


class ProjectGroupResponse(BaseModel):
    project_name: str
    workspaces: List[ProjectResponse]
    total_sessions: int
    total_messages: int
    last_updated: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc


def get_last_conversation_date(project_id: str, db) -> Optional[datetime]:
    """Get the most recent message timestamp for a project"""
    try:
        # Get the most recent message across all sessions in the project
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$match": {"timestamp": {"$ne": None}}},
            {"$sort": {"timestamp": -1}},
            {"$limit": 1},
            {"$project": {"timestamp": 1}}
        ]
        
        result = list(db.messages.aggregate(pipeline))
        if result and result[0].get('timestamp'):
            # Parse timestamp string to datetime
            timestamp_str = result[0]['timestamp']
            if isinstance(timestamp_str, str):
                try:
                    # Handle ISO format timestamps
                    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    pass
        
        # Fallback: check session message_timestamp fields
        sessions = list(db.sessions.find(
            {"project_id": project_id, "message_timestamp": {"$ne": None}},
            {"message_timestamp": 1}
        ).sort("message_timestamp", -1).limit(1))
        
        if sessions and sessions[0].get('message_timestamp'):
            timestamp_str = sessions[0]['message_timestamp']
            if isinstance(timestamp_str, str):
                try:
                    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    pass
                    
        return None
    except Exception as e:
        logger.error(f"Error getting last conversation date for project {project_id}: {e}")
        return None


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", database=MONGODB_DATABASE)

@app.post("/api/cache/clear")
async def clear_api_cache():
    """Clear API cache"""
    clear_cache()
    return {"message": "Cache cleared successfully"}


@app.get("/api/projects/grouped", response_model=List[ProjectGroupResponse])
async def get_projects_grouped(
    limit: int = Query(default=50, ge=1, le=200, description="Number of projects to return"),
    skip: int = Query(default=0, ge=0, description="Number of projects to skip")
):
    """Get projects grouped by project name"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check cache first
    cache_key = get_cache_key("projects_grouped", {"limit": limit, "skip": skip})
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result
    
    try:
        projects = list(db.projects.find().sort('updated_at', -1).skip(skip).limit(limit))
        
        # Group projects by extracted project name
        grouped = {}
        for project in projects:
            # Extract project info
            project_info = extract_project_info(project['path'])
            project_name = project_info['project_name']
            
            if not project_name:
                project_name = 'Unknown'
            
            # Initialize group if not exists
            if project_name not in grouped:
                grouped[project_name] = {
                    'project_name': project_name,
                    'workspaces': [],
                    'total_sessions': 0,
                    'total_messages': 0,
                    'last_updated': project['updated_at']
                }
            
            # Use cached statistics if available, otherwise calculate
            if 'session_count' in project and 'message_count' in project:
                session_count = project['session_count']
                message_count = project['message_count']
                last_conversation = project.get('last_conversation_date')
            else:
                # Fallback to real-time calculation
                session_count = db.sessions.count_documents({'project_id': project['id']})
                message_count = db.messages.count_documents({'project_id': project['id']})
                last_conversation = get_last_conversation_date(project['id'], db)
            
            # Add project metadata
            project['sessionCount'] = session_count
            project['messageCount'] = message_count
            project['workspace_type'] = project_info['workspace_type']
            project['branch_info'] = project_info['branch_info']
            project['last_conversation_date'] = last_conversation
            serialize_doc(project)
            
            # Update group
            grouped[project_name]['workspaces'].append(project)
            grouped[project_name]['total_sessions'] += session_count
            grouped[project_name]['total_messages'] += message_count
            
            # Update last_updated to the most recent
            if project['updated_at'] > grouped[project_name]['last_updated']:
                grouped[project_name]['last_updated'] = project['updated_at']
        
        # Convert to list and sort by last updated
        result = list(grouped.values())
        
        # Sort workspaces within each group by last conversation date
        for group in result:
            group['workspaces'].sort(
                key=lambda w: w.get('last_conversation_date') or w.get('updated_at'), 
                reverse=True
            )
        
        result.sort(key=lambda x: x['last_updated'], reverse=True)
        
        # Cache the result
        set_cache(cache_key, result)
        
        return result
    except Exception as e:
        logger.error(f"Error fetching grouped projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(
    limit: int = Query(default=50, ge=1, le=200, description="Number of projects to return"),
    skip: int = Query(default=0, ge=0, description="Number of projects to skip")
):
    """Get all projects"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check cache first
    cache_key = get_cache_key("projects", {"limit": limit, "skip": skip})
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result
    
    try:
        projects = list(db.projects.find().sort('updated_at', -1).skip(skip).limit(limit))
        
        # Add session count, message count, and last conversation date for each project
        for project in projects:
            # Use cached statistics if available, otherwise calculate
            if 'session_count' in project and 'message_count' in project:
                session_count = project['session_count']
                message_count = project['message_count']
                last_conversation = project.get('last_conversation_date')
            else:
                # Fallback to real-time calculation
                session_count = db.sessions.count_documents({'project_id': project['id']})
                message_count = db.messages.count_documents({'project_id': project['id']})
                last_conversation = get_last_conversation_date(project['id'], db)
            
            project['sessionCount'] = session_count
            project['messageCount'] = message_count
            project['last_conversation_date'] = last_conversation
            
            serialize_doc(project)
        
        # Sort projects by last conversation date (most recent first)
        projects.sort(
            key=lambda p: p.get('last_conversation_date') or p.get('updated_at'), 
            reverse=True
        )
        
        # Cache the result
        set_cache(cache_key, projects)
        
        return projects
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get a specific project by ID"""
    try:
        project = db.projects.find_one({'id': project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Add session count, message count, and last conversation date
        project['sessionCount'] = db.sessions.count_documents({'project_id': project_id})
        project['messageCount'] = db.messages.count_documents({'project_id': project_id})
        
        # Get last conversation date
        last_conversation = get_last_conversation_date(project_id, db)
        project['last_conversation_date'] = last_conversation
        
        serialize_doc(project)
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/sessions", response_model=List[SessionResponse])
async def get_project_sessions(project_id: str):
    """Get all sessions for a project"""
    try:
        sessions = list(db.sessions.find({'project_id': project_id}).sort('created_at', -1))
        for session in sessions:
            serialize_doc(session)
        return sessions
    except Exception as e:
        logger.error(f"Error fetching sessions for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get a specific session by ID"""
    try:
        session = db.sessions.find_one({'id': session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        serialize_doc(session)
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: str):
    """Get all messages for a session"""
    try:
        messages = list(db.messages.find({'session_id': session_id}).sort('message_index', 1))
        for message in messages:
            serialize_doc(message)
        return messages
    except Exception as e:
        logger.error(f"Error fetching messages for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/messages", response_model=List[MessageResponse])
async def search_messages(q: str = Query(..., description="Search query")):
    """Search messages by query"""
    try:
        if not q:
            return []
        
        # Create text search query
        search_filter = {
            '$text': {'$search': q}
        }
        
        # Limit results to 100 messages
        messages = list(db.messages.find(search_filter).limit(100))
        for message in messages:
            serialize_doc(message)
        
        return messages
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        # Fallback to regex search if text index doesn't exist
        try:
            regex_filter = {
                'content': {'$regex': q, '$options': 'i'}
            }
            messages = list(db.messages.find(regex_filter).limit(100))
            for message in messages:
                serialize_doc(message)
            return messages
        except Exception as e2:
            logger.error(f"Error with regex search: {e2}")
            raise HTTPException(status_code=500, detail=str(e2))


@app.get("/api/search/projects", response_model=List[ProjectResponse])
async def search_projects(q: str = Query(..., description="Search query")):
    """Search projects by query"""
    try:
        if not q:
            return []
        
        # Search in project path
        search_filter = {
            'path': {'$regex': q, '$options': 'i'}
        }
        
        projects = list(db.projects.find(search_filter))
        for project in projects:
            serialize_doc(project)
        
        return projects
    except Exception as e:
        logger.error(f"Error searching projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get overall statistics"""
    try:
        stats = StatsResponse(
            total_projects=db.projects.count_documents({}),
            total_sessions=db.sessions.count_documents({}),
            total_messages=db.messages.count_documents({})
        )
        return stats
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == '__main__':
    import uvicorn
    
    # Run the server
    port = int(os.getenv('PORT', 15011))
    uvicorn.run("api_server:app", host='0.0.0.0', port=port, reload=True)