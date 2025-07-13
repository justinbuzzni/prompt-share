# Claude Sync - Repository Selection & Security Features

The `claude_sync.py` script now supports:
1. Selecting by repository owner (organization/user) or individual repositories
2. Automatic redaction of sensitive information before storing in MongoDB

## Usage

### Interactive Mode (Default)
```bash
python claude_sync.py
```
When run without arguments, the script will:
1. Ask if you want to select by owner or repository name
2. Show available options
3. Let you select which ones to sync
4. Enter `0` to sync all

### Command Line Options

#### List Available Repositories and Owners
```bash
python claude_sync.py --list
# or
python claude_sync.py -l
```

#### Sync by Repository Owner
```bash
python claude_sync.py --owners buzzni anthropic
# or
python claude_sync.py -o buzzni
```

#### Sync Specific Repositories
```bash
python claude_sync.py --repos repo1 repo2 repo3
# or
python claude_sync.py -r repo1 repo2
```

#### Sync All (No Prompt)
```bash
python claude_sync.py --all
# or
python claude_sync.py -a
```

## Examples

1. **Sync all repositories owned by 'buzzni':**
   ```bash
   python claude_sync.py -o buzzni
   ```

2. **Sync repositories from multiple owners:**
   ```bash
   python claude_sync.py -o buzzni anthropic google
   ```

3. **Sync specific repositories:**
   ```bash
   python claude_sync.py -r prompt-share claudia
   ```

4. **See available owners and repositories:**
   ```bash
   python claude_sync.py -l
   ```

## Security Features

### Automatic Secret Redaction

By default, the script automatically detects and redacts sensitive information before storing messages in MongoDB. This includes:

- **API Keys**: OpenAI, Google, AWS, generic API keys
- **Passwords**: Database passwords, authentication credentials
- **Tokens**: JWT tokens, bearer tokens, OAuth tokens
- **Private Keys**: SSH keys, RSA private keys
- **AWS Credentials**: Access keys and secret keys
- **Database URLs**: MongoDB, MySQL, PostgreSQL connection strings

### Security Options

#### Disable Redaction (Use with Caution)
```bash
python claude_sync.py --no-redaction
```

### What Gets Redacted

The script replaces sensitive information with typed placeholders:
- `sk-abc123...` → `[REDACTED_API_KEY]`
- `password: secret123` → `password: [REDACTED_PASSWORD]`
- `mongodb://user:pass@host` → `mongodb://user:[REDACTED_MONGODB_PASSWORD]@host`

### Security Report

After syncing, you'll see a security report showing what was redacted:
```
Security Report - Redacted Secrets:
----------------------------------------
  API_KEY: 5
  PASSWORD: 3
  JWT_TOKEN: 2
  AWS_ACCESS_KEY: 1

Total secrets redacted: 11
```

## How Repository Detection Works

The script extracts repository owners and names from project paths:

### Owner Detection Patterns:
- `/workspace/owner/repo-name/...` → Owner: `owner`, Repo: `repo-name`
- `/Users/name/workspace/owner/repo-name/...` → Owner: `owner`, Repo: `repo-name`
- `/workspace/buzzni/mcp-hub/projects/...` → Owner: `buzzni`, Repo: `mcp-hub`

### Single Repository Patterns (No Owner):
- `/workspace/repo-name/...` → Owner: None, Repo: `repo-name`
- `/projects/repo-name/...` → Owner: None, Repo: `repo-name`

This helps organize and filter Claude conversations by repository owner (organization/user) or individual repository names.