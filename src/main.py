#!/usr/bin/env python3
"""
PulseAudio Control GUI (pactl-gui)
Main application entry point
"""

import tkinter as tk
import os
import sys

# Ensure we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our UI components
from ui.main_window import MainWindow

def main():
    """Main application entry point."""
    # Check if pactl is available
    if os.system("which pactl > /dev/null") != 0:
        print("Error: PulseAudio command-line utility (pactl) not found!")
        print("Please install PulseAudio utilities package:")
        print("  Debian/Ubuntu: sudo apt-get install pulseaudio-utils")
        print("  Fedora: sudo dnf install pulseaudio-utils")
        print("  openSUSE: sudo zypper install pulseaudio-utils")
        sys.exit(1)

    # Create the main window
    root = tk.Tk()
    app = MainWindow(root)
    
    # Start the main application loop
    root.mainloop()

if __name__ == "__main__":
    main() 