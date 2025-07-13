# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Prompt Synchronization Tool - a Python application that extracts Claude AI conversation data from local storage (`~/.claude/projects/`) and synchronizes it to MongoDB for backup and analysis.

## Key Commands

### Running the Application
```bash
# Main synchronization script
python claude_sync.py

# Test MongoDB connection
python test_connection.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Core Components

1. **models.py**: Pydantic data models
   - `Message`: Individual conversation messages with metadata
   - `Session`: Claude session containing multiple messages
   - `Project`: Claude project containing multiple sessions

2. **utils.py**: Utility functions
   - `get_claude_base_dir()`: Returns Claude's base directory path
   - `get_project_path()`: Decodes project paths from session directories
   - `parse_jsonl_file()`: Parses JSONL files containing messages

3. **claude_sync.py**: Main synchronization logic
   - `ClaudeSyncManager`: Handles all synchronization operations
   - Scans Claude's local storage directory
   - Extracts sessions and messages from JSONL files
   - Uses MongoDB upsert operations to prevent duplicates

### Data Flow

1. Scans `~/.claude/projects/` for project directories
2. For each project, finds all session directories
3. Extracts messages from `messages.jsonl` files
4. Extracts TODO data from `todo.json` files (if present)
5. Stores data in three MongoDB collections:
   - `projects`: Project metadata and session list
   - `sessions`: Session info with first message preview
   - `messages`: Complete message history

### MongoDB Schema

The application uses three collections with specific indexes:
- **projects**: Indexed on `id` (unique)
- **sessions**: Indexed on `id` (unique) and `project_id`
- **messages**: Indexed on `_id` (session_id_index format)

## Development Notes

### Environment Configuration
- Uses `.env` file for MongoDB connection details
- Required environment variables:
  - `MONGODB_URI`: MongoDB connection string
  - `MONGODB_DB_NAME`: Database name (default: claude_prompts)

### Error Handling
- Comprehensive logging throughout the application
- Graceful handling of missing files and directories
- Connection retry logic for MongoDB operations

### Code Style
- Uses type hints for all function parameters and returns
- Follows PEP 8 naming conventions
- Structured with clear separation of concerns