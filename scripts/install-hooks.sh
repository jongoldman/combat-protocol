#!/bin/bash
# Install git hooks for Combat Protocol

REPO_ROOT=$(git rev-parse --show-toplevel)

echo "Installing git hooks..."

# Copy pre-commit hook
cp "$REPO_ROOT/scripts/pre-commit.template" "$REPO_ROOT/.git/hooks/pre-commit"
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"

echo "✓ Pre-commit hook installed"
echo ""
echo "The hook will automatically bump V2 version on each commit."
echo "To bump V1 manually: ./scripts/bump-version.py v1 patch"
