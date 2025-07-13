# Release Notes

## Version 2.0.0 (2025-07-13)

### 🎯 Major Features

#### 1. Repository Owner-based Synchronization
- **Git Config Integration**: Now accurately detects repository owners from `.git/config` files
- **Owner Filtering**: Sync all repositories belonging to a specific GitHub organization or user
- **Command**: `python claude_sync.py -o buzzni` syncs all repositories owned by buzzni
- **Accurate Detection**: No more false positives - only shows real GitHub owners

#### 2. Security Enhancements
- **Automatic Secret Redaction**: Detects and redacts sensitive information before storing in MongoDB
- **Supported Patterns**:
  - API Keys (OpenAI, Google, AWS, generic)
  - Passwords and database credentials
  - JWT tokens, OAuth tokens, bearer tokens
  - SSH and RSA private keys
  - Database connection strings
  - Credit card numbers
- **Security Report**: Shows statistics of redacted secrets after each sync
- **Opt-out Option**: Use `--no-redaction` flag to disable (use with caution)

#### 3. Web Viewer Improvements
- **Project Grouping**: View projects grouped by repository name
- **Toggle Views**: Switch between grouped and flat project views
- **Workspace Sorting**: Projects sorted by last conversation date
- **Empty Message Filtering**: Automatically hides empty user/assistant messages
- **Last Conversation Display**: Shows actual conversation dates instead of sync dates

#### 4. Backend Migration
- **FastAPI**: Migrated from Flask to FastAPI for better performance
- **Type Safety**: Added Pydantic models for request/response validation
- **Async Support**: Improved concurrent request handling
- **Port Change**: API now runs on port 15011 (avoiding macOS AirPlay conflicts)

### 🐛 Bug Fixes

- Fixed empty message content extraction from list-based formats
- Resolved Grid component compatibility issues with MUI v7
- Fixed date formatting errors for invalid timestamps
- Corrected MongoDB connection using environment variables
- Fixed repository owner detection from complex project paths

### 🔧 Technical Improvements

- **Better Path Parsing**: Improved extraction logic for repository information
- **MongoDB Optimizations**: Added proper indexes for better query performance
- **Error Handling**: Enhanced error messages and logging throughout
- **Code Organization**: Separated security utilities into dedicated module

### 📝 Documentation

- Complete README.md with comprehensive usage instructions
- Added SYNC_USAGE.md for detailed synchronization options
- Created security documentation for redaction features
- Added architecture diagrams and data flow explanations

### 💥 Breaking Changes

- API port changed from 5000 to 15011
- Flask endpoints migrated to FastAPI format
- Repository selection now based on Git config (not path guessing)

### 🚀 Migration Guide

1. **Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Update Frontend API URL**:
   - Frontend now expects API on port 15011
   - Update any custom configurations

3. **Re-sync with Owner Detection**:
   ```bash
   # List available owners
   python claude_sync.py --list
   
   # Sync by owner
   python claude_sync.py -o your-github-org
   ```

---

## Version 1.0.0 (2025-07-01)

### Initial Release

- Basic synchronization from Claude local storage to MongoDB
- Simple Flask API for data access
- React frontend with project and message views
- MongoDB storage with three collections (projects, sessions, messages)
- Basic project listing and message display

---

## Upcoming Features (Roadmap)

- [ ] Real-time synchronization with file system monitoring
- [ ] Advanced search with filters and regex support
- [ ] Export functionality (PDF, Markdown, JSON)
- [ ] Multi-user support with authentication
- [ ] Conversation analytics and insights
- [ ] API rate limiting and monitoring
- [ ] Docker containerization
- [ ] Automated backup scheduling