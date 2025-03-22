#!/usr/bin/env python3
"""
Main entry point for PixelCraft application.

This module starts the PixelCraft application with a GUI interface.
"""

import sys
import argparse
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pixelcraft")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PixelCraft - Image Processing Application")
    
    parser.add_argument("--image", type=str, help="Path to the image to open on startup")
    parser.add_argument("--batch", action="store_true", help="Run in batch processing mode")
    parser.add_argument("--filter", type=str, choices=["average", "negative", "sharpen", "laplacian", "logarithm"],
                       help="Filter to apply in batch mode")
    parser.add_argument("--sensitivity", type=int, default=16, 
                       help="Sensitivity value for comparison (1-255)")
    parser.add_argument("--output", type=str, help="Output directory for batch processing")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    return parser.parse_args()

def setup_environment():
    """Set up the application environment."""
    # Ensure necessary directories exist
    resources_dir = Path(__file__).parent / "resources"
    images_dir = resources_dir / "images"
    output_dir = Path(__file__).parent / "output"
    
    resources_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Set up environment variables if needed
    return True

def start_gui(args):
    """Start the graphical user interface."""
    try:
        # Import PyQt dependencies only when needed
        from PyQt5.QtWidgets import QApplication
        from src.gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        # If an image was provided, open it
        if args.image:
            window.openImageFromPath(args.image)
        
        return app.exec_()
    except ImportError as e:
        logger.error(f"Could not start GUI: {e}")
        logger.error("Please ensure PyQt5 is installed: pip install PyQt5")
        return 1

def run_batch_mode(args):
    """Run the application in batch processing mode."""
    if not args.filter:
        logger.error("Batch mode requires a filter to be specified with --filter")
        return 1
    
    if not args.output:
        logger.error("Batch mode requires an output directory to be specified with --output")
        return 1
    
    # Import necessary modules
    from src.core.filters import ImageFilters
    from src.utils.image_io import ImageIO
    import os
    from pathlib import Path
    import glob
    
    # Setup
    filters = ImageFilters()
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    # Find all images in the input directory or use the specified image
    if os.path.isdir(args.image):
        image_paths = glob.glob(os.path.join(args.image, "*.jpg")) + \
                     glob.glob(os.path.join(args.image, "*.jpeg")) + \
                     glob.glob(os.path.join(args.image, "*.png"))
    else:
        image_paths = [args.image]
    
    # Process each image
    for img_path in image_paths:
        try:
            # Load image
            image = ImageIO.read_image(img_path)
            
            # Apply filter
            filter_name = args.filter.lower()
            if filter_name == "average":
                processed = filters.average_filter(image)
            elif filter_name == "sharpen":
                processed = filters.sharpen_filter(image)
            elif filter_name == "negative":
                processed = filters.negative_filter(image)
            elif filter_name == "laplacian":
                processed = filters.laplacian_filter(image)
            elif filter_name == "logarithm":
                processed = filters.logarithm_filter(image)
            else:
                logger.warning(f"Unknown filter: {filter_name}, skipping {img_path}")
                continue
            
            # Save processed image
            filename = Path(img_path).name
            output_path = output_dir / f"{filter_name}_{filename}"
            ImageIO.save_image(processed, str(output_path))
            
            logger.info(f"Processed {filename} with {filter_name} filter")
            
        except Exception as e:
            logger.error(f"Error processing {img_path}: {str(e)}")
    
    return 0

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
        
    logger.debug("Starting PixelCraft")
    
    # Set up environment
    if not setup_environment():
        logger.error("Failed to set up environment")
        return 1
    
    # Determine whether to run in GUI or batch mode
    if args.batch:
        return run_batch_mode(args)
    else:
        return start_gui(args)

if __name__ == "__main__":
    sys.exit(main())