"""
Comparison View for PixelCraft.

This module provides a view for comparing original and processed images
side by side with analysis tools.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSplitter, QScrollArea, QSlider, QCheckBox,
                           QPushButton, QToolBar, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor

import numpy as np
import cv2

class ComparisonView(QWidget):
    """
    A widget for comparing original and processed images side by side.
    
    Features:
    - Synchronized scrolling
    - Split view slider
    - Pixel value inspection
    - Difference highlighting
    """
    
    # Signal emitted when a pixel is hovered
    pixelHovered = pyqtSignal(int, int, tuple)  # x, y, pixel values
    
    def __init__(self, parent=None):
        """
        Initialize the comparison view.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.initUI()
        
        # Initialize instance variables
        self.original_image = None
        self.processed_image = None
        self.show_difference = False
        self.split_position = 0.5  # Position of the split (0-1)
        
    def initUI(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Image view area
        view_layout = QHBoxLayout()
        
        # Original image view
        self.original_scroll = QScrollArea()
        self.original_scroll.setWidgetResizable(True)
        self.original_container = QWidget()
        self.original_layout = QVBoxLayout(self.original_container)
        self.original_label = QLabel("Original Image")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_view = QLabel()
        self.original_view.setAlignment(Qt.AlignCenter)
        self.original_view.setStyleSheet("border: 1px solid #CCCCCC;")
        self.original_layout.addWidget(self.original_label)
        self.original_layout.addWidget(self.original_view)
        self.original_scroll.setWidget(self.original_container)
        
        # Processed image view
        self.processed_scroll = QScrollArea()
        self.processed_scroll.setWidgetResizable(True)
        self.processed_container = QWidget()
        self.processed_layout = QVBoxLayout(self.processed_container)
        self.processed_label = QLabel("Processed Image")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_view = QLabel()
        self.processed_view.setAlignment(Qt.AlignCenter)
        self.processed_view.setStyleSheet("border: 1px solid #CCCCCC;")
        self.processed_layout.addWidget(self.processed_label)
        self.processed_layout.addWidget(self.processed_view)
        self.processed_scroll.setWidget(self.processed_container)
        
        # Connect scroll bars for synchronized scrolling
        self.original_scroll.horizontalScrollBar().valueChanged.connect(
            self.processed_scroll.horizontalScrollBar().setValue
        )
        self.original_scroll.verticalScrollBar().valueChanged.connect(
            self.processed_scroll.verticalScrollBar().setValue
        )
        self.processed_scroll.horizontalScrollBar().valueChanged.connect(
            self.original_scroll.horizontalScrollBar().setValue
        )
        self.processed_scroll.verticalScrollBar().valueChanged.connect(
            self.original_scroll.verticalScrollBar().setValue
        )
        
        # Add the views to the layout
        self.view_splitter = QSplitter(Qt.Horizontal)
        self.view_splitter.addWidget(self.original_scroll)
        self.view_splitter.addWidget(self.processed_scroll)
        self.view_splitter.setSizes([1, 1])  # Equal sizes
        view_layout.addWidget(self.view_splitter)
        
        # Add the view layout to the main layout
        main_layout.addLayout(view_layout)
        
        # Toolbar for comparison options
        toolbar = QToolBar()
        
        # Split view slider
        self.split_slider = QSlider(Qt.Horizontal)
        self.split_slider.setRange(0, 100)
        self.split_slider.setValue(50)  # Default to middle (50%)
        self.split_slider.setToolTip("Drag to adjust split view position")
        self.split_slider.valueChanged.connect(self.adjustSplitView)
        
        # Checkbox for difference mode
        self.diff_checkbox = QCheckBox("Show Differences")
        self.diff_checkbox.setToolTip("Highlight differences between original and processed images")
        self.diff_checkbox.stateChanged.connect(self.toggleDifferenceMode)
        
        # Add widgets to toolbar
        toolbar.addWidget(QLabel("Split:"))
        toolbar.addWidget(self.split_slider)
        toolbar.addWidget(self.diff_checkbox)
        
        # Add the toolbar to the main layout
        main_layout.addWidget(toolbar)
        
        # Status bar (shows pixel information)
        status_bar = QFrame()
        status_bar.setFrameShape(QFrame.StyledPanel)
        status_layout = QHBoxLayout(status_bar)
        self.pixel_info_label = QLabel("Hover over image to see pixel values")
        status_layout.addWidget(self.pixel_info_label)
        main_layout.addWidget(status_bar)
        
    def setOriginalImage(self, image_data):
        """
        Set the original image.
        
        Args:
            image_data (numpy.ndarray): Original image data
        """
        self.original_image = image_data
        self.updateViews()
        
    def setProcessedImage(self, image_data):
        """
        Set the processed image.
        
        Args:
            image_data (numpy.ndarray): Processed image data
        """
        self.processed_image = image_data
        self.updateViews()
        
    def updateViews(self):
        """Update the image views based on current settings."""
        if self.original_image is None or self.processed_image is None:
            return
            
        # Convert OpenCV images to QPixmap
        original_pixmap = self.convertToPixmap(self.original_image)
        processed_pixmap = self.convertToPixmap(self.processed_image)
        
        # Display the images
        self.original_view.setPixmap(original_pixmap)
        self.processed_view.setPixmap(processed_pixmap)
        
        # If difference mode is enabled, show difference image
        if self.show_difference:
            diff_image = self.generateDifferenceImage()
            diff_pixmap = self.convertToPixmap(diff_image)
            self.processed_view.setPixmap(diff_pixmap)
            self.processed_label.setText("Difference Image")
        else:
            self.processed_label.setText("Processed Image")
        
    def convertToPixmap(self, image_data):
        """
        Convert OpenCV image to QPixmap.
        
        Args:
            image_data (numpy.ndarray): Image data
            
        Returns:
            QPixmap: Image as QPixmap
        """
        height, width = image_data.shape
        bytes_per_line = width
        q_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        return QPixmap.fromImage(q_image)
        
    def generateDifferenceImage(self):
        """
        Generate an image showing the difference between original and processed.
        
        Returns:
            numpy.ndarray: Difference image
        """
        # Calculate absolute difference
        diff = cv2.absdiff(self.original_image, self.processed_image)
        
        # Normalize to enhance visibility
        diff_norm = diff.copy()
        if np.max(diff) > 0:
            diff_norm = (diff * 255.0 / np.max(diff)).astype(np.uint8)
            
        return diff_norm
        
    def adjustSplitView(self, value):
        """
        Adjust the split view position.
        
        Args:
            value (int): Slider value (0-100)
        """
        self.split_position = value / 100.0
        self.view_splitter.setSizes([int(1000 * self.split_position), 
                                     int(1000 * (1 - self.split_position))])
        
    def toggleDifferenceMode(self, state):
        """
        Toggle difference highlighting mode.
        
        Args:
            state (int): Checkbox state
        """
        self.show_difference = (state == Qt.Checked)
        self.updateViews()
        
    def getOriginalImage(self):
        """
        Get the original image data.
        
        Returns:
            numpy.ndarray: Original image data
        """
        return self.original_image
        
    def getProcessedImage(self):
        """
        Get the processed image data.
        
        Returns:
            numpy.ndarray: Processed image data
        """
        return self.processed_image