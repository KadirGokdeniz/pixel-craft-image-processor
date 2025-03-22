"""
PixelCraft Test Package.

This package contains unit and integration tests for the PixelCraft application.
It provides test helpers, fixtures, and utilities to facilitate testing.
"""

import os
import sys
import unittest
import numpy as np
import cv2
from pathlib import Path

# Add the parent directory to sys.path to allow importing the src package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the src package for testing
from src.core import ImageFilters, calculate_similarity
from src.utils.image_io import ImageIO

# Test resources paths
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_RESOURCES_DIR = os.path.join(TEST_DIR, "resources")
TEST_IMAGES_DIR = os.path.join(TEST_RESOURCES_DIR, "test_images")
TEST_OUTPUT_DIR = os.path.join(TEST_DIR, "output")

# Ensure test directories exist
os.makedirs(TEST_RESOURCES_DIR, exist_ok=True)
os.makedirs(TEST_IMAGES_DIR, exist_ok=True)
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

def create_test_image(width=100, height=100, color=128):
    """
    Create a test image for unit testing.
    
    Args:
        width (int): Image width
        height (int): Image height
        color (int): Grayscale color value (0-255)
        
    Returns:
        numpy.ndarray: Grayscale test image
    """
    return np.ones((height, width), dtype=np.uint8) * color

def save_test_image(image, filename):
    """
    Save a test image to the test output directory.
    
    Args:
        image (numpy.ndarray): Image to save
        filename (str): Filename for the test image
        
    Returns:
        str: Path to the saved image
    """
    path = os.path.join(TEST_OUTPUT_DIR, filename)
    cv2.imwrite(path, image)
    return path

def load_sample_image(index=1):
    """
    Load a sample image for testing.
    
    Args:
        index (int): Index of the sample image (1-5)
        
    Returns:
        numpy.ndarray: Sample image or None if not found
    """
    # Try to load from test resources
    path = os.path.join(TEST_IMAGES_DIR, f"{index}.jpg")
    if os.path.exists(path):
        return cv2.imread(path, 0)
    
    # If not found, try to load from the original location
    # This is a fallback for initial development before test images are set up
    original_path = os.path.join(os.path.expanduser("~"), "Desktop", "1", f"{index}.jpg")
    if os.path.exists(original_path):
        return cv2.imread(original_path, 0)
    
    return None

class PixelCraftTestCase(unittest.TestCase):
    """
    Base test case class for PixelCraft tests.
    
    Provides common setup, teardown, and utility methods for tests.
    """
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create test images directory if it doesn't exist
        os.makedirs(TEST_IMAGES_DIR, exist_ok=True)
        
        # Create a test image if none exists
        if not os.listdir(TEST_IMAGES_DIR):
            test_img = create_test_image(450, 450)
            cv2.imwrite(os.path.join(TEST_IMAGES_DIR, "1.jpg"), test_img)
        
        # Initialize test images
        self.test_img = load_sample_image(1)
        
        # Initialize filters
        self.filters = ImageFilters()
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean output directory
        for file in os.listdir(TEST_OUTPUT_DIR):
            if file.endswith(".jpg") or file.endswith(".png"):
                os.remove(os.path.join(TEST_OUTPUT_DIR, file))
    
    def assert_images_similar(self, img1, img2, threshold=0.9):
        """
        Assert that two images are similar.
        
        Args:
            img1 (numpy.ndarray): First image
            img2 (numpy.ndarray): Second image
            threshold (float): Similarity threshold (0-1)
            
        Raises:
            AssertionError: If images are not similar
        """
        # Ensure same size
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Calculate similarity
        similarity_pct = calculate_similarity(img1, img2, 16)
        similarity = similarity_pct / 100.0
        
        # Assert
        self.assertGreaterEqual(
            similarity, threshold, 
            f"Images similarity {similarity:.2f} is below threshold {threshold}"
        )

def run_tests():
    """Run all tests in the package."""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir)
    
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    run_tests()