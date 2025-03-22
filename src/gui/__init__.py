"""
PixelCraft GUI module.

This module contains all the graphical user interface components for the PixelCraft
image processing application.
"""

# Import GUI components
# These will be defined in future implementations
from .main_window import MainWindow
from .filter_panel import FilterPanel
from .comparison_view import ComparisonView
from .batch_processor import BatchProcessorView

# Define what should be available when importing this package
__all__ = [
    'MainWindow',
    'FilterPanel',
    'ComparisonView',
    'BatchProcessorView',
    'initialize_gui'
]

def initialize_gui():
    """
    Initialize the GUI system.
    
    This function prepares any necessary GUI resources and returns
    the main application window.
    
    Returns:
        MainWindow: The main application window instance
    """
    return MainWindow()