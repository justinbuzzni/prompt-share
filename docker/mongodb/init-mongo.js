// MongoDB initialization script
db = db.getSiblingDB('prompt_share');

// Create collections
db.createCollection('projects');
db.createCollection('sessions');
db.createCollection('messages');

// Create indexes for better performance
db.projects.createIndex({ "id": 1 }, { unique: true });
db.sessions.createIndex({ "id": 1 }, { unique: true });
db.sessions.createIndex({ "project_id": 1 });
db.messages.createIndex({ "_id": 1 }, { unique: true });
db.messages.createIndex({ "session_id": 1 });
db.messages.createIndex({ "created_at": -1 });

// Create text index for search functionality
db.messages.createIndex({ 
    "content": "text", 
    "title": "text" 
}, { 
    name: "messages_text_index",
    default_language: "english"
});

print('Database initialization completed successfully');