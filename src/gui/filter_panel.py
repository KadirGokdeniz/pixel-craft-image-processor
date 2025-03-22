"""
Filter Panel Component for PixelCraft.

This module provides the filter selection and configuration panel
for the PixelCraft application.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                            QLabel, QSlider, QPushButton, QSpinBox, QGroupBox,
                            QRadioButton, QButtonGroup, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal

class FilterPanel(QWidget):
    """
    A panel for selecting and configuring image filters.
    
    This panel allows users to select from available filters and
    adjust sensitivity settings for comparison.
    """
    
    # Define signals for communicating with parent widgets
    filterApplied = pyqtSignal(str, int)  # Signal emitted when a filter is applied
    
    def __init__(self, parent=None):
        """
        Initialize the filter panel.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """Set up the user interface components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Filter selection group
        filter_group = QGroupBox("Filter Selection")
        filter_layout = QVBoxLayout()
        filter_group.setLayout(filter_layout)
        
        # Filter label and combobox
        filter_selector_layout = QHBoxLayout()
        filter_label = QLabel("Select Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Average", "Negative", "Sharpen", "Laplacian", "Logarithm"])
        self.filter_combo.currentTextChanged.connect(self.onFilterChanged)
        
        filter_selector_layout.addWidget(filter_label)
        filter_selector_layout.addWidget(self.filter_combo)
        filter_layout.addLayout(filter_selector_layout)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        filter_layout.addWidget(line)
        
        # Filter parameters section
        self.filter_params_layout = QVBoxLayout()
        filter_layout.addLayout(self.filter_params_layout)
        
        # Add filter section to main layout
        main_layout.addWidget(filter_group)
        
        # Sensitivity section
        sensitivity_group = QGroupBox("Comparison Settings")
        sensitivity_layout = QVBoxLayout()
        sensitivity_group.setLayout(sensitivity_layout)
        
        sensitivity_label = QLabel("Sensitivity for comparison:")
        sensitivity_layout.addWidget(sensitivity_label)
        
        # Sensitivity options as radio buttons
        self.sensitivity_group = QButtonGroup(self)
        sensitivity_values = [1, 2, 4, 16, 32, 64, 128, 255]
        radio_layout = QHBoxLayout()
        
        for i, value in enumerate(sensitivity_values):
            radio = QRadioButton(str(value))
            radio.setChecked(value == 16)  # Default to 16
            self.sensitivity_group.addButton(radio, value)
            radio_layout.addWidget(radio)
        
        sensitivity_layout.addLayout(radio_layout)
        
        # Add sensitivity section to main layout
        main_layout.addWidget(sensitivity_group)
        
        # Apply button
        apply_button = QPushButton("Apply Filter")
        apply_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        apply_button.clicked.connect(self.applyFilter)
        main_layout.addWidget(apply_button)
        
        # Add some space
        main_layout.addStretch()
        
    def onFilterChanged(self, filter_name):
        """
        Handle filter selection change.
        
        Args:
            filter_name (str): Name of the selected filter
        """
        # Clear existing parameters
        while self.filter_params_layout.count():
            item = self.filter_params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add parameters specific to the selected filter
        if filter_name == "Average":
            # Kernel size parameter
            param_layout = QHBoxLayout()
            param_layout.addWidget(QLabel("Kernel Size:"))
            
            kernel_size = QSpinBox()
            kernel_size.setMinimum(3)
            kernel_size.setMaximum(15)
            kernel_size.setSingleStep(2)  # Only odd numbers
            kernel_size.setValue(5)
            kernel_size.valueChanged.connect(lambda x: kernel_size.setValue(x if x % 2 == 1 else x + 1))
            
            param_layout.addWidget(kernel_size)
            self.filter_params_layout.addLayout(param_layout)
            
        elif filter_name == "Sharpen":
            # Strength parameter
            param_layout = QHBoxLayout()
            param_layout.addWidget(QLabel("Sharpening Strength:"))
            
            strength_slider = QSlider(Qt.Horizontal)
            strength_slider.setMinimum(1)
            strength_slider.setMaximum(10)
            strength_slider.setValue(5)
            
            param_layout.addWidget(strength_slider)
            param_layout.addWidget(QLabel("5"))  # Default value
            strength_slider.valueChanged.connect(lambda v: param_layout.itemAt(2).widget().setText(str(v)))
            
            self.filter_params_layout.addLayout(param_layout)
            
    def applyFilter(self):
        """Apply the selected filter with current settings."""
        # Get selected filter
        filter_name = self.filter_combo.currentText()
        
        # Get sensitivity value
        sensitivity = self.sensitivity_group.checkedId()
        
        # Emit signal with selected filter and sensitivity
        self.filterApplied.emit(filter_name, sensitivity)
        
    def getCurrentFilter(self):
        """
        Get the currently selected filter.
        
        Returns:
            str: Name of the selected filter
        """
        return self.filter_combo.currentText()
    
    def getCurrentSensitivity(self):
        """
        Get the currently selected sensitivity.
        
        Returns:
            int: Selected sensitivity value
        """
        return self.sensitivity_group.checkedId()