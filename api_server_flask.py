"""
Flask API server for Claude Viewer Frontend
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'claude_prompts')

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]


def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'database': MONGODB_DB_NAME})


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        projects = list(db.projects.find().sort('updated_at', -1))
        
        # Add session count and message count for each project
        for project in projects:
            session_count = db.sessions.count_documents({'project_id': project['id']})
            message_count = db.messages.count_documents({'project_id': project['id']})
            project['sessionCount'] = session_count
            project['messageCount'] = message_count
            serialize_doc(project)
        
        return jsonify(projects)
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project by ID"""
    try:
        project = db.projects.find_one({'id': project_id})
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Add session count and message count
        project['sessionCount'] = db.sessions.count_documents({'project_id': project_id})
        project['messageCount'] = db.messages.count_documents({'project_id': project_id})
        
        return jsonify(serialize_doc(project))
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/sessions', methods=['GET'])
def get_project_sessions(project_id):
    """Get all sessions for a project"""
    try:
        sessions = list(db.sessions.find({'project_id': project_id}).sort('created_at', -1))
        for session in sessions:
            serialize_doc(session)
        return jsonify(sessions)
    except Exception as e:
        logger.error(f"Error fetching sessions for project {project_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get a specific session by ID"""
    try:
        session = db.sessions.find_one({'id': session_id})
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        return jsonify(serialize_doc(session))
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions/<session_id>/messages', methods=['GET'])
def get_session_messages(session_id):
    """Get all messages for a session"""
    try:
        messages = list(db.messages.find({'session_id': session_id}).sort('message_index', 1))
        for message in messages:
            serialize_doc(message)
        return jsonify(messages)
    except Exception as e:
        logger.error(f"Error fetching messages for session {session_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search/messages', methods=['GET'])
def search_messages():
    """Search messages by query"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([])
        
        # Create text search query
        search_filter = {
            '$text': {'$search': query}
        }
        
        # Limit results to 100 messages
        messages = list(db.messages.find(search_filter).limit(100))
        for message in messages:
            serialize_doc(message)
        
        return jsonify(messages)
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        # Fallback to regex search if text index doesn't exist
        try:
            regex_filter = {
                'content': {'$regex': query, '$options': 'i'}
            }
            messages = list(db.messages.find(regex_filter).limit(100))
            for message in messages:
                serialize_doc(message)
            return jsonify(messages)
        except Exception as e2:
            logger.error(f"Error with regex search: {e2}")
            return jsonify({'error': str(e2)}), 500


@app.route('/api/search/projects', methods=['GET'])
def search_projects():
    """Search projects by query"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([])
        
        # Search in project path
        search_filter = {
            'path': {'$regex': query, '$options': 'i'}
        }
        
        projects = list(db.projects.find(search_filter))
        for project in projects:
            serialize_doc(project)
        
        return jsonify(projects)
    except Exception as e:
        logger.error(f"Error searching projects: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    try:
        stats = {
            'total_projects': db.projects.count_documents({}),
            'total_sessions': db.sessions.count_documents({}),
            'total_messages': db.messages.count_documents({}),
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Create text index for message search if it doesn't exist
    try:
        db.messages.create_index([('content', 'text')])
        logger.info("Text index created for messages collection")
    except Exception as e:
        logger.warning(f"Could not create text index: {e}")
    
    # Run the server
    port = int(os.getenv('PORT', 15011))
    app.run(host='0.0.0.0', port=port, debug=True)