#!/bin/bash
# Export Combat Protocol git history from both repos

OUTPUT_FILE="COMBAT_PROTOCOL_GIT_HISTORY.md"

echo "# Combat Protocol - Complete Git History" > "$OUTPUT_FILE"
echo "Generated: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "This document preserves the complete commit history from both the backend and frontend repositories before unifying them into a single monorepo." >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Export Backend History
echo "## Backend Repository History" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Repository: combat-protocol-backend" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

cd ~/src/Ventures/combat-protocol/src/combat-protocol-backend

# Get detailed log with full commit messages
git log --all --date=iso --pretty=format:"### Commit: %H%n**Author:** %an <%ae>%n**Date:** %ad%n**Message:** %s%n%n%b%n---%n" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Export Frontend History
echo "## Frontend Repository History" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Repository: combat-protocol-frontend" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

cd ~/src/Ventures/combat-protocol/src/combat-protocol-frontend

# Get detailed log with full commit messages
git log --all --date=iso --pretty=format:"### Commit: %H%n**Author:** %an <%ae>%n**Date:** %ad%n**Message:** %s%n%n%b%n---%n" >> "$OUTPUT_FILE"

# Summary statistics
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Repository Statistics" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

cd ~/src/Ventures/combat-protocol/src/combat-protocol-backend
BACKEND_COMMITS=$(git rev-list --all --count)
BACKEND_AUTHORS=$(git log --format='%an' | sort -u | wc -l)
echo "### Backend" >> "$OUTPUT_FILE"
echo "- Total commits: $BACKEND_COMMITS" >> "$OUTPUT_FILE"
echo "- Total authors: $BACKEND_AUTHORS" >> "$OUTPUT_FILE"
echo "- First commit: $(git log --reverse --format='%ad' --date=short | head -1)" >> "$OUTPUT_FILE"
echo "- Last commit: $(git log --format='%ad' --date=short | head -1)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

cd ~/src/Ventures/combat-protocol/src/combat-protocol-frontend
FRONTEND_COMMITS=$(git rev-list --all --count)
FRONTEND_AUTHORS=$(git log --format='%an' | sort -u | wc -l)
echo "### Frontend" >> "$OUTPUT_FILE"
echo "- Total commits: $FRONTEND_COMMITS" >> "$OUTPUT_FILE"
echo "- Total authors: $FRONTEND_AUTHORS" >> "$OUTPUT_FILE"
echo "- First commit: $(git log --reverse --format='%ad' --date=short | head -1)" >> "$OUTPUT_FILE"
echo "- Last commit: $(git log --format='%ad' --date=short | head -1)" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "**End of Git History Export**" >> "$OUTPUT_FILE"

# Move to parent directory
cd ~/src/Ventures/combat-protocol
mv ~/src/Ventures/combat-protocol/src/combat-protocol-backend/"$OUTPUT_FILE" .

echo "Git history exported to: ~/src/Ventures/combat-protocol/$OUTPUT_FILE"
