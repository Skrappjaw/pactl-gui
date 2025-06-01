#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Uninstalling PulseAudio Control GUI...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Define directories (user-specific)
APP_NAME="pactl-gui"
APP_DIR="$HOME/.local/share/$APP_NAME"
DESKTOP_DIR="$HOME/.local/share/applications"
BIN_DIR="$HOME/.local/bin"

# Check if installation exists
if [ ! -d "$APP_DIR" ] && [ ! -f "$BIN_DIR/pactl-gui" ] && [ ! -f "$DESKTOP_DIR/pactl-gui.desktop" ]; then
    echo -e "${YELLOW}PulseAudio Control GUI doesn't appear to be installed${NC}"
    echo "Nothing to uninstall."
    exit 0
fi

# Remove application directory
if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Removing application files from $APP_DIR...${NC}"
    rm -rf "$APP_DIR"
    echo -e "${GREEN}✓ Application files removed${NC}"
else
    echo -e "${YELLOW}Application directory not found, skipping...${NC}"
fi

# Remove symlink from bin directory
if [ -L "$BIN_DIR/pactl-gui" ] || [ -f "$BIN_DIR/pactl-gui" ]; then
    echo -e "${YELLOW}Removing symlink from $BIN_DIR...${NC}"
    rm -f "$BIN_DIR/pactl-gui"
    echo -e "${GREEN}✓ Command-line launcher removed${NC}"
else
    echo -e "${YELLOW}Command-line launcher not found, skipping...${NC}"
fi

# Remove desktop file
if [ -f "$DESKTOP_DIR/pactl-gui.desktop" ]; then
    echo -e "${YELLOW}Removing desktop file...${NC}"
    rm -f "$DESKTOP_DIR/pactl-gui.desktop"
    echo -e "${GREEN}✓ Desktop integration removed${NC}"
else
    echo -e "${YELLOW}Desktop file not found, skipping...${NC}"
fi

# Update desktop database
echo -e "${YELLOW}Updating desktop database...${NC}"
if command_exists update-desktop-database; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

# For KDE specifically
if command_exists kbuildsycoca5; then
    echo -e "${YELLOW}Refreshing KDE application cache...${NC}"
    kbuildsycoca5 --noincremental >/dev/null 2>&1 || true
elif command_exists kbuildsycoca6; then
    echo -e "${YELLOW}Refreshing KDE application cache...${NC}"
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo ""
echo -e "${GREEN}Uninstallation complete!${NC}"
echo -e "${BLUE}PulseAudio Control GUI has been removed from your user account.${NC}" 