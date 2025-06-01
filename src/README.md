# PulseAudio Control GUI - Source Code

This directory contains the source code for the PulseAudio Control GUI application.

## Directory Structure

```
src/
├── __init__.py                 # Package initialization
├── main.py                     # Application entry point
├── config/                     # Configuration management
│   └── __init__.py
├── ui/                         # UI components
│   ├── __init__.py
│   └── main_window.py          # Main application window implementation
└── utils/                      # Utility functions
    ├── __init__.py
    └── pactl_runner.py         # PulseAudio command execution and parsing
```

## Main Components

### main.py
Entry point for the application. Initializes the Tkinter root window and main application window.

### ui/main_window.py
Implements the main application window and all UI components:
- Tab-based interface (Create, Manage, Output)
- Menu system
- Status bar
- Event handling

### utils/pactl_runner.py
Handles interaction with PulseAudio through `pactl` commands:
- Running PulseAudio commands
- Parsing output from commands
- Managing audio devices and modules

## Running the Application

From the project root directory:
```bash
python3 src/main.py
```

## Contributing

When adding new features:
1. Add utility functions to the appropriate modules
2. Update UI components in main_window.py
3. Document any changes or new features 