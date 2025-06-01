#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define directories
APP_NAME="pactl-gui"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
CURRENT_DIR="$(pwd)"

# Commit message (from argument or default)
COMMIT_MESSAGE="${1:-Update application files}"

echo -e "${BLUE}Syncing development files to installed location...${NC}"

# Check if target directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}Error: Installation directory not found: $INSTALL_DIR${NC}"
    echo "Please run install.sh first to install the application"
    exit 1
fi

echo -e "${YELLOW}Copying files from $CURRENT_DIR to $INSTALL_DIR...${NC}"

# Use rsync to copy files efficiently, excluding development-only files
rsync -av --delete \
    --exclude='.git/' \
    --exclude='*.pyc' \
    --exclude='__pycache__/' \
    --exclude='commit-to-install.sh' \
    --exclude='install.sh' \
    --exclude='uninstall.sh' \
    --exclude='icons/' \
    --exclude='docs/' \
    --exclude='tests/' \
    "$CURRENT_DIR/" "$INSTALL_DIR/"

echo -e "${GREEN}✓ Files synchronized${NC}"

# Move to the install directory
cd "$INSTALL_DIR"

# Check if this is a git repository
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing Git repository in $INSTALL_DIR...${NC}"
    git init >/dev/null 2>&1
    git add . >/dev/null 2>&1
    git commit -m "Initial commit" >/dev/null 2>&1
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${YELLOW}Committing changes to Git repository...${NC}"
    git add . >/dev/null 2>&1
    if git commit -m "$COMMIT_MESSAGE" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Changes committed: $COMMIT_MESSAGE${NC}"
    else
        echo -e "${YELLOW}No changes to commit${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Sync complete!${NC}"
echo -e "${BLUE}Development files have been synchronized to the installed location${NC}"

# Return to original directory
cd "$CURRENT_DIR" 