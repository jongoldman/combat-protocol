#!/usr/bin/env python3
"""
Bump version for V1 (Flask) or V2 (React) deployments.

Usage: 
  ./bump-version.py v1 patch      # Bump V1 patch version
  ./bump-version.py v2 minor      # Bump V2 minor version
  ./bump-version.py v2 major      # Bump V2 major version

Version Targets:
  v1 = Flask server-rendered version (https://combatprotocol.com/)
  v2 = React SPA version (https://combatprotocol.com/v2/)

Bump Types:
  patch = X.Y.Z -> X.Y.(Z+1)
  minor = X.Y.Z -> X.(Y+1).0
  major = X.Y.Z -> (X+1).0.0
"""
import sys
import re
from pathlib import Path
from datetime import datetime

def get_repo_root():
    """Find the git repo root."""
    current = Path(__file__).resolve().parent.parent
    return current

def read_version(version_file):
    """Read current version from VERSION file."""
    if not version_file.exists():
        return None
    return version_file.read_text().strip()

def parse_version(version_str):
    """Parse version string into major, minor, patch."""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    return tuple(map(int, match.groups()))

def bump_version(version_str, bump_type='patch'):
    """Bump version number based on bump type."""
    major, minor, patch = parse_version(version_str)
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Unknown bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"

def update_v1_files(repo_root, new_version):
    """Update V1 (Flask server-rendered) version files."""
    print("\n  Updating V1 files:")
    
    files_to_update = {
        repo_root / "VERSION_V1": "version_file",
        repo_root / "backend" / "app_v1.py": "python",
        repo_root / "backend" / "templates" / "index_v1.html": "html",
        repo_root / "backend" / "templates" / "index.html": "html",
    }
    
    for file_path, file_type in files_to_update.items():
        if not file_path.exists():
            print(f"    ⊗ {file_path.name} not found, skipping")
            continue
        
        content = file_path.read_text()
        updated = False
        
        if file_type == "version_file":
            content = new_version
            updated = True
        elif file_type == "python":
            # Update __version__ = "X.Y.Z" or VERSION = "X.Y.Z"
            new_content = re.sub(
                r'(__version__|VERSION)\s*=\s*["\'][\d.]+["\']',
                rf'\g<1> = "{new_version}"',
                content
            )
            if new_content != content:
                content = new_content
                updated = True
        elif file_type == "html":
            # Update version display in template (e.g., "v0.2.8" or "Version: 0.2.8")
            new_content = re.sub(
                r'(Version|v)[\s:]*[\d.]+',
                rf'\g<1> {new_version}',
                content,
                flags=re.IGNORECASE
            )
            if new_content != content:
                content = new_content
                updated = True
        
        if updated:
            file_path.write_text(content)
            print(f"    ✓ {file_path.relative_to(repo_root)}")
        else:
            print(f"    - {file_path.name} (no version pattern found)")

def update_v2_files(repo_root, new_version):
    """Update V2 (React SPA) version files."""
    print("\n  Updating V2 files:")
    
    files_to_update = {
        repo_root / "VERSION_V2": "version_file",
        repo_root / "frontend" / "package.json": "json",
        repo_root / "backend" / "app.py": "python",
        repo_root / "docs" / "COMBAT_PROTOCOL_SYSTEM_DOCUMENTATION.md": "markdown",
    }
    
    for file_path, file_type in files_to_update.items():
        if not file_path.exists():
            print(f"    ⊗ {file_path.name} not found, skipping")
            continue
        
        content = file_path.read_text()
        updated = False
        
        if file_type == "version_file":
            content = new_version
            updated = True
        elif file_type == "json":
            # Update "version": "X.Y.Z" in package.json
            new_content = re.sub(
                r'("version":\s*")[\d.]+(")',
                rf'\g<1>{new_version}\g<2>',
                content
            )
            if new_content != content:
                content = new_content
                updated = True
        elif file_type == "python":
            # Update __version__ = "X.Y.Z" or VERSION = "X.Y.Z"
            new_content = re.sub(
                r'(__version__|VERSION)\s*=\s*["\'][\d.]+["\']',
                rf'\g<1> = "{new_version}"',
                content
            )
            if new_content != content:
                content = new_content
                updated = True
        elif file_type == "markdown":
            # Update **Version:** X.Y.Z in markdown
            new_content = re.sub(
                r'(\*\*Version:\*\*\s+)[\d.]+',
                rf'\g<1>{new_version}',
                content
            )
            # Also update Last Updated date
            today = datetime.now().strftime("%B %d, %Y")
            new_content = re.sub(
                r'(\*\*Last Updated:\*\*\s+).*',
                rf'\g<1>{today}',
                new_content
            )
            if new_content != content:
                content = new_content
                updated = True
        
        if updated:
            file_path.write_text(content)
            print(f"    ✓ {file_path.relative_to(repo_root)}")
        else:
            print(f"    - {file_path.name} (no version pattern found)")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    version_target = sys.argv[1].lower()
    bump_type = sys.argv[2].lower() if len(sys.argv) > 2 else 'patch'
    
    if version_target not in ['v1', 'v2']:
        print(f"ERROR: Version target must be 'v1' or 'v2', got '{version_target}'")
        print("\nUsage: bump-version.py [v1|v2] [patch|minor|major]")
        sys.exit(1)
    
    if bump_type not in ['patch', 'minor', 'major']:
        print(f"ERROR: Bump type must be 'patch', 'minor', or 'major', got '{bump_type}'")
        sys.exit(1)
    
    repo_root = get_repo_root()
    version_file = repo_root / f"VERSION_{version_target.upper()}"
    
    if not version_file.exists():
        print(f"ERROR: {version_file.name} file not found at repo root")
        print(f"Expected location: {version_file}")
        print(f"\nPlease create this file with the current version (e.g., '0.2.8')")
        sys.exit(1)
    
    old_version = read_version(version_file)
    new_version = bump_version(old_version, bump_type)
    
    print(f"\n{'='*60}")
    print(f"Bumping {version_target.upper()} ({bump_type}): {old_version} → {new_version}")
    print(f"{'='*60}")
    
    if version_target == 'v1':
        update_v1_files(repo_root, new_version)
    else:
        update_v2_files(repo_root, new_version)
    
    print(f"\n{'='*60}")
    print(f"✓ {version_target.upper()} version bumped successfully!")
    print(f"{'='*60}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
