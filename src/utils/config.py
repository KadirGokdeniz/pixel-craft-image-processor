"""
Configuration module for PixelCraft.

This module handles application settings, paths, and preferences.
It provides functionality to load and save configurations.
"""

import os
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pixelcraft.config")

class Config:
    """Application configuration manager."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        "paths": {
            "resources": "resources",
            "images": "resources/images",
            "output": "output",
            "temp": "temp"
        },
        "filters": {
            "default_filter": "Average",
            "default_sensitivity": 16,
            "average": {
                "kernel_size": 5
            },
            "sharpen": {
                "strength": 5
            },
            "laplacian": {
                "scale": 1.0
            },
            "logarithm": {
                "threshold": 1
            }
        },
        "ui": {
            "theme": "system",
            "language": "en",
            "window_size": [1200, 800],
            "show_toolbar": True,
            "show_statusbar": True
        },
        "processing": {
            "default_resize": [450, 450],
            "preserve_exif": True,
            "auto_enhance": False
        }
    }
    
    def __init__(self, config_path=None):
        """
        Initialize configuration.
        
        Args:
            config_path (str, optional): Path to configuration file.
                If None, default path is used.
        """
        self.home_dir = str(Path.home())
        
        # Determine config directory
        if os.name == 'nt':  # Windows
            self.config_dir = os.path.join(self.home_dir, 'AppData', 'Local', 'PixelCraft')
        else:  # macOS and Linux
            self.config_dir = os.path.join(self.home_dir, '.pixelcraft')
            
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Set config file path
        self.config_path = config_path or os.path.join(self.config_dir, 'config.json')
        
        # Load or create configuration
        self.config = self.load_config()
        
    def load_config(self):
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with default config to ensure all keys exist
                config = self.DEFAULT_CONFIG.copy()
                self._deep_update(config, loaded_config)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
            else:
                # Create default config
                logger.info("No configuration file found, using defaults")
                return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """
        Save current configuration to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get(self, key_path, default=None):
        """
        Get a configuration value by key path.
        
        Args:
            key_path (str): Dot-separated path to the configuration value (e.g., "paths.images")
            default: Value to return if the key path doesn't exist
            
        Returns:
            Value at the specified key path, or default if not found
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """
        Set a configuration value by key path.
        
        Args:
            key_path (str): Dot-separated path to the configuration value (e.g., "paths.images")
            value: Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        keys = key_path.split('.')
        config = self.config
        
        try:
            # Navigate to the parent of the final key
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
                
            # Set the value
            config[keys[-1]] = value
            return True
        except Exception as e:
            logger.error(f"Error setting config value: {str(e)}")
            return False
    
    def get_path(self, path_name):
        """
        Get an absolute path from a configured path.
        
        Args:
            path_name (str): Name of the path in the configuration
            
        Returns:
            str: Absolute path
        """
        rel_path = self.get(f"paths.{path_name}")
        
        if not rel_path:
            return None
            
        # If it's already an absolute path, return it
        if os.path.isabs(rel_path):
            return rel_path
            
        # Make it absolute relative to the application directory
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        abs_path = os.path.join(app_dir, rel_path)
        
        # Ensure path exists
        os.makedirs(abs_path, exist_ok=True)
        
        return abs_path
    
    def reset(self):
        """
        Reset configuration to defaults.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save_config()
    
    def _deep_update(self, target, source):
        """Recursively update a dictionary."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value


# Create a singleton instance
_config_instance = None

def get_config():
    """
    Get the global configuration instance.
    
    Returns:
        Config: The global configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance