# Git Hooks - Secret Detection

This project includes Git hooks to prevent accidentally committing or pushing sensitive information.

## 🚀 Installation

Run the setup script to install the hooks:
```bash
./setup_hooks.sh
```

This will copy the hooks from `.githooks/` to `.git/hooks/` and make them executable.

## 🔒 Available Hooks

### 1. Pre-commit Hook
**When it runs**: Before each commit  
**What it does**: Scans staged files for secrets

The hook will block commits if it detects:
- API keys (OpenAI, Google, AWS, etc.)
- Passwords and credentials
- Private keys (SSH, RSA)
- Database connection strings
- JWT tokens
- Other sensitive patterns

### 2. Pre-push Hook
**When it runs**: Before pushing to remote repository  
**What it does**: Scans all commits that would be pushed for secrets

This provides a second layer of protection, checking the entire commit history that would be pushed.

## 📋 Example Output

### When secrets are detected:
```
🔍 Checking staged files for secrets...
Checking 3 file(s)...

⚠️  SECRETS DETECTED - Commit blocked!

Found 2 potential secret(s) in staged files:

File: config.py
  Line 15: API_KEY (api_key)
    Preview: sk-1234567890abcdef...
  Line 23: PASSWORD (database)
    Preview: MySecretPass123...

Please remove these secrets before committing!
```

### When no secrets are found:
```
🔍 Checking staged files for secrets...
Checking 5 file(s)...
✓ No secrets detected in staged files
```

## 🛠️ Configuration

### Files Automatically Skipped
- Binary files (images, PDFs, archives)
- `.env` files (they're meant to contain secrets)
- Files in `.gitignore`

### Bypassing Hooks (Not Recommended)

If you absolutely need to bypass the hooks:
```bash
# Bypass pre-commit hook
git commit --no-verify

# Bypass pre-push hook
git push --no-verify
```

⚠️ **Warning**: Only bypass hooks if you're certain the flagged content is safe (e.g., example keys in documentation).

## 🔧 Troubleshooting

### Hook not running
1. Ensure hooks are executable:
   ```bash
   ls -la .git/hooks/
   ```
2. Re-run the setup script:
   ```bash
   ./setup_hooks.sh
   ```

### False positives
If the hook is detecting non-sensitive content as secrets:
1. Check if the pattern matches common secret formats
2. Consider updating the pattern in `security_utils.py`
3. Use `--no-verify` as a last resort

### Performance issues
For large commits, the hook might take a few seconds. This is normal as it's scanning all changed content for security.

## 🤝 Contributing

When adding new secret patterns:
1. Update `security_utils.py` with the new pattern
2. Add test cases in `test_security.py`
3. Document the pattern in this file

## 📝 Manual Testing

Test the hooks manually:
```bash
# Test pre-commit hook
python .githooks/pre-commit

# Test pre-push hook  
python .githooks/pre-push
```