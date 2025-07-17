"""
Claude Prompt Synchronization Tool
Syncs Claude prompt data from local storage to MongoDB
"""

import argparse
import configparser
import json
import logging
import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, OperationFailure

from models import Message, Project, Session
from utils import (
    decode_project_path,
    extract_first_user_message,
    get_claude_dir,
    get_file_creation_time,
    get_project_path_from_sessions,
    parse_jsonl_messages,
)
from security_utils import redact_message_content, scan_and_report
from elasticsearch_client import ElasticsearchClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ClaudeSyncManager:
    """Manager class for syncing Claude data to MongoDB"""

    def __init__(self, selected_repos: Optional[Set[str]] = None, selected_owners: Optional[Set[str]] = None, enable_redaction: bool = True):
        """Initialize the sync manager
        
        Args:
            selected_repos: Set of repository names to sync. If None, sync all.
            selected_owners: Set of repository owners to sync. If None, sync all.
            enable_redaction: Whether to redact sensitive information before storing.
        """
        self.mongo_client = None
        self.db = None
        self.projects_collection = None
        self.sessions_collection = None
        self.messages_collection = None
        self.claude_dir = get_claude_dir()
        self.projects_dir = self.claude_dir / "projects"
        self.todos_dir = self.claude_dir / "todos"
        self.selected_repos = selected_repos
        self.selected_owners = selected_owners
        self.enable_redaction = enable_redaction
        self.redaction_stats = {}
        
        # Elasticsearch client
        self.es_client = ElasticsearchClient()

    def connect_mongodb(self) -> bool:
        """Connect to MongoDB using environment variables"""
        try:
            # Get MongoDB configuration from environment
            mongo_url = os.getenv("MONGODB_URL")
            mongo_user = os.getenv("MONGODB_USER")
            mongo_password = os.getenv("MONGODB_PASSWORD")
            mongo_database = os.getenv("MONGODB_DATABASE")

            if not all([mongo_url, mongo_user, mongo_password, mongo_database]):
                logger.error("Missing MongoDB configuration in .env file")
                return False
            # Create MongoDB connection with authentication
            connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_url.replace('mongodb://', '')}"
            self.mongo_client = MongoClient(connection_string)

            # Test connection
            self.mongo_client.admin.command("ping")

            # Select database and collections
            self.db = self.mongo_client[mongo_database]
            self.projects_collection = self.db["projects"]
            self.sessions_collection = self.db["sessions"]
            self.messages_collection = self.db["messages"]

            # Create indexes for better performance
            self._create_indexes()

            logger.info(f"Successfully connected to MongoDB database: {mongo_database}")
            
            # Connect to Elasticsearch
            if self.es_client.connect():
                logger.info("Connected to Elasticsearch successfully")
            else:
                logger.warning("Failed to connect to Elasticsearch - search functionality will be disabled")
            
            return True

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False

    def _create_indexes(self):
        """Create MongoDB indexes for better query performance"""
        try:
            # Projects collection indexes
            self.projects_collection.create_index("id", unique=True)
            self.projects_collection.create_index("path")
            self.projects_collection.create_index("created_at")

            # Sessions collection indexes
            self.sessions_collection.create_index("id", unique=True)
            self.sessions_collection.create_index("project_id")
            self.sessions_collection.create_index("created_at")
            self.sessions_collection.create_index([("project_id", 1), ("id", 1)])

            # Messages collection indexes
            self.messages_collection.create_index("session_id")
            self.messages_collection.create_index("timestamp")
            self.messages_collection.create_index([("session_id", 1), ("timestamp", 1)])

            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")

    def extract_repo_info_from_git_config(self, base_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract repository owner and name from .git/config file
        
        Returns:
            Tuple of (owner, repo_name)
        """
        # Find .git directory by traversing up the directory tree
        current_path = Path(base_path)
        
        while current_path != current_path.parent:
            git_config_path = current_path / '.git' / 'config'
            if git_config_path.exists():
                try:
                    config = configparser.ConfigParser()
                    config.read(git_config_path)
                    
                    # Look for remote "origin" section
                    if 'remote "origin"' in config:
                        url = config['remote "origin"'].get('url', '')
                        
                        # Parse GitHub URL patterns
                        # https://github.com/owner/repo.git
                        # git@github.com:owner/repo.git
                        # https://github.com/owner/repo
                        
                        # Remove .git suffix if present
                        url = url.rstrip('.git')
                        
                        # Extract owner/repo from different URL formats
                        patterns = [
                            r'github\.com[:/]([^/]+)/([^/\s]+)',  # Matches both HTTPS and SSH
                            r'gitlab\.com[:/]([^/]+)/([^/\s]+)',
                            r'bitbucket\.org[:/]([^/]+)/([^/\s]+)',
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, url)
                            if match:
                                owner = match.group(1)
                                repo = match.group(2)
                                logger.debug(f"Found git config: {base_path} -> owner={owner}, repo={repo}")
                                return owner, repo
                
                except Exception as e:
                    logger.debug(f"Failed to parse git config at {git_config_path}: {e}")
            
            # Move up one directory
            current_path = current_path.parent
        
        return None, None

    def extract_repo_info(self, project_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract repository owner and name from project path
        
        First tries to extract from .git/config, then falls back to path parsing.
        
        Returns:
            Tuple of (owner, repo_name)
        """
        # First try to get info from git config
        owner, repo = self.extract_repo_info_from_git_config(project_path)
        if owner and repo:
            return owner, repo
        
        # Without Git config, we can't reliably determine the owner
        # So we'll only extract the repository name
        
        # Handle /workspace/ paths
        if '/workspace/' in project_path:
            workspace_part = project_path.split('/workspace/')[1]
            parts = workspace_part.split('/')
            
            # Extract what looks like the main repository/project name
            if len(parts) >= 1:
                repo_name = parts[0]
                
                # If there's a /projects/ subdirectory, use what comes after it
                if '/projects/' in workspace_part:
                    proj_parts = workspace_part.split('/projects/')[1].split('/')
                    if proj_parts:
                        # Return None for owner since we can't determine it without Git
                        return None, proj_parts[0]
                
                # Return the first significant folder as repo name
                return None, repo_name
        
        # Last resort: extract last folder name
        parts = project_path.rstrip('/').split('/')
        return None, parts[-1] if parts else None
    
    def extract_repo_name(self, project_path: str) -> Optional[str]:
        """Extract repository name from project path (backward compatibility)"""
        _, repo_name = self.extract_repo_info(project_path)
        return repo_name

    def scan_projects(self) -> List[Project]:
        """Scan all projects in the Claude directory"""
        projects = []
        if not self.projects_dir.exists():
            logger.warning(f"Projects directory does not exist: {self.projects_dir}")
            return projects

        logger.info(f"Scanning projects in: {self.projects_dir}")
        if self.selected_repos:
            logger.info(f"Filtering for repositories: {', '.join(self.selected_repos)}")
        if self.selected_owners:
            logger.info(f"Filtering for owners: {', '.join(self.selected_owners)}")

        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            try:
                project_id = project_dir.name

                # Get project path
                project_path = get_project_path_from_sessions(project_dir)
                if not project_path:
                    project_path = decode_project_path(project_id)

                # Check if this project belongs to selected repositories or owners
                owner, repo_name = self.extract_repo_info(project_path)
                
                # Filter by repository name if specified
                if self.selected_repos:
                    if not repo_name or repo_name not in self.selected_repos:
                        logger.debug(f"Skipping project {project_path} (repo: {repo_name})")
                        continue
                
                # Filter by owner if specified
                if self.selected_owners:
                    if not owner or owner not in self.selected_owners:
                        logger.debug(f"Skipping project {project_path} (owner: {owner})")
                        continue

                # Get session IDs
                session_ids = []
                for jsonl_file in project_dir.glob("*.jsonl"):
                    session_ids.append(jsonl_file.stem)

                # Create project object
                project = Project(
                    id=project_id,
                    path=project_path,
                    sessions=session_ids,
                    created_at=get_file_creation_time(project_dir),
                )
                projects.append(project)
                logger.info(
                    f"Found project: {project_id} with {len(session_ids)} sessions"
                )

            except Exception as e:
                logger.error(f"Failed to process project {project_dir.name}: {e}")
                continue

        return projects

    def scan_sessions(self, project: Project) -> List[Session]:
        """Scan all sessions for a given project"""
        sessions = []
        project_dir = self.projects_dir / project.id

        logger.info(f"Scanning sessions for project: {project.id}")

        for session_file in project_dir.glob("*.jsonl"):
            try:
                session_id = session_file.stem

                # Extract first user message
                first_message, message_timestamp = extract_first_user_message(
                    session_file
                )

                # Load TODO data if exists
                todo_file = self.todos_dir / f"{session_id}.json"
                todo_data = None
                if todo_file.exists():
                    try:
                        with open(todo_file, "r") as f:
                            todo_data = json.load(f)
                    except Exception as e:
                        logger.warning(
                            f"Failed to load TODO data for session {session_id}: {e}"
                        )

                # Parse all messages
                raw_messages = parse_jsonl_messages(session_file)
                messages = []

                for raw_msg in raw_messages:
                    # Extract content
                    content = raw_msg.get("message", {}).get("content") if "message" in raw_msg else None
                    
                    # Handle list-based content format (for tool use, etc.)
                    if isinstance(content, list):
                        text_parts = []
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                text_parts.append(block.get('text', ''))
                        content = '\n'.join(text_parts) if text_parts else ''
                    
                    # Redact sensitive information if enabled
                    if self.enable_redaction and content:
                        redacted_content, stats = redact_message_content(content)
                        
                        # Update statistics
                        for secret_type, count in stats.items():
                            self.redaction_stats[secret_type] = self.redaction_stats.get(secret_type, 0) + count
                        
                        # Update raw_msg with redacted content
                        if "message" in raw_msg:
                            raw_msg = raw_msg.copy()
                            raw_msg["message"] = raw_msg["message"].copy()
                            raw_msg["message"]["content"] = redacted_content
                        
                        content = redacted_content
                    
                    message = Message(
                        type=raw_msg.get("type"),
                        role=raw_msg.get("message", {}).get("role")
                        if "message" in raw_msg
                        else None,
                        content=content,
                        timestamp=raw_msg.get("timestamp"),
                        raw_data=raw_msg,
                    )
                    messages.append(message)

                # Create session object
                session = Session(
                    id=session_id,
                    project_id=project.id,
                    project_path=project.path,
                    messages=messages,
                    first_message=first_message,
                    message_timestamp=message_timestamp,
                    created_at=get_file_creation_time(session_file),
                    todo_data=todo_data,
                )
                sessions.append(session)
                logger.info(
                    f"Found session: {session_id} with {len(messages)} messages"
                )

            except Exception as e:
                logger.error(f"Failed to process session {session_file.name}: {e}")
                continue

        return sessions

    def sync_project_to_mongodb(self, project: Project) -> bool:
        """Sync a single project to MongoDB"""
        try:
            # Convert to dict and add sync metadata
            project_data = project.model_dump()
            project_data["last_synced"] = datetime.now()

            # Upsert project
            self.projects_collection.update_one(
                {"id": project.id}, {"$set": project_data}, upsert=True
            )

            logger.info(f"Synced project {project.id} to MongoDB")
            return True

        except Exception as e:
            logger.error(f"Failed to sync project {project.id}: {e}")
            return False
    
    def update_project_statistics(self, project_id: str) -> bool:
        """Update project statistics after all sessions are synced"""
        try:
            # Count sessions for this project
            session_count = self.sessions_collection.count_documents({"project_id": project_id})
            
            # Count messages for this project
            message_count = self.messages_collection.count_documents({"project_id": project_id})
            
            # Get the most recent message timestamp
            latest_message = self.messages_collection.find_one(
                {"project_id": project_id, "timestamp": {"$ne": None}},
                {"timestamp": 1},
                sort=[("timestamp", -1)]
            )
            
            # If no message timestamp, try session timestamp
            if not latest_message:
                latest_session = self.sessions_collection.find_one(
                    {"project_id": project_id, "message_timestamp": {"$ne": None}},
                    {"message_timestamp": 1},
                    sort=[("message_timestamp", -1)]
                )
                last_conversation_date = latest_session.get("message_timestamp") if latest_session else None
            else:
                last_conversation_date = latest_message.get("timestamp")
            
            # Update project with cached statistics
            update_data = {
                "session_count": session_count,
                "message_count": message_count,
                "last_conversation_date": last_conversation_date,
                "stats_updated_at": datetime.now()
            }
            
            self.projects_collection.update_one(
                {"id": project_id},
                {"$set": update_data}
            )
            
            logger.info(f"Updated statistics for project {project_id}: {session_count} sessions, {message_count} messages")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update statistics for project {project_id}: {e}")
            return False

    def sync_session_to_mongodb(self, session: Session) -> bool:
        """Sync a single session and its messages to MongoDB"""
        try:
            # Prepare session data without messages
            session_data = session.model_dump(exclude={"messages"})
            session_data["last_synced"] = datetime.now()
            session_data["message_count"] = len(session.messages)

            # Upsert session
            self.sessions_collection.update_one(
                {"id": session.id}, {"$set": session_data}, upsert=True
            )

            # Prepare messages for bulk insert
            if session.messages:
                message_operations = []
                for idx, message in enumerate(session.messages):
                    message_data = message.model_dump()
                    message_data["session_id"] = session.id
                    message_data["project_id"] = session.project_id
                    message_data["message_index"] = idx
                    message_data["last_synced"] = datetime.now()

                    # Create unique ID for message
                    message_id = f"{session.id}_{idx}"

                    message_operations.append(
                        UpdateOne(
                            {"_id": message_id}, {"$set": message_data}, upsert=True
                        )
                    )

                # Bulk write messages
                if message_operations:
                    self.messages_collection.bulk_write(message_operations)
                
                # Index messages in Elasticsearch
                if self.es_client.es and session.messages:
                    try:
                        # Get project data for indexing
                        project_data = self.projects_collection.find_one({"id": session.project_id})
                        if project_data:
                            # Prepare message data for ES indexing
                            es_messages = []
                            for idx, message in enumerate(session.messages):
                                message_data = message.model_dump()
                                message_data["_id"] = f"{session.id}_{idx}"
                                message_data["session_id"] = session.id
                                message_data["project_id"] = session.project_id
                                message_data["message_index"] = idx
                                message_data["last_synced"] = datetime.now()
                                es_messages.append(message_data)
                            
                            # Bulk index to Elasticsearch
                            self.es_client.index_messages_bulk(es_messages, project_data)
                    except Exception as e:
                        logger.warning(f"Failed to index messages to Elasticsearch: {e}")

            logger.info(
                f"Synced session {session.id} with {len(session.messages)} messages"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to sync session {session.id}: {e}")
            return False

    def sync_all(self) -> Dict[str, Any]:
        """Sync all Claude data to MongoDB"""
        stats = {
            "projects_found": 0,
            "projects_synced": 0,
            "sessions_found": 0,
            "sessions_synced": 0,
            "total_messages": 0,
            "errors": [],
            "redaction_stats": {},
        }

        try:  # Connect to MongoDB
            if not self.connect_mongodb():
                stats["errors"].append("Failed to connect to MongoDB")
                return stats

            # Scan all projects
            projects = self.scan_projects()
            stats["projects_found"] = len(projects)

            for project in projects:
                # Sync project
                if self.sync_project_to_mongodb(project):
                    stats["projects_synced"] += 1

                    # Scan and sync sessions
                    sessions = self.scan_sessions(project)
                    stats["sessions_found"] += len(sessions)

                    for session in sessions:
                        if self.sync_session_to_mongodb(session):
                            stats["sessions_synced"] += 1
                            stats["total_messages"] += len(session.messages)
                        else:
                            stats["errors"].append(
                                f"Failed to sync session {session.id}"
                            )
                    
                    # Update project statistics after all sessions are synced
                    self.update_project_statistics(project.id)
                else:
                    stats["errors"].append(f"Failed to sync project {project.id}")

            # Add redaction statistics
            stats["redaction_stats"] = self.redaction_stats
            
            logger.info(f"Sync completed: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Sync failed with error: {e}")
            stats["errors"].append(str(e))
            return stats
        finally:
            self.close()

    def close(self):
        """Close MongoDB and Elasticsearch connections"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")
        
        if self.es_client:
            self.es_client.close()
            logger.info("Elasticsearch connection closed")


def get_available_repos(claude_dir: Path) -> Set[str]:
    """Scan for all available repository names"""
    repos = set()
    projects_dir = claude_dir / "projects"
    
    if not projects_dir.exists():
        return repos
    
    temp_manager = ClaudeSyncManager()
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        
        try:
            project_path = get_project_path_from_sessions(project_dir)
            if not project_path:
                project_path = decode_project_path(project_dir.name)
            
            repo_name = temp_manager.extract_repo_name(project_path)
            if repo_name:
                repos.add(repo_name)
        except Exception:
            continue
    
    return repos


def get_available_owners(claude_dir: Path) -> Set[str]:
    """Scan for all available repository owners from Git configs only"""
    owners = set()
    projects_dir = claude_dir / "projects"
    
    if not projects_dir.exists():
        return owners
    
    temp_manager = ClaudeSyncManager()
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        
        try:
            project_path = get_project_path_from_sessions(project_dir)
            if not project_path:
                project_path = decode_project_path(project_dir.name)
            
            # Only get owners from Git config, not from path guessing
            owner, _ = temp_manager.extract_repo_info_from_git_config(project_path)
            if owner:
                owners.add(owner)
        except Exception:
            continue
    
    return owners


def select_repositories(available_repos: List[str]) -> Set[str]:
    """Interactive repository selection"""
    print("\nAvailable repositories:")
    for i, repo in enumerate(available_repos, 1):
        print(f"  {i}. {repo}")
    
    print(f"\n  0. Sync all repositories")
    print("\nEnter repository numbers to sync (comma-separated), or 0 for all:")
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if user_input == "0":
                return None  # Sync all
            
            selected_indices = [int(x.strip()) for x in user_input.split(',')]
            selected_repos = set()
            
            for idx in selected_indices:
                if 1 <= idx <= len(available_repos):
                    selected_repos.add(available_repos[idx - 1])
                else:
                    print(f"Invalid number: {idx}")
                    raise ValueError
            
            if selected_repos:
                return selected_repos
            else:
                print("No repositories selected. Please try again.")
                
        except (ValueError, IndexError):
            print("Invalid input. Please enter comma-separated numbers (e.g., 1,3,5)")


def select_owners(available_owners: List[str]) -> Set[str]:
    """Interactive owner selection"""
    print("\nAvailable repository owners:")
    for i, owner in enumerate(available_owners, 1):
        print(f"  {i}. {owner}")
    
    print(f"\n  0. Sync all owners")
    print("\nEnter owner numbers to sync (comma-separated), or 0 for all:")
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if user_input == "0":
                return None  # Sync all
            
            selected_indices = [int(x.strip()) for x in user_input.split(',')]
            selected_owners = set()
            
            for idx in selected_indices:
                if 1 <= idx <= len(available_owners):
                    selected_owners.add(available_owners[idx - 1])
                else:
                    print(f"Invalid number: {idx}")
                    raise ValueError
            
            if selected_owners:
                return selected_owners
            else:
                print("No owners selected. Please try again.")
                
        except (ValueError, IndexError):
            print("Invalid input. Please enter comma-separated numbers (e.g., 1,3,5)")


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Claude Prompt Synchronization Tool - Syncs Claude prompt data to MongoDB"
    )
    parser.add_argument(
        '--repos', '-r',
        nargs='+',
        help='Specific repository names to sync (e.g., -r repo1 repo2)'
    )
    parser.add_argument(
        '--owners', '-o',
        nargs='+',
        help='Specific repository owners to sync (e.g., -o owner1 owner2)'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Sync all repositories without prompting'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available repositories and owners and exit'
    )
    parser.add_argument(
        '--no-redaction',
        action='store_true',
        help='Disable automatic redaction of sensitive information'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Claude Prompt Synchronization Tool")
    print("=" * 60)

    # Check if Claude directory exists
    claude_dir = get_claude_dir()
    if not claude_dir.exists():
        print(f"Error: Claude directory not found at {claude_dir}")
        print("Please ensure Claude Code is installed and has been used at least once.")
        sys.exit(1)
    print(f"Found Claude directory: {claude_dir}")
    
    # Get available repositories and owners
    available_repos = sorted(get_available_repos(claude_dir))
    available_owners = sorted(get_available_owners(claude_dir))
    
    # Handle --list option
    if args.list:
        if available_owners:
            print("\nAvailable repository owners:")
            for owner in available_owners:
                print(f"  - {owner}")
        else:
            print("\nNo repository owners found.")
            
        if available_repos:
            print("\nAvailable repositories:")
            for repo in available_repos:
                print(f"  - {repo}")
        else:
            print("\nNo repositories found.")
        sys.exit(0)
    
    # Determine which repos/owners to sync
    selected_repos = None
    selected_owners = None
    
    if args.repos and args.owners:
        print("\nError: Cannot use both --repos and --owners options together.")
        sys.exit(1)
    
    if args.repos:
        # Use repos specified via command line
        selected_repos = set(args.repos)
        # Validate specified repos
        invalid_repos = selected_repos - set(available_repos)
        if invalid_repos:
            print(f"\nWarning: The following repositories were not found: {', '.join(invalid_repos)}")
            selected_repos = selected_repos & set(available_repos)
            if not selected_repos:
                print("No valid repositories specified. Exiting.")
                sys.exit(1)
        print(f"\nSelected repositories: {', '.join(sorted(selected_repos))}")
    elif args.owners:
        # Use owners specified via command line
        selected_owners = set(args.owners)
        # Validate specified owners
        invalid_owners = selected_owners - set(available_owners)
        if invalid_owners:
            print(f"\nWarning: The following owners were not found: {', '.join(invalid_owners)}")
            selected_owners = selected_owners & set(available_owners)
            if not selected_owners:
                print("No valid owners specified. Exiting.")
                sys.exit(1)
        print(f"\nSelected repository owners: {', '.join(sorted(selected_owners))}")
    elif args.all:
        # Sync all without prompting
        print("\nSyncing all repositories...")
        selected_repos = None
        selected_owners = None
    else:
        # Interactive selection - ask user to choose between owner or repo selection
        if available_owners:
            print("\nSelect synchronization method:")
            print("  1. Select by repository owner")
            print("  2. Select by repository name")
            print("  3. Sync all")
            
            while True:
                choice = input("\nEnter your choice (1-3): ").strip()
                if choice == "1":
                    selected_owners = select_owners(available_owners)
                    if selected_owners:
                        print(f"\nSelected repository owners: {', '.join(sorted(selected_owners))}")
                    else:
                        print("\nSyncing all repositories...")
                    break
                elif choice == "2":
                    selected_repos = select_repositories(available_repos)
                    if selected_repos:
                        print(f"\nSelected repositories: {', '.join(sorted(selected_repos))}")
                    else:
                        print("\nSyncing all repositories...")
                    break
                elif choice == "3":
                    print("\nSyncing all repositories...")
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
        elif available_repos:
            # No owners found, fall back to repo selection
            selected_repos = select_repositories(available_repos)
            if selected_repos:
                print(f"\nSelected repositories: {', '.join(sorted(selected_repos))}")
            else:
                print("\nSyncing all repositories...")
        else:
            print("\nNo repositories found. Syncing all projects...")

    # Create sync manager with selected repositories
    enable_redaction = not args.no_redaction
    sync_manager = ClaudeSyncManager(selected_repos, selected_owners, enable_redaction=enable_redaction)
    
    if enable_redaction:
        print("\nSecurity: Sensitive information will be automatically redacted")
    else:
        print("\nWarning: Redaction is disabled. Sensitive information will be stored as-is")

    # Perform sync
    print("\nStarting synchronization...")
    stats = sync_manager.sync_all()

    # Print results
    print("\n" + "=" * 60)
    print("Synchronization Results:")
    print("=" * 60)
    print(f"Projects found: {stats['projects_found']}")
    print(f"Projects synced: {stats['projects_synced']}")
    print(f"Sessions found: {stats['sessions_found']}")
    print(f"Sessions synced: {stats['sessions_synced']}")
    print(f"Total messages: {stats['total_messages']}")

    # Print redaction statistics if enabled
    if enable_redaction and stats.get("redaction_stats"):
        print("\nSecurity Report - Redacted Secrets:")
        print("-" * 40)
        total_redacted = 0
        for secret_type, count in sorted(stats["redaction_stats"].items()):
            print(f"  {secret_type}: {count}")
            total_redacted += count
        print(f"\nTotal secrets redacted: {total_redacted}")
    
    if stats["errors"]:
        print("\nErrors encountered:")
        for error in stats["errors"]:
            print(f"  - {error}")
    else:
        print("\nSync completed successfully!")

    print("=" * 60)


if __name__ == "__main__":
    main()
