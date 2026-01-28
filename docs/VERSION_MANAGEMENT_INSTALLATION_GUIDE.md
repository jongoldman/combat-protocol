# Combat Protocol - Dual Version Management System

## Overview

This package contains a complete dual-version management system for Combat Protocol's V1 (Flask server-rendered) and V2 (React SPA) deployments.

## Files Included

1. **bump-version.py** - Python script for version bumping
2. **VERSION_V1** - V1 (Flask) version tracker (starts at 0.2.8)
3. **VERSION_V2** - V2 (React) version tracker (starts at 0.2.9)
4. **pre-commit** - Git hook for automatic V2 version bumping
5. **COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION_v2.md** - Updated system documentation

## Installation Instructions

### Step 1: Copy Version Files to Repo Root

```bash
# From your repo root (~/Downloads/personal/combat-protocol/combat-protocol)
cp /path/to/downloads/VERSION_V1 .
cp /path/to/downloads/VERSION_V2 .
```

### Step 2: Install the Bump Script

```bash
# Copy to scripts directory
cp /path/to/downloads/bump-version.py scripts/
chmod +x scripts/bump-version.py
```

### Step 3: Install Git Pre-Commit Hook

```bash
# Copy to git hooks directory
cp /path/to/downloads/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### Step 4: Update Documentation

```bash
# Replace the old documentation
cp /path/to/downloads/COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION_v2.md docs/COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION.md
```

### Step 5: Verify Installation

```bash
# Test the bump script manually
./scripts/bump-version.py v2 patch

# Check that it updated files correctly
cat VERSION_V2
cat frontend/package.json | grep version
```

## Usage

### Automatic V2 Version Bumping (Default)

Every commit automatically bumps V2 patch version via the pre-commit hook:

```bash
git add .
git commit -m "feat: new feature"  # V2 auto-bumps: 0.2.9 → 0.2.10
```

### Manual Version Bumping

**Bump V2 manually:**
```bash
./scripts/bump-version.py v2 patch   # 0.2.9 → 0.2.10
./scripts/bump-version.py v2 minor   # 0.2.9 → 0.3.0
./scripts/bump-version.py v2 major   # 0.2.9 → 1.0.0
```

**Bump V1 (rare):**
```bash
./scripts/bump-version.py v1 patch   # 0.2.8 → 0.2.9
./scripts/bump-version.py v1 minor   # 0.2.8 → 0.3.0
```

### What Gets Updated

**V1 Bump Updates:**
- `VERSION_V1`
- `backend/app_v1.py` (if it has `__version__` or `VERSION`)
- `backend/templates/index.html` and `index_v1.html` (version displays)

**V2 Bump Updates:**
- `VERSION_V2`
- `frontend/package.json`
- `backend/app.py` (if it has `__version__` or `VERSION`)
- `docs/COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION.md`

## Adding Version Display to Your Code

### Backend (Flask)

Add to `backend/app.py`:
```python
from pathlib import Path

# Read version from VERSION_V2 file
VERSION_FILE = Path(__file__).parent.parent / "VERSION_V2"
VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "0.0.0"

# Add version endpoint
@app.route('/api/version')
def get_version():
    return jsonify({"version": VERSION})
```

### Frontend (React)

The version is already in `package.json`. To display it:
```javascript
import packageJson from '../package.json';

function App() {
  return (
    <div>
      <p>Version: {packageJson.version}</p>
    </div>
  );
}
```

## Tinker's Setup

Since git hooks are local and not pushed to the remote, Tinker needs to:

1. Pull the latest changes (which will include VERSION files and the bump script)
2. Manually install the pre-commit hook:
   ```bash
   cp scripts/pre-commit.template .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

Or create a setup script both of you can run:
```bash
# scripts/install-hooks.sh
#!/bin/bash
cp scripts/pre-commit.template .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "✓ Git hooks installed"
```

## Troubleshooting

**Hook not running?**
```bash
# Check if hook is executable
ls -la .git/hooks/pre-commit

# Make it executable if needed
chmod +x .git/hooks/pre-commit
```

**Version not updating?**
```bash
# Check if VERSION files exist
ls -la VERSION_*

# Run bump manually to see errors
./scripts/bump-version.py v2 patch
```

**Python not found?**
```bash
# Check Python 3 is available
which python3

# Or modify the hook to use 'python' instead of 'python3'
```

## Notes

- The pre-commit hook only bumps **V2** by default (active development version)
- V1 bumps are manual only (legacy version, rarely updated)
- Version bumps happen before the commit, so the new version is included in the commit
- Both you and Tinker need to install the hook separately (hooks aren't version controlled)

---

**Questions?** Check the updated system documentation for more details on the dual-deployment architecture.
