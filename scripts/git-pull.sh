#!/bin/bash

# git-pull.sh - Pull latest changes for Combat Protocol frontend and backend

echo "=========================================="
echo "Pulling Combat Protocol repositories..."
echo "=========================================="

# Save current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pull backend
echo ""
echo "📦 Updating backend..."
cd "$SCRIPT_DIR/combat-protocol-backend" || exit 1
git pull
BACKEND_STATUS=$?

# Pull frontend
echo ""
echo "🎨 Updating frontend..."
cd "$SCRIPT_DIR/combat-protocol-frontend" || exit 1
git pull
FRONTEND_STATUS=$?

# Return to original directory
cd "$SCRIPT_DIR"

# Report status
echo ""
echo "=========================================="
if [ $BACKEND_STATUS -eq 0 ] && [ $FRONTEND_STATUS -eq 0 ]; then
    echo "✅ All repositories updated successfully!"
else
    echo "⚠️  Some repositories failed to update"
    [ $BACKEND_STATUS -ne 0 ] && echo "   - Backend: FAILED"
    [ $FRONTEND_STATUS -ne 0 ] && echo "   - Frontend: FAILED"
fi
echo "=========================================="

