"""
Utility functions for Claude prompt synchronization
"""
import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

logger = logging.getLogger(__name__)


def get_claude_dir() -> Path:
    """Get the Claude directory path"""
    return Path.home() / ".claude"


def decode_project_path(encoded: str) -> str:
    """
    Decode a project directory name back to its original path.
    The directory names in ~/.claude/projects are encoded paths.
    """
    # This is a simplified decoder - the actual encoding might be more complex
    return encoded.replace('-', '/')


def get_project_path_from_sessions(project_dir: Path) -> Optional[str]:
    """
    Extract the actual project path by reading session files.
    This is more reliable than decoding the directory name.
    """
    try:
        # Look for any JSONL file in the project directory
        for jsonl_file in project_dir.glob("*.jsonl"):
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if 'projectPath' in entry:
                            return entry['projectPath']
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.warning(f"Failed to get project path from sessions: {e}")
    
    return None


def extract_first_user_message(jsonl_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the first valid user message from a JSONL file.
    Returns (message_content, timestamp)
    """
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Check if this is a message entry
                    if 'message' in entry and isinstance(entry['message'], dict):
                        message = entry['message']
                        
                        # Check if it's a user message
                        if message.get('role') == 'user':
                            content = message.get('content', '')
                            
                            # Handle list-based content format
                            if isinstance(content, list):
                                text_parts = []
                                for block in content:
                                    if isinstance(block, dict) and block.get('type') == 'text':
                                        text_parts.append(block.get('text', ''))
                                content = '\n'.join(text_parts) if text_parts else ''
                            
                            # Skip caveat messages
                            if 'Caveat: The messages below were generated' in content:
                                continue
                            
                            # Skip command messages
                            if content.startswith('<command-name>'):
                                continue
                            
                            # Return the first valid user message
                            timestamp = entry.get('timestamp')
                            return content, timestamp
                            
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        logger.warning(f"Failed to extract first user message: {e}")
    
    return None, None


def parse_jsonl_messages(jsonl_path: Path) -> List[Dict[str, Any]]:
    """
    Parse all messages from a JSONL file.
    Returns a list of message dictionaries.
    """
    messages = []
    
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    
                    # Add line number for debugging
                    entry['_line_number'] = line_num
                    
                    messages.append(entry)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse line {line_num} in {jsonl_path}: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"Failed to read JSONL file {jsonl_path}: {e}")
    
    return messages


def get_file_creation_time(file_path: Path) -> datetime:
    """Get the creation time of a file"""
    try:
        stat = file_path.stat()
        # Use creation time if available, otherwise modification time
        timestamp = stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_mtime
        return datetime.fromtimestamp(timestamp)
    except Exception:
        return datetime.now()


def extract_project_info(path: str) -> Dict[str, str]:
    """
    Extract project information from path
    
    Returns:
        dict: Contains project_name, workspace_type, and branch_info
    """
    # Default values
    project_info = {
        'project_name': None,
        'workspace_type': 'unknown',
        'branch_info': ''
    }
    
    # Extract project name from /projects/ pattern
    project_match = re.search(r'/projects/(.+?)$', path)
    if project_match:
        # Get full project path after /projects/
        project_info['project_name'] = project_match.group(1)
    else:
        # No /projects/ folder, use the last meaningful folder name
        path_parts = [p for p in path.split('/') if p and p != 'workspace']
        if path_parts:
            project_info['project_name'] = path_parts[-1]
    
    # Determine workspace type
    if '/hsmoa/backend/release/' in path:
        project_info['workspace_type'] = 'release'
    elif '/hsmoa/backend/projects/' in path:
        project_info['workspace_type'] = 'main' 
    elif '/workspace/' in path and '/projects/' in path:
        # Feature branch pattern: /workspace/{feature}/projects/
        project_info['workspace_type'] = 'feature'
    
    # Extract branch/feature info for feature workspaces
    if project_info['workspace_type'] == 'feature':
        # Pattern: /workspace/{feature_path}/projects/{project}
        feature_match = re.search(r'/workspace/(.+?)/projects/', path)
        if feature_match:
            project_info['branch_info'] = feature_match.group(1).replace('/', '-')
    
    return project_info
