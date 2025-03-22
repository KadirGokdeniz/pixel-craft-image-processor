"""
Unit tests for the image filters module.

This module tests the functionality of each filter in the ImageFilters class.
"""

import unittest
import numpy as np
import cv2
from pathlib import Path
import os

# Import from the test package
from tests import PixelCraftTestCase, create_test_image, save_test_image
from src.core.filters import ImageFilters

class TestImageFilters(PixelCraftTestCase):
    """Test cases for the ImageFilters class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        super().setUp()
        
        # Create different test images for specific tests
        self.uniform_image = create_test_image(100, 100, 128)  # Uniform gray
        self.gradient_image = np.zeros((100, 100), dtype=np.uint8)
        for i in range(100):
            self.gradient_image[:, i] = i * 2.55  # 0-255 gradient
        
        self.edge_image = np.zeros((100, 100), dtype=np.uint8)
        self.edge_image[40:60, 40:60] = 255  # White square on black background
        
        # Create an image with noise
        self.noisy_image = create_test_image(100, 100, 128)
        noise = np.random.normal(0, 25, (100, 100))
        self.noisy_image = np.clip(self.noisy_image + noise, 0, 255).astype(np.uint8)
        
    def test_average_filter(self):
        """Test the average (blur) filter."""
        # Apply filter
        filtered = self.filters.average_filter(self.noisy_image.copy())
        
        # Save images for visual inspection
        save_test_image(self.noisy_image, "noisy_original.jpg")
        save_test_image(filtered, "noisy_averaged.jpg")
        
        # Test that the filter reduces variance (smooths the image)
        original_variance = np.var(self.noisy_image)
        filtered_variance = np.var(filtered)
        
        self.assertLess(
            filtered_variance, 
            original_variance, 
            "Average filter should reduce image variance"
        )
        
        # Test that the average filter preserves the general intensity level
        self.assertAlmostEqual(
            np.mean(filtered),
            np.mean(self.noisy_image),
            delta=5.0,
            msg="Average filter should preserve mean intensity"
        )
        
    def test_sharpen_filter(self):
        """Test the sharpen filter."""
        # Apply filter
        filtered = self.filters.sharpen_filter(self.edge_image.copy())
        
        # Save images for visual inspection
        save_test_image(self.edge_image, "edge_original.jpg")
        save_test_image(filtered, "edge_sharpened.jpg")
        
        # Test that sharpening increases the edge contrast
        # Check gradient magnitude at edge transitions
        edge_gradient_orig = cv2.Sobel(self.edge_image, cv2.CV_64F, 1, 1, ksize=3)
        edge_gradient_sharp = cv2.Sobel(filtered, cv2.CV_64F, 1, 1, ksize=3)
        
        self.assertGreater(
            np.max(np.abs(edge_gradient_sharp)),
            np.max(np.abs(edge_gradient_orig)),
            "Sharpening should increase edge contrast"
        )
        
    def test_negative_filter(self):
        """Test the negative filter."""
        # Apply filter
        filtered = self.filters.negative_filter(self.gradient_image.copy())
        
        # Save images for visual inspection
        save_test_image(self.gradient_image, "gradient_original.jpg")
        save_test_image(filtered, "gradient_negative.jpg")
        
        # Test that the negative filter inverts the image properly
        for i in range(0, 100, 10):  # Test every 10th pixel
            x, y = i, i
            original_value = self.gradient_image[y, x]
            negative_value = filtered[y, x]
            
            self.assertEqual(
                negative_value,
                255 - original_value,
                f"Negative filter should invert value at ({x},{y})"
            )
        
        # Test the sum of original and negative
        sum_image = self.gradient_image.astype(np.int32) + filtered.astype(np.int32)
        self.assertTrue(
            np.all(sum_image == 255),
            "Original + negative should equal 255 for all pixels"
        )
        
    def test_laplacian_filter(self):
        """Test the Laplacian filter."""
        # Apply filter
        filtered = self.filters.laplacian_filter(self.edge_image.copy())
        
        # Save images for visual inspection
        save_test_image(self.edge_image, "edge_original.jpg")
        save_test_image(filtered, "edge_laplacian.jpg")
        
        # Test that the Laplacian filter detects edges
        # The filter should produce high values at edge locations
        
        # Find edge pixels in the original image (where value changes)
        edge_mask = np.zeros_like(self.edge_image)
        edge_mask[39:41, 40:60] = 1  # Horizontal edges
        edge_mask[59:61, 40:60] = 1  # Horizontal edges
        edge_mask[40:60, 39:41] = 1  # Vertical edges
        edge_mask[40:60, 59:61] = 1  # Vertical edges
        
        # Calculate average filter response at edge and non-edge locations
        edge_response = np.mean(filtered[edge_mask == 1])
        non_edge_response = np.mean(filtered[edge_mask == 0])
        
        self.assertGreater(
            edge_response,
            non_edge_response,
            "Laplacian filter should respond stronger at edges"
        )
        
    def test_logarithm_filter(self):
        """Test the logarithm filter."""
        # Create a high dynamic range test image
        hdr_image = np.zeros((100, 100), dtype=np.uint8)
        for i in range(100):
            value = int(np.exp(i / 20.0) * 10) % 256
            hdr_image[:, i] = value
        
        # Apply filter
        filtered = self.filters.logarithm_filter(hdr_image.copy())
        
        # Save images for visual inspection
        save_test_image(hdr_image, "hdr_original.jpg")
        save_test_image(filtered, "hdr_logarithm.jpg")
        
        # Test that the output is binary (1 or 255) after threshold
        unique_values = np.unique(filtered)
        self.assertLessEqual(
            len(unique_values),
            2,
            f"Logarithm filter should produce binary output, got {len(unique_values)} values"
        )
        
    def test_filter_empty_image(self):
        """Test filters with an empty image."""
        empty_image = np.array([], dtype=np.uint8)
        
        # Test that filters handle empty images gracefully
        with self.assertRaises(Exception):
            self.filters.average_filter(empty_image)
            
    def test_filter_preserves_size(self):
        """Test that filters preserve image size."""
        original_shape = self.test_img.shape
        
        # Test all filters
        avg_filtered = self.filters.average_filter(self.test_img.copy())
        sharp_filtered = self.filters.sharpen_filter(self.test_img.copy())
        neg_filtered = self.filters.negative_filter(self.test_img.copy())
        lap_filtered = self.filters.laplacian_filter(self.test_img.copy())
        log_filtered = self.filters.logarithm_filter(self.test_img.copy())
        
        # Check shapes
        self.assertEqual(avg_filtered.shape, original_shape, "Average filter should preserve image size")
        self.assertEqual(sharp_filtered.shape, original_shape, "Sharpen filter should preserve image size")
        self.assertEqual(neg_filtered.shape, original_shape, "Negative filter should preserve image size")
        self.assertEqual(lap_filtered.shape, original_shape, "Laplacian filter should preserve image size")
        self.assertEqual(log_filtered.shape, original_shape, "Logarithm filter should preserve image size")
        
    def test_filter_multiple_applications(self):
        """Test applying filters multiple times."""
        # Apply sharpening filter multiple times
        img = self.edge_image.copy()
        for _ in range(3):
            img = self.filters.sharpen_filter(img)
            
        # Save images for visual inspection
        save_test_image(self.edge_image, "edge_original.jpg")
        save_test_image(img, "edge_multi_sharpen.jpg")
        
        # Test that multiple applications increase edge contrast even more
        edge_gradient_orig = cv2.Sobel(self.edge_image, cv2.CV_64F, 1, 1, ksize=3)
        edge_gradient_sharp = cv2.Sobel(img, cv2.CV_64F, 1, 1, ksize=3)
        
        self.assertGreater(
            np.max(np.abs(edge_gradient_sharp)),
            np.max(np.abs(edge_gradient_orig)) * 1.5,  # Expect significant increase
            "Multiple sharpen filters should significantly increase edge contrast"
        )

if __name__ == "__main__":
    unittest.main()