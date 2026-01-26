#!/usr/bin/env python3
"""
Migration Script: Add model_3d to Existing Fighters

This script:
1. Scans all fighter JSON files in data/fighters/
2. For fighters missing model_3d field, uses GPT to select appropriate model
3. Updates the JSON files with the selected model
4. Creates backups before modifying

Usage:
    python migrate_add_models.py [--dry-run] [--backup-dir DIRECTORY]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import shutil

# Add parent directory to path so we can import fighter_generator
SCRIPT_DIR = Path(__file__).parent
PARENT_DIR = SCRIPT_DIR.parent  # Go up one level from utils/
sys.path.insert(0, str(PARENT_DIR))

from fighter_generator import FighterGenerator


def backup_fighter_file(filepath: Path, backup_dir: Path) -> Path:
    """Create a backup of a fighter JSON file"""
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{filepath.stem}_{timestamp}.json"
    backup_path = backup_dir / backup_filename
    shutil.copy2(filepath, backup_path)
    return backup_path


def load_fighter_json(filepath: Path) -> dict:
    """Load fighter JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_fighter_json(filepath: Path, data: dict) -> None:
    """Save fighter JSON file with proper formatting"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def select_model_for_fighter(generator: FighterGenerator, fighter_data: dict, fighter_name: str) -> str:
    """
    Select appropriate 3D model for a fighter based on their attributes.
    
    Returns the model filename (e.g., "Punching_blender.glb")
    """
    # Build a description from fighter attributes
    physical = fighter_data.get('physical', {})
    style = fighter_data.get('style', {})
    
    height = physical.get('height_cm', 175)
    weight = physical.get('weight_kg', 75)
    muscle_mass = physical.get('muscle_mass_percent', 70)
    
    # Build description for model selection
    description_parts = [f"Fighter named {fighter_name}"]
    
    # Body type description
    if weight > 95:
        description_parts.append("heavyweight")
    elif weight < 70:
        description_parts.append("lightweight")
    else:
        description_parts.append("middleweight")
    
    if muscle_mass > 80:
        description_parts.append("very muscular and powerful")
    elif muscle_mass < 70:
        description_parts.append("lean and agile")
    else:
        description_parts.append("balanced build")
    
    # Fighting style hints
    if style:
        leg_kick = style.get('leg_kick_tendency', 0)
        power_punch = style.get('power_punch_frequency', 0)
        
        if leg_kick > 60:
            description_parts.append("focuses on leg kicks")
        if power_punch > 60:
            description_parts.append("aggressive power puncher")
    
    description = ", ".join(description_parts)
    
    # Use the fighter generator's model selection logic
    try:
        selected_model = generator._select_3d_model(description, physical)
        return selected_model
    except Exception as e:
        print(f"  ⚠️  Error selecting model for {fighter_name}: {e}")
        print(f"      Using default: Punching_blender.glb")
        return "Punching_blender.glb"


def migrate_fighters(data_dir: Path, backup_dir: Path, dry_run: bool = False) -> dict:
    """
    Migrate all fighters in the data directory.
    
    Returns a summary dict with statistics.
    """
    fighters_dir = data_dir / "fighters"
    
    if not fighters_dir.exists():
        print(f"❌ Fighters directory not found: {fighters_dir}")
        return {"error": "Directory not found"}
    
    # Initialize generator
    print("🔧 Initializing FighterGenerator...")
    try:
        generator = FighterGenerator()
    except Exception as e:
        print(f"❌ Failed to initialize FighterGenerator: {e}")
        return {"error": str(e)}
    
    # Find all fighter JSON files
    fighter_files = list(fighters_dir.glob("*.json"))
    print(f"\n📂 Found {len(fighter_files)} fighter files\n")
    
    stats = {
        "total": len(fighter_files),
        "already_has_model": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0
    }
    
    for filepath in fighter_files:
        fighter_id = filepath.stem
        print(f"Processing: {fighter_id}")
        
        try:
            # Load fighter data
            fighter_data = load_fighter_json(filepath)
            fighter_name = fighter_data.get('name', fighter_id)
            
            # Check if already has model_3d
            if 'model_3d' in fighter_data and fighter_data['model_3d']:
                print(f"  ✓ Already has model_3d: {fighter_data['model_3d']}")
                stats["already_has_model"] += 1
                continue
            
            # Select model
            print(f"  🤖 Selecting model for {fighter_name}...")
            selected_model = select_model_for_fighter(generator, fighter_data, fighter_name)
            print(f"  ✓ Selected: {selected_model}")
            
            if dry_run:
                print(f"  [DRY RUN] Would update {fighter_id}.json with model_3d: {selected_model}")
                stats["updated"] += 1
            else:
                # Backup original file
                backup_path = backup_fighter_file(filepath, backup_dir)
                print(f"  💾 Backup created: {backup_path.name}")
                
                # Update fighter data
                fighter_data['model_3d'] = selected_model
                
                # Save updated file
                save_fighter_json(filepath, fighter_data)
                print(f"  ✅ Updated {fighter_id}.json")
                stats["updated"] += 1
            
        except Exception as e:
            print(f"  ❌ Error processing {fighter_id}: {e}")
            stats["errors"] += 1
        
        print()  # Blank line between fighters
    
    return stats


def print_summary(stats: dict, dry_run: bool) -> None:
    """Print migration summary"""
    print("=" * 60)
    if dry_run:
        print("DRY RUN SUMMARY")
    else:
        print("MIGRATION SUMMARY")
    print("=" * 60)
    
    if "error" in stats:
        print(f"❌ Migration failed: {stats['error']}")
        return
    
    print(f"Total fighters:              {stats['total']}")
    print(f"Already had model_3d:        {stats['already_has_model']}")
    print(f"Updated with model_3d:       {stats['updated']}")
    print(f"Errors:                      {stats['errors']}")
    print("=" * 60)
    
    if stats['updated'] > 0:
        if dry_run:
            print("\n✅ Dry run complete! Run without --dry-run to apply changes.")
        else:
            print("\n✅ Migration complete!")
            print(f"💾 Backups saved in: backups/")
            print("\n📝 Next steps:")
            print("   1. Restart your Flask server")
            print("   2. Go to /preview and test the updated fighters")
            print("   3. If anything goes wrong, restore from backups/")


def main():
    parser = argparse.ArgumentParser(
        description='Add model_3d fields to existing fighter JSON files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--backup-dir',
        type=str,
        default='backups',
        help='Directory for backup files (default: backups/)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Data directory containing fighters/ (default: data/)'
    )
    
    args = parser.parse_args()
    
    # Convert paths
    data_dir = Path(args.data_dir)
    backup_dir = Path(args.backup_dir)
    
    # Print header
    print("\n" + "=" * 60)
    print("COMBAT PROTOCOL - MODEL MIGRATION SCRIPT")
    print("=" * 60)
    print(f"Data directory:    {data_dir.absolute()}")
    print(f"Backup directory:  {backup_dir.absolute()}")
    print(f"Mode:              {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60 + "\n")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    else:
        print("⚠️  LIVE MODE - Files will be modified (backups will be created)\n")
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Migration cancelled")
            return
        print()
    
    # Run migration
    stats = migrate_fighters(data_dir, backup_dir, dry_run=args.dry_run)
    
    # Print summary
    print_summary(stats, args.dry_run)


if __name__ == '__main__':
    main()
