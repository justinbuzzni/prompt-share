"""
Elasticsearch client for indexing and searching Claude prompts
"""
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ElasticsearchClient:
    """Elasticsearch client for Claude prompt indexing and search"""
    
    def __init__(self):
        self.es_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        self.index_name = os.getenv('ELASTICSEARCH_INDEX', 'prompt_share')
        self.es = None
        
    def connect(self) -> bool:
        """Connect to Elasticsearch"""
        try:
            self.es = Elasticsearch([self.es_url], timeout=30, retry_on_timeout=True)
            
            # Test connection
            if not self.es.ping():
                logger.error("Could not connect to Elasticsearch")
                return False
                
            logger.info(f"Connected to Elasticsearch at {self.es_url}")
            
            # Create index if it doesn't exist
            self._create_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            return False
    
    def _create_index(self):
        """Create Elasticsearch index with proper mapping"""
        if self.es.indices.exists(index=self.index_name):
            logger.info(f"Index {self.index_name} already exists")
            return
        
        # Index mapping for Claude prompts
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "session_id": {"type": "keyword"},
                    "project_id": {"type": "keyword"},
                    "project_name": {"type": "keyword"},
                    "project_path": {"type": "keyword"},
                    "workspace_type": {"type": "keyword"},
                    "branch_info": {"type": "text"},
                    "message_index": {"type": "integer"},
                    "type": {"type": "keyword"},
                    "role": {"type": "keyword"},
                    "content": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "english": {
                                "type": "text",
                                "analyzer": "english"
                            }
                        }
                    },
                    "timestamp": {"type": "date"},
                    "created_at": {"type": "date"},
                    "last_synced": {"type": "date"},
                    "tags": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "code_blocks": {
                        "type": "nested",
                        "properties": {
                            "language": {"type": "keyword"},
                            "code": {"type": "text", "analyzer": "keyword"}
                        }
                    }
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "code_analyzer": {
                            "type": "custom",
                            "tokenizer": "keyword",
                            "filter": ["lowercase"]
                        }
                    }
                }
            }
        }
        
        try:
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Created index {self.index_name}")
        except RequestError as e:
            if e.error == 'resource_already_exists_exception':
                logger.info(f"Index {self.index_name} already exists")
            else:
                logger.error(f"Error creating index: {e}")
    
    def index_message(self, message_data: Dict[str, Any], project_data: Dict[str, Any]) -> bool:
        """Index a single message"""
        try:
            # Prepare document for indexing
            doc = {
                "id": message_data.get("_id"),
                "session_id": message_data.get("session_id"),
                "project_id": message_data.get("project_id"),
                "project_name": project_data.get("name", ""),
                "project_path": project_data.get("path", ""),
                "workspace_type": project_data.get("workspace_type", ""),
                "branch_info": project_data.get("branch_info", ""),
                "message_index": message_data.get("message_index", 0),
                "type": message_data.get("type"),
                "role": message_data.get("role"),
                "content": message_data.get("content", ""),
                "timestamp": message_data.get("timestamp"),
                "created_at": datetime.now(),
                "last_synced": message_data.get("last_synced"),
                "tags": self._extract_tags(message_data.get("content", "")),
                "language": self._detect_language(message_data.get("content", "")),
                "code_blocks": self._extract_code_blocks(message_data.get("content", ""))
            }
            
            # Index document
            response = self.es.index(
                index=self.index_name,
                id=message_data.get("_id"),
                body=doc
            )
            
            logger.debug(f"Indexed message {message_data.get('_id')}: {response['result']}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing message {message_data.get('_id')}: {e}")
            return False
    
    def index_messages_bulk(self, messages: List[Dict[str, Any]], project_data: Dict[str, Any]) -> int:
        """Index multiple messages in bulk"""
        if not messages:
            return 0
            
        try:
            actions = []
            for message in messages:
                doc = {
                    "id": message.get("_id"),
                    "session_id": message.get("session_id"),
                    "project_id": message.get("project_id"),
                    "project_name": project_data.get("name", ""),
                    "project_path": project_data.get("path", ""),
                    "workspace_type": project_data.get("workspace_type", ""),
                    "branch_info": project_data.get("branch_info", ""),
                    "message_index": message.get("message_index", 0),
                    "type": message.get("type"),
                    "role": message.get("role"),
                    "content": message.get("content", ""),
                    "timestamp": message.get("timestamp"),
                    "created_at": datetime.now(),
                    "last_synced": message.get("last_synced"),
                    "tags": self._extract_tags(message.get("content", "")),
                    "language": self._detect_language(message.get("content", "")),
                    "code_blocks": self._extract_code_blocks(message.get("content", ""))
                }
                
                actions.append({
                    "_index": self.index_name,
                    "_id": message.get("_id"),
                    "_source": doc
                })
            
            from elasticsearch.helpers import bulk
            success_count, errors = bulk(self.es, actions, chunk_size=100)
            
            if errors:
                logger.warning(f"Bulk indexing had {len(errors)} errors")
            
            logger.info(f"Bulk indexed {success_count} messages for project {project_data.get('id')}")
            return success_count
            
        except Exception as e:
            logger.error(f"Error bulk indexing messages: {e}")
            return 0
    
    def search_messages(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                       size: int = 50, from_: int = 0) -> Dict[str, Any]:
        """Search messages with optional filters"""
        try:
            # Build search query
            search_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": [
                                        "content^3",
                                        "content.english^2",
                                        "project_name^2",
                                        "project_path",
                                        "tags"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                },
                "highlight": {
                    "fields": {
                        "content": {
                            "fragment_size": 150,
                            "number_of_fragments": 3
                        }
                    }
                },
                "sort": [
                    {"timestamp": {"order": "desc"}},
                    "_score"
                ],
                "size": size,
                "from": from_
            }
            
            # Apply filters if provided
            if filters:
                filter_conditions = []
                
                if filters.get("project_id"):
                    filter_conditions.append({"term": {"project_id": filters["project_id"]}})
                
                if filters.get("session_id"):
                    filter_conditions.append({"term": {"session_id": filters["session_id"]}})
                
                if filters.get("role"):
                    filter_conditions.append({"term": {"role": filters["role"]}})
                
                if filters.get("project_name"):
                    filter_conditions.append({"term": {"project_name": filters["project_name"]}})
                
                if filters.get("date_from"):
                    filter_conditions.append({"range": {"timestamp": {"gte": filters["date_from"]}}})
                
                if filters.get("date_to"):
                    filter_conditions.append({"range": {"timestamp": {"lte": filters["date_to"]}}})
                
                if filter_conditions:
                    search_query["query"]["bool"]["filter"] = filter_conditions
            
            # Execute search
            response = self.es.search(index=self.index_name, body=search_query)
            
            # Process results
            results = {
                "total": response["hits"]["total"]["value"],
                "max_score": response["hits"]["max_score"],
                "hits": []
            }
            
            for hit in response["hits"]["hits"]:
                result = {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"],
                    "highlight": hit.get("highlight", {})
                }
                results["hits"].append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return {"total": 0, "max_score": 0, "hits": []}
    
    def delete_project_messages(self, project_id: str) -> bool:
        """Delete all messages for a project"""
        try:
            response = self.es.delete_by_query(
                index=self.index_name,
                body={
                    "query": {
                        "term": {"project_id": project_id}
                    }
                }
            )
            
            deleted_count = response.get("deleted", 0)
            logger.info(f"Deleted {deleted_count} messages for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting messages for project {project_id}: {e}")
            return False
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from message content"""
        tags = []
        
        # Simple tag extraction logic
        if "python" in content.lower():
            tags.append("python")
        if "javascript" in content.lower() or "js" in content.lower():
            tags.append("javascript")
        if "docker" in content.lower():
            tags.append("docker")
        if "api" in content.lower():
            tags.append("api")
        if "database" in content.lower() or "db" in content.lower():
            tags.append("database")
        if "error" in content.lower() or "bug" in content.lower():
            tags.append("error")
        if "fix" in content.lower() or "solve" in content.lower():
            tags.append("fix")
        
        return tags
    
    def _detect_language(self, content: str) -> str:
        """Detect primary language from content"""
        if not content:
            return "unknown"
        
        # Simple language detection
        if "def " in content or "import " in content or "python" in content.lower():
            return "python"
        if "function" in content or "const " in content or "let " in content:
            return "javascript"
        if "SELECT" in content.upper() or "FROM" in content.upper():
            return "sql"
        if "docker" in content.lower() or "FROM " in content:
            return "docker"
        
        return "text"
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from content"""
        code_blocks = []
        
        # Simple code block extraction (looking for ``` blocks)
        import re
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match[0] if match[0] else "unknown"
            code = match[1].strip()
            code_blocks.append({
                "language": language,
                "code": code
            })
        
        return code_blocks
    
    def close(self):
        """Close Elasticsearch connection"""
        if self.es:
            self.es.close()
            logger.info("Elasticsearch connection closed")