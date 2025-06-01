#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Installing PulseAudio Control GUI...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python tkinter module
check_tkinter() {
    python3 -c "import tkinter" >/dev/null 2>&1
}

# Dependency checks
echo -e "${YELLOW}Checking dependencies...${NC}"

# Check for Python3
if ! command_exists python3; then
    echo -e "${RED}Error: Python3 is not installed${NC}"
    echo "Please install Python3 and try again"
    exit 1
fi
echo -e "${GREEN}✓ Python3 found${NC}"

# Check for Tkinter
if ! check_tkinter; then
    echo -e "${RED}Error: Python3 Tkinter module is not available${NC}"
    echo "Please install python3-tkinter package:"
    echo "  Ubuntu/Debian: sudo apt install python3-tkinter"
    echo "  Fedora/RHEL:   sudo dnf install python3-tkinter"
    echo "  Arch Linux:    sudo pacman -S tk"
    exit 1
fi
echo -e "${GREEN}✓ Python3 Tkinter found${NC}"

# Check for pactl (PulseAudio)
if ! command_exists pactl; then
    echo -e "${RED}Error: pactl (PulseAudio) is not installed${NC}"
    echo "Please install PulseAudio and try again:"
    echo "  Ubuntu/Debian: sudo apt install pulseaudio pulseaudio-utils"
    echo "  Fedora/RHEL:   sudo dnf install pulseaudio pulseaudio-utils"
    echo "  Arch Linux:    sudo pacman -S pulseaudio"
    exit 1
fi
echo -e "${GREEN}✓ PulseAudio (pactl) found${NC}"

echo -e "${GREEN}All dependencies satisfied!${NC}"
echo ""

# Define directories (user-specific)
APP_NAME="pactl-gui"
APP_DIR="$HOME/.local/share/$APP_NAME"
DESKTOP_DIR="$HOME/.local/share/applications"
BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons/hicolor"

# Create directories if they don't exist
echo -e "${YELLOW}Creating installation directories...${NC}"
mkdir -p "$APP_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$ICON_DIR/48x48/apps"
mkdir -p "$ICON_DIR/64x64/apps"
mkdir -p "$ICON_DIR/128x128/apps"
mkdir -p "$ICON_DIR/scalable/apps"

# Copy application files
echo -e "${YELLOW}Copying application files to $APP_DIR...${NC}"
cp -r ./* "$APP_DIR/"

# Remove installation scripts from the installed location (they're not needed there)
rm -f "$APP_DIR/install.sh" "$APP_DIR/uninstall.sh" "$APP_DIR/commit-to-install.sh"

# Make the launcher script executable
chmod +x "$APP_DIR/pactl-gui.sh"

# Create symlink in bin directory
echo -e "${YELLOW}Creating symbolic link in $BIN_DIR...${NC}"
ln -sf "$APP_DIR/pactl-gui.sh" "$BIN_DIR/pactl-gui"

# Install desktop file with correct paths
echo -e "${YELLOW}Installing desktop file to $DESKTOP_DIR...${NC}"
cat > "$DESKTOP_DIR/pactl-gui.desktop" << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=PulseAudio GUI
GenericName=Audio Control
Comment=Manage PulseAudio modules and configurations
Exec=$BIN_DIR/pactl-gui
Icon=audio-card
Terminal=false
Categories=AudioVideo;Audio;Settings;
Keywords=sound;audio;volume;pulseaudio;pulse;mixer;
StartupNotify=true
X-KDE-SubstituteUID=false
X-KDE-StartupNotify=true
EOL

chmod +x "$DESKTOP_DIR/pactl-gui.desktop"

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

# Add ~/.local/bin to PATH if it's not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo -e "${YELLOW}Note: $HOME/.local/bin is not in your PATH${NC}"
    echo "To run 'pactl-gui' from anywhere, add this line to your ~/.bashrc or ~/.zshrc:"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo -e "${BLUE}You can now launch PulseAudio Control GUI:${NC}"
echo "• From your application menu (Audio → PulseAudio GUI)"
echo "• By typing 'pactl-gui' in a terminal"
echo "• By running '$BIN_DIR/pactl-gui'"
echo ""
echo -e "${YELLOW}Note: If the application doesn't appear in your menu immediately:${NC}"
echo "1. Log out and log back in to your desktop session"
echo "2. Or restart your desktop environment"
echo ""
echo -e "${BLUE}To uninstall, run: $APP_DIR/uninstall.sh${NC}" 