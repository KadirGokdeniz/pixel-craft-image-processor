import numpy as np
import cv2

class ImageFilters:
    """
    A collection of image processing filters.
    """
    
    @staticmethod
    def average_filter(image):
        """
        Apply average (blur) filter to an image.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Filtered image
        """
        kernel = np.ones((5, 5), np.float32) / 25
        return cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    
    @staticmethod
    def sharpen_filter(image):
        """
        Apply sharpening filter to an image.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Filtered image
        """
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    
    @staticmethod
    def negative_filter(image):
        """
        Apply negative filter to an image.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Filtered image
        """
        return 255 - image
    
    @staticmethod
    def laplacian_filter(image):
        """
        Apply Laplacian filter to an image.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Filtered image
        """
        kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        return cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    
    @staticmethod
    def logarithm_filter(image):
        """
        Apply logarithm filter to an image.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Filtered image
        """
        log_image = np.uint8(np.log1p(image))
        threshold = 1
        return cv2.threshold(log_image, threshold, 255, cv2.THRESH_BINARY)[1]