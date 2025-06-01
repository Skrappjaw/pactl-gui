"""
PulseAudio command execution and parsing utilities.
"""

import subprocess
import re
from typing import List, Dict, Any, Tuple, Optional


class PactlRunner:
    """
    A class to execute PulseAudio commands and parse their output.
    """

    @staticmethod
    def run_command(command: List[str], logger=None) -> Tuple[str, int]:
        """
        Run a pactl command and return its output.

        Args:
            command: A list of command components (e.g., ['list', 'sinks'])
            logger: Optional callback function to log command execution

        Returns:
            A tuple containing (output_string, return_code)
        """
        full_command = ['pactl'] + command
        command_str = ' '.join(full_command)
        
        # Log the command being executed
        if logger:
            logger(f"$ {command_str}")
        
        try:
            result = subprocess.run(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False
            )
            
            # Log the result
            if logger:
                if result.returncode == 0:
                    if result.stdout.strip():
                        # Only log output for commands that produce meaningful output
                        if any(cmd in command_str for cmd in ['list', 'info']):
                            logger(f"Command completed successfully (output truncated for readability)")
                        else:
                            logger(f"Command completed successfully")
                            if result.stdout.strip():
                                logger(f"Output: {result.stdout.strip()}")
                    else:
                        logger(f"Command completed successfully")
                else:
                    logger(f"Command failed (exit code {result.returncode})")
                    if result.stdout.strip():
                        logger(f"Error: {result.stdout.strip()}")
            
            return result.stdout, result.returncode
        except Exception as e:
            error_msg = str(e)
            if logger:
                logger(f"Command execution failed: {error_msg}")
            return error_msg, 1

    @staticmethod
    def list_sinks(logger=None) -> List[Dict[str, Any]]:
        """
        Get a comprehensive list of all audio sinks (outputs) with full specifications.

        Args:
            logger: Optional callback function to log command execution

        Returns:
            A list of dictionaries containing complete sink information
        """
        output, return_code = PactlRunner.run_command(['list', 'sinks'], logger)
        if return_code != 0:
            return []
        
        sinks = []
        current_sink = None
        current_section = None
        
        for line in output.splitlines():
            line_stripped = line.strip()
            
            if line.startswith('Sink #'):
                # Save previous sink and start new one
                if current_sink:
                    sinks.append(current_sink)
                sink_id = line.split('#')[1].strip()
                current_sink = {'id': sink_id, 'properties': {}}
                current_section = None
                
            elif current_sink:
                if line_stripped.startswith('Properties:'):
                    current_section = 'properties'
                elif line_stripped.startswith('Formats:'):
                    current_section = 'formats'
                    current_sink['formats'] = []
                elif current_section == 'properties' and '=' in line_stripped:
                    # Parse property line: key = "value"
                    parts = line_stripped.split(' = ', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"')
                        current_sink['properties'][key] = value
                elif current_section == 'formats' and line_stripped:
                    current_sink['formats'].append(line_stripped)
                elif ':' in line and current_section not in ['properties', 'formats']:
                    # Parse regular field: Key: Value
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Map to standardized field names
                    field_map = {
                        'State': 'state',
                        'Name': 'name', 
                        'Description': 'description',
                        'Driver': 'driver',
                        'Sample Specification': 'sample_spec',
                        'Channel Map': 'channel_map',
                        'Owner Module': 'owner_module',
                        'Mute': 'mute',
                        'Volume': 'volume',
                        'Base Volume': 'base_volume',
                        'Monitor Source': 'monitor_source',
                        'Latency': 'latency',
                        'Flags': 'flags'
                    }
                    
                    field_name = field_map.get(key, key.lower().replace(' ', '_'))
                    current_sink[field_name] = value
        
        if current_sink:
            sinks.append(current_sink)
            
        return sinks

    @staticmethod
    def list_sources(logger=None) -> List[Dict[str, Any]]:
        """
        Get a comprehensive list of all audio sources (inputs) with full specifications.

        Args:
            logger: Optional callback function to log command execution

        Returns:
            A list of dictionaries containing complete source information
        """
        output, return_code = PactlRunner.run_command(['list', 'sources'], logger)
        if return_code != 0:
            return []
        
        sources = []
        current_source = None
        current_section = None
        
        for line in output.splitlines():
            line_stripped = line.strip()
            
            if line.startswith('Source #'):
                # Save previous source and start new one
                if current_source:
                    sources.append(current_source)
                source_id = line.split('#')[1].strip()
                current_source = {'id': source_id, 'properties': {}}
                current_section = None
                
            elif current_source:
                if line_stripped.startswith('Properties:'):
                    current_section = 'properties'
                elif line_stripped.startswith('Formats:'):
                    current_section = 'formats'
                    current_source['formats'] = []
                elif current_section == 'properties' and '=' in line_stripped:
                    # Parse property line: key = "value"
                    parts = line_stripped.split(' = ', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"')
                        current_source['properties'][key] = value
                elif current_section == 'formats' and line_stripped:
                    current_source['formats'].append(line_stripped)
                elif ':' in line and current_section not in ['properties', 'formats']:
                    # Parse regular field: Key: Value
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Map to standardized field names
                    field_map = {
                        'State': 'state',
                        'Name': 'name',
                        'Description': 'description', 
                        'Driver': 'driver',
                        'Sample Specification': 'sample_spec',
                        'Channel Map': 'channel_map',
                        'Owner Module': 'owner_module',
                        'Mute': 'mute',
                        'Volume': 'volume',
                        'Base Volume': 'base_volume',
                        'Monitor of Sink': 'monitor_of_sink',
                        'Latency': 'latency',
                        'Flags': 'flags'
                    }
                    
                    field_name = field_map.get(key, key.lower().replace(' ', '_'))
                    current_source[field_name] = value
        
        if current_source:
            sources.append(current_source)
            
        return sources

    @staticmethod
    def list_modules(logger=None) -> List[Dict[str, Any]]:
        """
        Get a comprehensive list of all loaded PulseAudio modules with full specifications.

        Args:
            logger: Optional callback function to log command execution

        Returns:
            A list of dictionaries containing complete module information
        """
        output, return_code = PactlRunner.run_command(['list', 'modules'], logger)
        if return_code != 0:
            return []
        
        modules = []
        current_module = None
        current_section = None
        
        for line in output.splitlines():
            line_stripped = line.strip()
            
            if line.startswith('Module #'):
                # Save previous module and start new one
                if current_module:
                    modules.append(current_module)
                module_id = line.split('#')[1].strip()
                current_module = {'id': module_id, 'properties': {}}
                current_section = None
                
            elif current_module:
                if line_stripped.startswith('Properties:'):
                    current_section = 'properties'
                elif current_section == 'properties' and '=' in line_stripped:
                    # Parse property line: key = "value"
                    parts = line_stripped.split(' = ', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"')
                        current_module['properties'][key] = value
                elif line_stripped.startswith('Name: '):
                    current_module['name'] = line_stripped[6:].strip()
                elif line_stripped.startswith('Argument: '):
                    # Handle multi-line arguments
                    arg_content = line_stripped[10:].strip()
                    if arg_content.startswith('{'):
                        # Multi-line argument block
                        current_section = 'argument'
                        current_module['argument'] = arg_content
                    else:
                        # Single line argument
                        current_module['argument'] = arg_content
                elif current_section == 'argument':
                    # Continue collecting multi-line argument
                    if 'argument' not in current_module:
                        current_module['argument'] = ''
                    current_module['argument'] += '\n' + line
                    if line_stripped.endswith('}'):
                        current_section = None
                elif line_stripped.startswith('Usage counter: '):
                    current_module['usage_counter'] = line_stripped[15:].strip()
                    current_section = None  # Reset section after usage counter
        
        if current_module:
            modules.append(current_module)
            
        return modules

    @staticmethod
    def unload_module(module_id: str, logger=None) -> bool:
        """
        Unload a PulseAudio module by ID.

        Args:
            module_id: The numeric ID of the module to unload
            logger: Optional callback function to log command execution

        Returns:
            True if successful, False otherwise
        """
        output, return_code = PactlRunner.run_command(['unload-module', module_id], logger)
        return return_code == 0

    @staticmethod
    def create_duplex_sink(
        name: str, 
        description: str, 
        channels: int = 2,
        rate: Optional[int] = None,
        format: Optional[str] = None,
        channel_map: Optional[str] = None,
        sink_properties: Optional[str] = None,
        logger=None
    ) -> bool:
        """
        Create a duplex null sink with the given parameters.

        Args:
            name: The name for the sink (no spaces, used as identifier)
            description: Human-readable description (not used in the command directly)
            channels: Number of channels (1=mono, 2=stereo, etc.)
            rate: Sample rate in Hz (optional, defaults to system default)
            format: Sample format (optional, defaults to system default)
            channel_map: Channel mapping (optional, defaults to system default)
            sink_properties: Additional sink properties (optional)
            logger: Optional callback function to log command execution

        Returns:
            True if successful, False otherwise
        """
        # Build the command arguments
        cmd_args = [
            'load-module', 
            'module-null-sink', 
            'media.class=Audio/Duplex',
            f'sink_name={name}',
            f'channels={channels}'
        ]
        
        # Add advanced options if specified
        if rate is not None:
            cmd_args.append(f'rate={rate}')
        
        if format is not None:
            cmd_args.append(f'format={format}')
        
        if channel_map is not None:
            cmd_args.append(f'channel_map={channel_map}')
        
        if sink_properties is not None:
            cmd_args.append(f'sink_properties={sink_properties}')
        
        output, return_code = PactlRunner.run_command(cmd_args, logger)
        
        return return_code == 0

    @staticmethod
    def unload_all_null_sinks(logger=None) -> Tuple[int, List[str]]:
        """
        Unload all null sink modules.
        
        Args:
            logger: Optional callback function to log command execution
        
        Returns:
            A tuple containing (number_of_modules_unloaded, list_of_errors)
        """
        modules = PactlRunner.list_modules(logger)
        null_sink_modules = [m for m in modules if m.get('name') == 'module-null-sink']
        
        successful = 0
        errors = []
        
        for module in null_sink_modules:
            module_id = module.get('id', '')
            if module_id:
                success = PactlRunner.unload_module(module_id, logger)
                if success:
                    successful += 1
                else:
                    errors.append(f"Failed to unload module #{module_id}")
        
        return successful, errors 