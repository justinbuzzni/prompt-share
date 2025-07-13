#!/bin/bash
# Setup script to install Git hooks

echo "🔧 Setting up Git hooks..."

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-commit hook
if [ -f .githooks/pre-commit ]; then
    cp .githooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Pre-commit hook installed"
else
    echo "❌ Pre-commit hook not found in .githooks/"
    exit 1
fi

# Copy pre-push hook
if [ -f .githooks/pre-push ]; then
    cp .githooks/pre-push .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    echo "✅ Pre-push hook installed"
else
    echo "❌ Pre-push hook not found in .githooks/"
    exit 1
fi

# Configure Git to use the hooks directory (alternative method)
# git config core.hooksPath .githooks

echo ""
echo "✨ Git hooks setup complete!"
echo ""
echo "The following hooks are now active:"
echo "  - pre-commit: Checks staged files for secrets before committing"
echo "  - pre-push: Checks all commits for secrets before pushing"
echo ""
echo "To bypass hooks (not recommended), use:"
echo "  - git commit --no-verify"
echo "  - git push --no-verify"