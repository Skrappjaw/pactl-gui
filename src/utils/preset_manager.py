"""
Preset Manager for pactl-gui application.
Handles saving, loading, and managing custom audio presets.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any


class PresetManager:
    """Manages custom audio presets for the pactl-gui application."""
    
    def __init__(self, presets_dir: str = "presets"):
        """
        Initialize the preset manager.
        
        Args:
            presets_dir: Directory to store preset files
        """
        self.presets_dir = presets_dir
        self.presets_file = os.path.join(presets_dir, "user_presets.json")
        self._ensure_presets_dir()
        
        # Built-in presets that cannot be deleted
        self.builtin_presets = {
            "Stereo": {
                "channels": "2",
                "channel_map": "front-left,front-right",
                "description": "Stereo Virtual Device",
                "builtin": True
            },
            "Mono": {
                "channels": "1",
                "channel_map": "mono", 
                "description": "Mono Virtual Device",
                "builtin": True
            },
            "5.1 Surround": {
                "channels": "6",
                "channel_map": "front-left,front-right,front-center,lfe,rear-left,rear-right",
                "description": "5.1 Surround Virtual Device",
                "builtin": True
            },
            "7.1 Surround": {
                "channels": "8",
                "channel_map": "front-left,front-right,front-center,lfe,rear-left,rear-right,side-left,side-right",
                "description": "7.1 Surround Virtual Device",
                "builtin": True
            },
            "Custom": {
                "channels": "2",
                "channel_map": "",
                "description": "Custom Virtual Device",
                "builtin": True
            }
        }
    
    def _ensure_presets_dir(self):
        """Ensure the presets directory exists."""
        os.makedirs(self.presets_dir, exist_ok=True)
    
    def _load_user_presets(self) -> Dict[str, Any]:
        """Load user presets from file."""
        if not os.path.exists(self.presets_file):
            return {}
        
        try:
            with open(self.presets_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading presets: {e}")
            return {}
    
    def _save_user_presets(self, presets: Dict[str, Any]) -> bool:
        """Save user presets to file."""
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(presets, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving presets: {e}")
            return False
    
    def get_all_presets(self) -> Dict[str, Any]:
        """Get all presets (builtin + user)."""
        user_presets = self._load_user_presets()
        all_presets = self.builtin_presets.copy()
        all_presets.update(user_presets)
        return all_presets
    
    def get_preset_names(self) -> List[str]:
        """Get list of all preset names."""
        return list(self.get_all_presets().keys())
    
    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific preset by name."""
        all_presets = self.get_all_presets()
        return all_presets.get(name)
    
    def save_preset(self, name: str, preset_data: Dict[str, Any]) -> bool:
        """
        Save a custom preset.
        
        Args:
            name: Preset name
            preset_data: Preset configuration data
            
        Returns:
            True if saved successfully, False otherwise
        """
        if name in self.builtin_presets:
            print(f"Cannot overwrite builtin preset: {name}")
            return False
        
        # Add metadata
        preset_data = preset_data.copy()
        preset_data["created"] = datetime.now().isoformat()
        preset_data["builtin"] = False
        
        # Load existing user presets
        user_presets = self._load_user_presets()
        user_presets[name] = preset_data
        
        return self._save_user_presets(user_presets)
    
    def delete_preset(self, name: str) -> bool:
        """
        Delete a custom preset.
        
        Args:
            name: Preset name to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if name in self.builtin_presets:
            print(f"Cannot delete builtin preset: {name}")
            return False
        
        user_presets = self._load_user_presets()
        if name not in user_presets:
            print(f"Preset not found: {name}")
            return False
        
        del user_presets[name]
        return self._save_user_presets(user_presets)
    
    def is_builtin_preset(self, name: str) -> bool:
        """Check if a preset is builtin (cannot be deleted)."""
        return name in self.builtin_presets
    
    def export_preset(self, name: str, filepath: str) -> bool:
        """Export a preset to a file."""
        preset = self.get_preset(name)
        if not preset:
            return False
        
        try:
            with open(filepath, 'w') as f:
                json.dump({name: preset}, f, indent=2)
            return True
        except IOError as e:
            print(f"Error exporting preset: {e}")
            return False
    
    def import_preset(self, filepath: str) -> Optional[str]:
        """
        Import a preset from a file.
        
        Returns:
            Preset name if imported successfully, None otherwise
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or len(data) != 1:
                print("Invalid preset file format")
                return None
            
            name, preset_data = next(iter(data.items()))
            
            if self.save_preset(name, preset_data):
                return name
            else:
                return None
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error importing preset: {e}")
            return None 