#!/bin/bash
# Migrate Combat Protocol to unified monorepo structure

set -e  # Exit on any error

echo "=================================="
echo "Combat Protocol Monorepo Migration"
echo "=================================="
echo ""

# Start from combat-protocol root
cd ~/src/Ventures/combat-protocol

# 1. Create backup of current state
echo "Step 1: Creating backup..."
BACKUP_DIR="backup-pre-monorepo-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/combat-protocol-backend "$BACKUP_DIR/"
cp -r src/combat-protocol-frontend "$BACKUP_DIR/"
echo "✓ Backup created at: $BACKUP_DIR"
echo ""

# 2. Create new directory structure
echo "Step 2: Creating new directory structure..."
mkdir -p backend
mkdir -p frontend
mkdir -p docs
mkdir -p scripts
echo "✓ Directories created"
echo ""

# 3. Move backend files (excluding .git)
echo "Step 3: Moving backend files..."
cd ~/src/Ventures/combat-protocol/src/combat-protocol-backend
rsync -av --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' --exclude='venv' --exclude='.DS_Store' . ../../backend/
echo "✓ Backend files moved"
echo ""

# 4. Move frontend files (excluding .git and node_modules)
echo "Step 4: Moving frontend files..."
cd ~/src/Ventures/combat-protocol/src/combat-protocol-frontend
rsync -av --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='.DS_Store' . ../../frontend/
echo "✓ Frontend files moved"
echo ""

# 5. Move documentation
echo "Step 5: Moving documentation..."
cd ~/src/Ventures/combat-protocol
mv src/COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION.md docs/
mv COMBAT_PROTOCOL_GIT_HISTORY.md docs/
echo "✓ Documentation moved"
echo ""

# 6. Move scripts
echo "Step 6: Moving scripts..."
if [ -f src/git-pull.sh ]; then
    mv src/git-pull.sh scripts/
fi
echo "✓ Scripts moved"
echo ""

# 7. Create unified .gitignore
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

# 8. Create unified README
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

# 9. Initialize git repository
echo "Step 9: Initializing git repository..."
git init
echo "✓ Git initialized"
echo ""

# 10. Create initial commit
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
echo "1. Review the new structure in ~/src/Ventures/combat-protocol"
echo "2. Test backend: cd backend && python app.py"
echo "3. Test frontend: cd frontend && npm run dev"
echo "4. If everything works, you can delete:"
echo "   - src/combat-protocol-backend/"
echo "   - src/combat-protocol-frontend/"
echo "   - src/ directory (if empty)"
echo "5. Create GitHub repo and push:"
echo "   git remote add origin <your-repo-url>"
echo "   git push -u origin main"
echo ""
echo "Backup location: $BACKUP_DIR"
