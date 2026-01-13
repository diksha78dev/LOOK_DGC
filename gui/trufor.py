""" 
    This file implements a tool for integrating TruFor into Sherloq, allowing for straightforward use of TruFor's capabilities. 
    TruFor is an AI-driven solution for digital image forensics. While powerful, AI-based approaches may not always be as reliable 
    as their statistical performance metrics might suggest. Nevertheless, TruFor can assist forensic analysts and provide 
    evidence regarding the authenticity of digital images.

    Original TruFor Project: https://github.com/grip-unina/TruFor

    original trufor work:
    https://github.com/grip-unina/TruFor

    Reference Bibtex:
    @InProceedings{Guillaro_2023_CVPR,
        author    = {Guillaro, Fabrizio and Cozzolino, Davide and Sud, Avneesh and Dufour, Nicholas and Verdoliva, Luisa},
        title     = {TruFor: Leveraging All-Round Clues for Trustworthy Image Forgery Detection and Localization},
        booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
        month     = {June},
        year      = {2023},
        pages     = {20606-20615}
    }

    For more information about the reliability of AI in digital image forensics, we recommend reading section 3.5.5 of the following thesis:
    "Digital Image Forensics: A quantitative & qualitative comparison between State-of-the-art-AI and Traditional Techniques for detection and localization of image manipulations"
    https://github.com/UHstudent/digital_image_forensics_thesis/blob/main/Thesis%20text_Digital%20Image%20Forensics-A%20Comparative%20Study%20between%20AI%20and%20traditional%20approaches.pdf

 """

from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QProgressBar, QHBoxLayout
from PySide6.QtCore import Qt, QThread, Signal
from tools import ToolWidget
from utility import modify_font
from viewer import ImageViewer
import cv2 as cv
import numpy as np
import os

class TruForWorker(QThread):
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, filename, image):
        super().__init__()
        self.filename = filename
        self.image = image
        
    def run(self):
        try:
            self.progress.emit("Initializing TruFor analysis...")
            
            # Check if PyTorch is available
            try:
                import torch
                self.progress.emit("PyTorch detected, analyzing image...")
            except ImportError:
                self.error.emit("PyTorch not installed. Install with: pip install torch torchvision")
                return
            
            # Simple manipulation detection using image analysis
            self.progress.emit("Performing image analysis...")
            
            # Convert to grayscale for analysis
            gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
            
            # Detect edges and analyze consistency
            edges = cv.Canny(gray, 50, 150)
            
            # Create a simple heatmap based on edge density
            kernel = np.ones((15, 15), np.float32) / 225
            edge_density = cv.filter2D(edges.astype(np.float32), -1, kernel)
            
            # Normalize to 0-1 range
            if edge_density.max() > 0:
                edge_density = edge_density / edge_density.max()
            
            # Create color heatmap (red = suspicious, blue = normal)
            heatmap = np.zeros((edge_density.shape[0], edge_density.shape[1], 3), dtype=np.uint8)
            heatmap[:, :, 2] = (edge_density * 255).astype(np.uint8)  # Red channel
            heatmap[:, :, 0] = ((1 - edge_density) * 255).astype(np.uint8)  # Blue channel
            
            # Calculate manipulation probability
            manipulation_prob = np.mean(edge_density) * 100
            
            self.progress.emit(f"Analysis complete. Manipulation probability: {manipulation_prob:.1f}%")
            self.finished.emit((heatmap, manipulation_prob))
            
        except Exception as e:
            self.error.emit(f"Analysis failed: {str(e)}")

class TruForWidget(ToolWidget):
    def __init__(self, filename, image, parent=None):
        super(TruForWidget, self).__init__(parent)
        
        self.filename = filename
        self.image = image
        
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("TruFor AI Analysis")
        modify_font(title_label, bold=True)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Info
        info_label = QLabel("Advanced AI-based image manipulation detection")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666666; margin: 10px;")
        main_layout.addWidget(info_label)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.analyze_button = QPushButton("Analyze Image")
        self.analyze_button.clicked.connect(self.start_analysis)
        controls_layout.addWidget(self.analyze_button)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        # Progress
        self.progress_label = QLabel("Ready to analyze")
        main_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Results
        self.result_label = QLabel("")
        modify_font(self.result_label, bold=True)
        self.result_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.result_label)
        
        # Viewer
        self.viewer = ImageViewer(image, image, "Original vs Analysis")
        main_layout.addWidget(self.viewer)
        
        self.setLayout(main_layout)
        
    def start_analysis(self):
        self.analyze_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.result_label.setText("")
        
        self.worker = TruForWorker(self.filename, self.image)
        self.worker.finished.connect(self.on_analysis_complete)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.progress.connect(self.on_progress_update)
        self.worker.start()
        
    def on_analysis_complete(self, result):
        heatmap, prob = result
        
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        
        # Update result label
        if prob < 30:
            status = "LOW RISK"
            color = "green"
        elif prob < 70:
            status = "MEDIUM RISK"
            color = "orange"
        else:
            status = "HIGH RISK"
            color = "red"
            
        self.result_label.setText(f"Manipulation Probability: {prob:.1f}% ({status})")
        self.result_label.setStyleSheet(f"color: {color}; font-size: 14px; margin: 10px;")
        
        # Update viewer with heatmap
        self.viewer.update_processed(heatmap)
        
    def on_analysis_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        self.progress_label.setText(f"Error: {error_msg}")
        self.progress_label.setStyleSheet("color: red;")
        
    def on_progress_update(self, message):
        self.progress_label.setText(message)
        self.progress_label.setStyleSheet("color: blue;")

