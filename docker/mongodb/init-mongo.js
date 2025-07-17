// MongoDB initialization script
db = db.getSiblingDB('prompt_share');

// Create collections
db.createCollection('projects');
db.createCollection('sessions');
db.createCollection('messages');

// Create indexes for better performance

// Projects collection indexes
db.projects.createIndex({ "id": 1 }, { unique: true });
db.projects.createIndex({ "updated_at": -1 });
db.projects.createIndex({ "last_conversation_date": -1 });
db.projects.createIndex({ "path": 1 });
db.projects.createIndex({ "session_count": -1 });
db.projects.createIndex({ "message_count": -1 });

// Sessions collection indexes
db.sessions.createIndex({ "id": 1 }, { unique: true });
db.sessions.createIndex({ "project_id": 1 });
db.sessions.createIndex({ "project_id": 1, "message_timestamp": -1 });
db.sessions.createIndex({ "created_at": -1 });
db.sessions.createIndex({ "message_timestamp": -1 });

// Messages collection indexes
db.messages.createIndex({ "_id": 1 }, { unique: true });
db.messages.createIndex({ "session_id": 1 });
db.messages.createIndex({ "project_id": 1 });
db.messages.createIndex({ "project_id": 1, "timestamp": -1 });
db.messages.createIndex({ "timestamp": -1 });
db.messages.createIndex({ "role": 1 });
db.messages.createIndex({ "type": 1 });

// Compound indexes for common queries
db.messages.createIndex({ "project_id": 1, "session_id": 1, "message_index": 1 });
db.sessions.createIndex({ "project_id": 1, "created_at": -1 });

// Create text index for search functionality
db.messages.createIndex({ 
    "content": "text", 
    "title": "text" 
}, { 
    name: "messages_text_search",
    default_language: "english"
});

// Create sparse indexes for optional fields
db.messages.createIndex({ "timestamp": -1 }, { sparse: true });
db.sessions.createIndex({ "message_timestamp": -1 }, { sparse: true });
db.projects.createIndex({ "last_conversation_date": -1 }, { sparse: true });

print('Database initialization completed successfully with optimized indexes');