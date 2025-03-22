"""
Batch Processor for PixelCraft.

This module provides a dialog for batch processing multiple images
with the same filter and settings.
"""

import os
import glob
from PyQt5.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QComboBox, QLineEdit,
                           QFileDialog, QListWidget, QProgressBar,
                           QGroupBox, QCheckBox, QSpinBox, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon

from ..core.filters import ImageFilters
from ..utils.image_io import ImageIO

class BatchProcessorWorker(QThread):
    """
    Worker thread for batch processing images.
    
    This thread handles the actual processing to keep the UI responsive.
    """
    
    # Signals for communication with the main thread
    progressChanged = pyqtSignal(int)  # Current progress (0-100)
    imageProcessed = pyqtSignal(str)   # Path of processed image
    processingFinished = pyqtSignal()  # Emitted when all processing is complete
    processingError = pyqtSignal(str, str)  # Error message and associated file
    
    def __init__(self, image_paths, filter_name, sensitivity, output_dir, parent=None):
        """
        Initialize the worker.
        
        Args:
            image_paths (list): List of paths to images
            filter_name (str): Name of the filter to apply
            sensitivity (int): Sensitivity value
            output_dir (str): Output directory for processed images
            parent (QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(parent)
        self.image_paths = image_paths
        self.filter_name = filter_name
        self.sensitivity = sensitivity
        self.output_dir = output_dir
        self.is_canceled = False
        
    def cancel(self):
        """Cancel the processing."""
        self.is_canceled = True
        
    def run(self):
        """Run the batch processing."""
        # Initialize filters
        filters = ImageFilters()
        
        # Process each image
        total_images = len(self.image_paths)
        
        for i, image_path in enumerate(self.image_paths):
            # Check if canceled
            if self.is_canceled:
                break
                
            try:
                # Update progress
                progress = int((i / total_images) * 100)
                self.progressChanged.emit(progress)
                
                # Load the image
                image = ImageIO.read_image(image_path)
                
                # Apply the selected filter
                if self.filter_name.lower() == "average":
                    processed = filters.average_filter(image.copy())
                elif self.filter_name.lower() == "sharpen":
                    processed = filters.sharpen_filter(image.copy())
                elif self.filter_name.lower() == "negative":
                    processed = filters.negative_filter(image.copy())
                elif self.filter_name.lower() == "laplacian":
                    processed = filters.laplacian_filter(image.copy())
                elif self.filter_name.lower() == "logarithm":
                    processed = filters.logarithm_filter(image.copy())
                else:
                    self.processingError.emit(f"Unknown filter: {self.filter_name}", image_path)
                    continue
                
                # Generate output path
                filename = os.path.basename(image_path)
                base_name, ext = os.path.splitext(filename)
                output_path = os.path.join(self.output_dir, f"{base_name}_{self.filter_name}{ext}")
                
                # Save the processed image
                success = ImageIO.save_image(processed, output_path)
                
                if success:
                    self.imageProcessed.emit(output_path)
                else:
                    self.processingError.emit("Failed to save processed image", image_path)
                    
            except Exception as e:
                self.processingError.emit(str(e), image_path)
                
        # Emit final progress and completion signal
        self.progressChanged.emit(100)
        self.processingFinished.emit()


class BatchProcessorView(QDialog):
    """
    Dialog for batch processing multiple images.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the dialog.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.initUI()
        
        # Initialize instance variables
        self.image_paths = []
        self.worker = None
        
    def initUI(self):
        """Set up the user interface."""
        # Set window properties
        self.setWindowTitle("Batch Processing")
        self.setMinimumSize(600, 500)
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Input section
        input_group = QGroupBox("Input Images")
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)
        
        # Input folder selection
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Input Folder:")
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browseInputFolder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_button)
        input_layout.addLayout(folder_layout)
        
        # Image list
        self.image_list = QListWidget()
        input_layout.addWidget(self.image_list)
        
        # Add button for individual images
        add_button = QPushButton("Add Images...")
        add_button.clicked.connect(self.addImages)
        input_layout.addWidget(add_button)
        
        main_layout.addWidget(input_group)
        
        # Processing options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)
        
        # Filter selection
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Average", "Negative", "Sharpen", "Laplacian", "Logarithm"])
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        options_layout.addLayout(filter_layout)
        
        # Sensitivity selection
        sensitivity_layout = QHBoxLayout()
        sensitivity_label = QLabel("Sensitivity:")
        self.sensitivity_spin = QSpinBox()
        self.sensitivity_spin.setRange(1, 255)
        self.sensitivity_spin.setValue(16)
        self.sensitivity_spin.setToolTip("Sensitivity value for comparison (1-255)")
        
        sensitivity_layout.addWidget(sensitivity_label)
        sensitivity_layout.addWidget(self.sensitivity_spin)
        options_layout.addLayout(sensitivity_layout)
        
        main_layout.addWidget(options_group)
        
        # Output section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)
        
        # Output folder selection
        output_folder_layout = QHBoxLayout()
        output_folder_label = QLabel("Output Folder:")
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        output_browse_button = QPushButton("Browse...")
        output_browse_button.clicked.connect(self.browseOutputFolder)
        
        output_folder_layout.addWidget(output_folder_label)
        output_folder_layout.addWidget(self.output_folder_edit)
        output_folder_layout.addWidget(output_browse_button)
        output_layout.addLayout(output_folder_layout)
        
        main_layout.addWidget(output_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Processing")
        self.start_button.clicked.connect(self.startProcessing)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancelProcessing)
        self.cancel_button.setEnabled(False)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        
    def browseInputFolder(self):
        """Browse for input folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Input Folder", "", QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.folder_edit.setText(folder)
            self.loadImagesFromFolder(folder)
            
    def loadImagesFromFolder(self, folder):
        """
        Load images from a folder.
        
        Args:
            folder (str): Path to the folder
        """
        # Clear the current list
        self.image_list.clear()
        self.image_paths = []
        
        # Find all image files
        image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff"]
        for ext in image_extensions:
            paths = glob.glob(os.path.join(folder, ext))
            self.image_paths.extend(paths)
            
        # Add to the list widget
        for path in self.image_paths:
            self.image_list.addItem(os.path.basename(path))
            
        # Update status
        self.status_label.setText(f"Loaded {len(self.image_paths)} images")
        
    def addImages(self):
        """Add individual images."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", 
            "Image Files (*.jpg *.jpeg *.png *.bmp *.tif *.tiff);;All Files (*)"
        )
        
        if files:
            # Add to existing list
            for file in files:
                if file not in self.image_paths:
                    self.image_paths.append(file)
                    self.image_list.addItem(os.path.basename(file))
                    
            # Update status
            self.status_label.setText(f"Loaded {len(self.image_paths)} images")
            
    def browseOutputFolder(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", "", QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.output_folder_edit.setText(folder)
            
    def startProcessing(self):
        """Start the batch processing."""
        # Validate inputs
        if not self.image_paths:
            QMessageBox.warning(self, "Warning", "No images selected for processing.")
            return
            
        if not self.output_folder_edit.text():
            QMessageBox.warning(self, "Warning", "Please select an output folder.")
            return
            
        # Get processing options
        filter_name = self.filter_combo.currentText()
        sensitivity = self.sensitivity_spin.value()
        output_dir = self.output_folder_edit.text()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create worker thread
        self.worker = BatchProcessorWorker(
            self.image_paths, filter_name, sensitivity, output_dir, self
        )
        
        # Connect signals
        self.worker.progressChanged.connect(self.progress_bar.setValue)
        self.worker.imageProcessed.connect(self.onImageProcessed)
        self.worker.processingFinished.connect(self.onProcessingFinished)
        self.worker.processingError.connect(self.onProcessingError)
        
        # Update UI
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.status_label.setText("Processing...")
        
        # Start the worker
        self.worker.start()
        
    def cancelProcessing(self):
        """Cancel the processing."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_label.setText("Canceling...")
            
    def onImageProcessed(self, output_path):
        """
        Handle processed image.
        
        Args:
            output_path (str): Path to the processed image
        """
        self.status_label.setText(f"Processed: {os.path.basename(output_path)}")
        
    def onProcessingFinished(self):
        """Handle processing completion."""
        self.status_label.setText(f"Processing complete - {len(self.image_paths)} images processed")
        self.progress_bar.setValue(100)
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
    def onProcessingError(self, error_message, file_path):
        """
        Handle processing error.
        
        Args:
            error_message (str): Error message
            file_path (str): Path to the file that caused the error
        """
        filename = os.path.basename(file_path)
        self.status_label.setText(f"Error processing {filename}: {error_message}")
        
        # Log the error
        print(f"Error processing {file_path}: {error_message}")