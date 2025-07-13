"""
Data models for Claude prompt synchronization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class Message(BaseModel):
    """Represents a single message in a conversation"""
    role: Optional[str] = None
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    timestamp: Optional[str] = None
    type: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('content', pre=True)
    def extract_content_text(cls, v):
        """Extract text from content if it's a list of content blocks"""
        if isinstance(v, list):
            # Extract text from content blocks
            text_parts = []
            for block in v:
                if isinstance(block, dict) and block.get('type') == 'text':
                    text_parts.append(block.get('text', ''))
            return '\n'.join(text_parts) if text_parts else ''
        return v


class Session(BaseModel):
    """Represents a Claude session"""
    id: str
    project_id: str
    project_path: str
    messages: List[Message] = Field(default_factory=list)
    first_message: Optional[str] = None
    message_timestamp: Optional[str] = None
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.now)
    todo_data: Optional[Union[Dict[str, Any], List]] = None
    
    @validator('todo_data', pre=True)
    def handle_todo_data(cls, v):
        """Handle todo_data that might be an empty list"""
        if isinstance(v, list) and len(v) == 0:
            return None
        return v


class Project(BaseModel):
    """Represents a Claude project"""
    id: str
    path: str
    sessions: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.now)
