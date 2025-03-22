"""
Main Window for PixelCraft.

This module provides the main application window for the PixelCraft
image processing application.
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QAction, QToolBar, QStatusBar, QFileDialog,
                            QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QDockWidget, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QImage
import cv2
import numpy as np

from .filter_panel import FilterPanel
from ..core.filters import ImageFilters
from ..core.similarity import calculate_similarity
from ..utils.image_io import ImageIO

class ImageView(QLabel):
    """Custom widget for displaying images with proper scaling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(450, 450)
        self.setStyleSheet("border: 1px solid #CCCCCC;")
        self.setScaledContents(True)
        self.image_data = None
        
    def setImage(self, image_data):
        """
        Set the image data and display it.
        
        Args:
            image_data (numpy.ndarray): Image data
        """
        self.image_data = image_data
        
        if image_data is None:
            self.clear()
            return
            
        # Convert cv2 image to QImage
        height, width = image_data.shape
        bytes_per_line = width
        q_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        
        # Set the pixmap
        self.setPixmap(QPixmap.fromImage(q_image))
        
    def getImageData(self):
        """Get the current image data."""
        return self.image_data


class MainWindow(QMainWindow):
    """Main window for the PixelCraft application."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.current_image_path = None
        self.original_image = None
        self.processed_image = None
        self.filters = ImageFilters()
        
        # Set up the user interface
        self.initUI()
        
    def initUI(self):
        """Set up the user interface."""
        # Set window properties
        self.setWindowTitle("PixelCraft - Image Processing Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.createMenuBar()
        
        # Create toolbar
        self.createToolBar()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Status bar için benzerlik etiketi
        self.status_similarity_label = QLabel("Similarity: N/A")
        self.statusBar.addPermanentWidget(self.status_similarity_label)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Image display area
        image_display = QSplitter(Qt.Horizontal)
        
        # Original image view
        self.original_view = ImageView()
        self.original_label = QLabel("Original Image")
        self.original_label.setAlignment(Qt.AlignCenter)
        
        original_container = QWidget()
        original_layout = QVBoxLayout()
        original_layout.addWidget(self.original_label)
        original_layout.addWidget(self.original_view)
        original_container.setLayout(original_layout)
        
        # Processed image view
        self.processed_view = ImageView()
        self.processed_label = QLabel("Processed Image")
        self.processed_label.setAlignment(Qt.AlignCenter)
        
        processed_container = QWidget()
        processed_layout = QVBoxLayout()
        processed_layout.addWidget(self.processed_label)
        processed_layout.addWidget(self.processed_view)
        processed_container.setLayout(processed_layout)
        
        # Add views to splitter
        image_display.addWidget(original_container)
        image_display.addWidget(processed_container)
        
        # Add splitter to main layout
        main_layout.addWidget(image_display)
        
        # Create filter panel as a dock widget
        filter_dock = QDockWidget("Filters", self)
        filter_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        self.filter_panel = FilterPanel()
        self.filter_panel.filterApplied.connect(self.applyFilter)
        
        # Benzerlik göstergesini ekleyin
        self.filter_panel.addSimilarityDisplay()
        
        # Benzerlik etiketine referans oluşturun
        self.similarity_label = self.filter_panel.similarity_label
        
        filter_dock.setWidget(self.filter_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, filter_dock)
        
    def createMenuBar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Image...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.openImage)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Processed Image...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.saveProcessedImage)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        reset_action = QAction("&Reset", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.resetImage)
        edit_menu.addAction(reset_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        batch_action = QAction("&Batch Processing...", self)
        batch_action.setShortcut("Ctrl+B")
        batch_action.triggered.connect(self.openBatchProcessor)
        tools_menu.addAction(batch_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.showAboutDialog)
        help_menu.addAction(about_action)
        
    def createToolBar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Open image action
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.openImage)
        toolbar.addAction(open_action)
        
        # Save image action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.saveProcessedImage)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Reset image action
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.resetImage)
        toolbar.addAction(reset_action)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoomIn)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoomOut)
        toolbar.addAction(zoom_out_action)
        
    def openImage(self):
        """Open an image file for processing."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;All Files (*)",
            options=options
        )
        
        if file_path:
            try:
                # Load the image
                self.current_image_path = file_path
                self.original_image = ImageIO.read_image(file_path)
                
                # Update the views
                self.original_view.setImage(self.original_image)
                self.processed_view.clear()
                self.processed_image = None
                
                # Update status
                file_name = os.path.basename(file_path)
                self.statusBar.showMessage(f"Opened {file_name}")
                self.similarity_label.setText("N/A %")
                self.status_similarity_label.setText("Similarity: N/A")
                
                # Update window title
                self.setWindowTitle(f"PixelCraft - {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open image: {str(e)}")
                
    def saveProcessedImage(self):
        """Save the processed image to a file."""
        if self.processed_image is None:
            QMessageBox.warning(self, "Warning", "No processed image to save.")
            return
            
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Processed Image", "", 
            "JPEG (*.jpg *.jpeg);;PNG (*.png);;BMP (*.bmp);;TIFF (*.tif *.tiff);;All Files (*)",
            options=options
        )
        
        if file_path:
            try:
                # Save the image
                success = ImageIO.save_image(self.processed_image, file_path)
                
                if success:
                    file_name = os.path.basename(file_path)
                    self.statusBar.showMessage(f"Saved processed image as {file_name}")
                else:
                    QMessageBox.warning(self, "Warning", "Failed to save the image.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save image: {str(e)}")
                
    def resetImage(self):
        """Reset the processed image to the original state."""
        if self.original_image is not None:
            self.processed_view.clear()
            self.processed_image = None
            self.similarity_label.setText("N/A %")
            self.status_similarity_label.setText("Similarity: N/A")
            self.statusBar.showMessage("Image reset")
            
    def applyFilter(self, filter_name, sensitivity):
        """
        Apply the selected filter to the original image.
        
        Args:
            filter_name (str): Name of the filter to apply
            sensitivity (int): Sensitivity value for comparison
        """
        if self.original_image is None:
            QMessageBox.warning(self, "Warning", "Please open an image first.")
            return
            
        try:
            # Apply the selected filter
            if filter_name == "Average":
                processed = self.filters.average_filter(self.original_image.copy())
            elif filter_name == "Sharpen":
                processed = self.filters.sharpen_filter(self.original_image.copy())
            elif filter_name == "Negative":
                processed = self.filters.negative_filter(self.original_image.copy())
            elif filter_name == "Laplacian":
                processed = self.filters.laplacian_filter(self.original_image.copy())
            elif filter_name == "Logarithm":
                processed = self.filters.logarithm_filter(self.original_image.copy())
            else:
                QMessageBox.warning(self, "Warning", f"Unknown filter: {filter_name}")
                return
                
            # Update the processed image view
            self.processed_image = processed
            self.processed_view.setImage(processed)
            self.processed_label.setText(f"{filter_name} Filter")
            
            # Calculate similarity
            similarity = calculate_similarity(processed, self.original_image, sensitivity)
            
            # Değere göre renkli geri bildirim
            color = "#4CAF50"  # Green for high similarity
            if similarity < 50:
                color = "#F44336"  # Red for low similarity
            elif similarity < 80:
                color = "#FF9800"  # Orange for medium similarity
                
            self.similarity_label.setText(f"{similarity}%")
            self.similarity_label.setStyleSheet(f"""
                font-size: 32px;
                font-weight: bold;
                color: {color};
                padding: 15px;
                margin: 10px;
                border: 2px solid #CCCCCC;
                border-radius: 10px;
                background-color: #F8F9FA;
            """)
            
            # Durum çubuğundaki etiketi de güncelleyin
            self.status_similarity_label.setText(f"Similarity: {similarity}%")
            
            # Update status
            self.statusBar.showMessage(f"Applied {filter_name} filter with sensitivity {sensitivity}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying filter: {str(e)}")
            
    def zoomIn(self):
        """Zoom in on the images."""
        # Placeholder for future zoom implementation
        self.statusBar.showMessage("Zoom in not implemented yet")
        
    def zoomOut(self):
        """Zoom out from the images."""
        # Placeholder for future zoom implementation
        self.statusBar.showMessage("Zoom out not implemented yet")
        
    def openBatchProcessor(self):
        """Open the batch processing dialog."""
        # Placeholder for future batch processing implementation
        self.statusBar.showMessage("Batch processing not implemented yet")
        
    def showAboutDialog(self):
        """Show the about dialog."""
        QMessageBox.about(self, "About PixelCraft",
            "PixelCraft - Advanced Image Processing Tool\n\n"
            "Version 1.0\n\n"
            "A professional image processing application with customizable filters, "
            "similarity analysis, and batch processing capabilities."
        )
    
    def openImageFromPath(self, image_path):
        """
        Open an image from a file path.
        
        Args:
            image_path (str): Path to the image file
        """
        if os.path.exists(image_path):
            try:
                # Load the image
                self.current_image_path = image_path
                self.original_image = ImageIO.read_image(image_path)
                
                # Update the views
                self.original_view.setImage(self.original_image)
                self.processed_view.clear()
                self.processed_image = None
                
                # Update status
                file_name = os.path.basename(image_path)
                self.statusBar.showMessage(f"Opened {file_name}")
                self.similarity_label.setText("N/A %")
                self.status_similarity_label.setText("Similarity: N/A")
                
                # Update window title
                self.setWindowTitle(f"PixelCraft - {file_name}")
                
                return True
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open image: {str(e)}")
                return False
        else:
            QMessageBox.warning(self, "Warning", f"Image file not found: {image_path}")
            return False