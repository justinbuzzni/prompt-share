# Claude Prompt Share

A comprehensive tool for synchronizing, managing, and viewing Claude AI conversation data. This project consists of two main components: a synchronization tool and a web-based viewer.

## 🌟 Features

### Synchronization Tool (`claude_sync.py`)
- **Automatic Backup**: Sync Claude conversations from local storage to MongoDB
- **Repository-based Filtering**: Sync by GitHub owner or individual repositories
- **Security**: Automatic redaction of sensitive information (API keys, passwords, tokens)
- **Git Integration**: Accurately detects repository ownership from Git configurations

### Web Viewer
- **Modern UI**: React-based frontend with Material-UI components
- **FastAPI Backend**: High-performance API server
- **Project Organization**: View projects grouped by repository name
- **Search Functionality**: Search through messages and projects
- **Real-time Updates**: See latest conversation timestamps

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB 4.4+
- Claude Desktop App (for local conversation data)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/prompt-share.git
cd prompt-share
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root:
```env
MONGODB_URL=localhost:27017
MONGODB_USER=your_username
MONGODB_PASSWORD=your_password
MONGODB_DATABASE=claude_prompts
```

### 3. Install Dependencies

**Python dependencies:**
```bash
pip install -r requirements.txt
```

**Frontend dependencies:**
```bash
cd claude-viewer-frontend
npm install
```

**Git hooks (recommended):**
```bash
./setup_hooks.sh
```

### 4. Run the Synchronization
```bash
# Sync all conversations
python claude_sync.py

# Sync by repository owner
python claude_sync.py -o buzzni

# Sync specific repositories
python claude_sync.py -r prompt-share hsmoa
```

### 5. Start the Web Viewer

**Backend API Server:**
```bash
python api_server.py
# API runs on http://localhost:15011
```

**Frontend Development Server:**
```bash
cd claude-viewer-frontend
npm start
# Frontend runs on http://localhost:3000
```

## 📖 Detailed Usage

### Synchronization Tool

#### Interactive Mode
```bash
python claude_sync.py
```
Choose between:
1. Select by repository owner
2. Select by repository name
3. Sync all

#### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--list`, `-l` | List available owners and repositories | `python claude_sync.py -l` |
| `--owners`, `-o` | Sync by repository owner | `python claude_sync.py -o buzzni anthropic` |
| `--repos`, `-r` | Sync specific repositories | `python claude_sync.py -r repo1 repo2` |
| `--all`, `-a` | Sync all without prompting | `python claude_sync.py -a` |
| `--no-redaction` | Disable security redaction | `python claude_sync.py --no-redaction` |

### Web Viewer Features

#### Project Views
- **Grouped View**: Projects grouped by repository name
- **Flat View**: All projects in a list
- **Workspace Badges**: Visual indicators for main/release/feature branches

#### Message Display
- Syntax highlighting for code blocks
- Markdown rendering
- Timestamp display with relative time
- Empty message filtering

## 🔒 Security Features

The synchronization tool automatically detects and redacts:
- API Keys (OpenAI, Google, AWS, etc.)
- Passwords and authentication tokens
- Private keys (SSH, RSA)
- Database connection strings
- JWT tokens
- Credit card numbers

Example:
```
Original: sk-1234567890abcdefghijklmnop
Redacted: [REDACTED_API_KEY]
```

## 🏗️ Architecture

### Data Flow
```
Claude Desktop App
    ↓
~/.claude/projects/ (Local Storage)
    ↓
claude_sync.py (Extraction & Security)
    ↓
MongoDB (Secure Storage)
    ↓
FastAPI Backend (api_server.py)
    ↓
React Frontend (Web Viewer)
```

### MongoDB Schema
- **projects**: Project metadata and session lists
- **sessions**: Individual conversation sessions
- **messages**: Complete message history with metadata

## 🔧 Configuration

### MongoDB Indexes
The tool automatically creates indexes for optimal performance:
- Projects: `id` (unique), `path`, `created_at`
- Sessions: `id` (unique), `project_id`, `created_at`
- Messages: `session_id`, `timestamp`, text search

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection URL | `localhost:27017` |
| `MONGODB_USER` | MongoDB username | - |
| `MONGODB_PASSWORD` | MongoDB password | - |
| `MONGODB_DATABASE` | Database name | `claude_prompts` |
| `PORT` | API server port | `15011` |

## 📝 Project Structure
```
prompt-share/
├── claude_sync.py          # Main synchronization script
├── api_server.py           # FastAPI backend server
├── models.py               # Pydantic data models
├── utils.py                # Utility functions
├── security_utils.py       # Security redaction logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── claude-viewer-frontend/ # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   └── services/      # API services
│   └── package.json       # Node dependencies
└── README.md              # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for the Claude AI community
- Uses Material-UI for the beautiful interface
- Powered by FastAPI for high-performance API serving