#!/bin/bash
# Complete the Combat Protocol monorepo migration
# Run this after the initial migration script encountered an error

cd ~/src/Ventures/combat-protocol

echo "Completing monorepo migration..."
echo ""

# Step 5b: Move documentation (with error handling)
echo "Step 5: Moving documentation..."
if [ -f src/COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION.md ]; then
    mv src/COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION.md docs/
    echo "✓ Moved COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION.md"
fi

if [ -f COMBAT_PROTOCOL_GIT_HISTORY.md ]; then
    mv COMBAT_PROTOCOL_GIT_HISTORY.md docs/
    echo "✓ Moved COMBAT_PROTOCOL_GIT_HISTORY.md"
elif [ -f src/COMBAT_PROTOCOL_GIT_HISTORY.md ]; then
    mv src/COMBAT_PROTOCOL_GIT_HISTORY.md docs/
    echo "✓ Moved COMBAT_PROTOCOL_GIT_HISTORY.md from src/"
elif [ -f frontend/COMBAT_PROTOCOL_GIT_HISTORY.md ]; then
    mv frontend/COMBAT_PROTOCOL_GIT_HISTORY.md docs/
    echo "✓ Moved COMBAT_PROTOCOL_GIT_HISTORY.md from frontend/"
else
    echo "⚠ COMBAT_PROTOCOL_GIT_HISTORY.md not found (may already be moved or missing)"
fi
echo ""

# Step 6: Move scripts
echo "Step 6: Moving scripts..."
if [ -f src/git-pull.sh ]; then
    mv src/git-pull.sh scripts/
    echo "✓ Moved git-pull.sh"
fi
echo ""

# Step 7: Create unified .gitignore
echo "Step 7: Creating unified .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/

# Node
node_modules/
dist/
.cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment
.env
.env.local

# Backups
backup-*/
*.backup

# Build artifacts
build/
*.egg-info/

# Sensitive data
github-repo-access-token.txt
*.pem
*.key
EOF
echo "✓ .gitignore created"
echo ""

# Step 8: Create unified README
echo "Step 8: Creating README.md..."
cat > README.md << 'EOF'
# Combat Protocol

A physics-based Muay Thai fighting simulation with AI-generated fighters and real-time 3D visualization.

## Project Structure

```
combat-protocol/
├── backend/          # Flask API server and physics simulation
├── frontend/         # React + Three.js web interface
├── docs/             # Documentation and git history
├── legal/            # Legal documents
├── papers/           # Research papers
└── scripts/          # Utility scripts
```

## Quick Start

### Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend runs on `http://localhost:5001`

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173/v2/`

## Development

- **Local Development**: Both servers run independently
- **Production**: Frontend builds to static files served by Flask

## Documentation

See `docs/` for detailed system documentation and git history.

## Deployment

Production site: https://combatprotocol.com/v2/
EOF
echo "✓ README.md created"
echo ""

# Step 9: Initialize git repository
echo "Step 9: Initializing git repository..."
if [ ! -d .git ]; then
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi
echo ""

# Step 10: Create initial commit
echo "Step 10: Creating initial commit..."
git add .
git commit -m "Initial monorepo commit

Unified backend and frontend into single repository.
Previous git history preserved in docs/COMBAT_PROTOCOL_GIT_HISTORY.md

Structure:
- backend/ - Flask API and physics simulation
- frontend/ - React + Three.js interface
- docs/ - Documentation
- legal/ - Legal documents
- papers/ - Research papers
- scripts/ - Utility scripts"
echo "✓ Initial commit created"
echo ""

echo "=================================="
echo "Migration Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Test backend: cd backend && source venv/bin/activate && python app.py"
echo "2. Test frontend: cd frontend && npm install && npm run dev"
echo "3. If everything works, you can delete:"
echo "   - src/combat-protocol-backend/"
echo "   - src/combat-protocol-frontend/"
echo "4. Create GitHub repo and push:"
echo "   git remote add origin <your-repo-url>"
echo "   git branch -M main"
echo "   git push -u origin main"
