#!/bin/bash
# Find all useful source files in Combat Protocol project
# Excludes common build/cache directories

find . -type f \( \
    -name "*.py" -o \
    -name "*.html" -o \
    -name "*.js" -o \
    -name "*.json" -o \
    -name "*.md" -o \
    -name "*.css" -o \
    -name "*.txt" \
\) \
    ! -path "*/node_modules/*" \
    ! -path "*/.venv/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.git/*" \
    ! -path "*/venv/*" \
    ! -path "*/.pytest_cache/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    | sort
