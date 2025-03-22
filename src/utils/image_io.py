import os
import cv2
import numpy as np

class ImageIO:
    """
    Utility class for image input/output operations.
    """
    
    @staticmethod
    def read_image(file_path, grayscale=True, resize=(450, 450)):
        """
        Read an image from a file path.
        
        Args:
            file_path (str): Path to the image file
            grayscale (bool, optional): Whether to read as grayscale. Defaults to True.
            resize (tuple, optional): Size to resize the image to. Defaults to (450, 450).
            
        Returns:
            numpy.ndarray: Image as numpy array
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
            
        # Read image in grayscale if specified
        img_flag = 0 if grayscale else 1
        image = cv2.imread(file_path, img_flag)
        
        # Resize if necessary
        if resize:
            image = cv2.resize(image, resize)
            
        return image
    
    @staticmethod
    def save_image(image, file_path):
        """
        Save an image to a file.
        
        Args:
            image (numpy.ndarray): Image to save
            file_path (str): Path to save the image to
        
        Returns:
            bool: True if successful, False otherwise
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        return cv2.imwrite(file_path, image)
    
    @staticmethod
    def display_image(image, window_name="Image"):
        """
        Display an image in a window.
        
        Args:
            image (numpy.ndarray): Image to display
            window_name (str, optional): Name of the window. Defaults to "Image".
        """
        cv2.imshow(window_name, image)
        # Wait for a key press
        cv2.waitKey(1)
    
    @staticmethod
    def close_window(window_name=None):
        """
        Close image display window(s).
        
        Args:
            window_name (str, optional): Name of window to close. If None, closes all windows.
        """
        if window_name:
            cv2.destroyWindow(window_name)
        else:
            cv2.destroyAllWindows()