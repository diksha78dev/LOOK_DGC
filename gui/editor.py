import os
import webbrowser
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                               QFileDialog, QMessageBox, QTextEdit, QLabel)
from PySide6.QtWebEngineWidgets import QWebEngineView

from tools import ToolWidget


class EditorWidget(ToolWidget):
    def __init__(self, parent=None):
        super(EditorWidget, self).__init__(parent)
        
        main_layout = QVBoxLayout()
        
        # Header with instructions
        header_label = QLabel("🔧 Hex Editor - Binary File Analysis")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        main_layout.addWidget(header_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Online HexEd.it button
        online_btn = QPushButton("🌐 Open HexEd.it Online")
        online_btn.clicked.connect(self.open_online_editor)
        online_btn.setToolTip("Open the full-featured online hex editor")
        button_layout.addWidget(online_btn)
        
        # Local file button
        local_btn = QPushButton("📁 Open Local File")
        local_btn.clicked.connect(self.open_local_file)
        local_btn.setToolTip("Open a local file for hex analysis")
        button_layout.addWidget(local_btn)
        
        # Built-in viewer button
        builtin_btn = QPushButton("🔍 Built-in Hex Viewer")
        builtin_btn.clicked.connect(self.show_builtin_viewer)
        builtin_btn.setToolTip("Use the built-in hex viewer (offline)")
        button_layout.addWidget(builtin_btn)
        
        main_layout.addLayout(button_layout)
        
        # Web view for online editor
        self.web_view = QWebEngineView()
        self.web_view.hide()
        main_layout.addWidget(self.web_view)
        
        # Built-in hex viewer
        self.hex_viewer = QTextEdit()
        self.hex_viewer.setFont(self.get_monospace_font())
        self.hex_viewer.setReadOnly(True)
        self.hex_viewer.hide()
        main_layout.addWidget(self.hex_viewer)
        
        # Status label
        self.status_label = QLabel("💡 Choose an option above to start hex editing")
        self.status_label.setStyleSheet("color: #666; padding: 10px;")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        
    def get_monospace_font(self):
        """Get a monospace font for hex display"""
        from PySide6.QtGui import QFont
        font = QFont("Consolas, Monaco, monospace")
        font.setPointSize(10)
        return font
        
    def open_online_editor(self):
        """Open HexEd.it in web view or browser"""
        try:
            # Try to load in web view first
            self.web_view.load(QUrl("https://hexed.it/"))
            self.web_view.show()
            self.hex_viewer.hide()
            self.status_label.setText("🌐 Loading HexEd.it online editor...")
        except Exception as e:
            # Fallback to system browser
            try:
                webbrowser.open("https://hexed.it/")
                self.status_label.setText("🌐 Opened HexEd.it in your default browser")
            except Exception as e2:
                QMessageBox.warning(self, "Error", f"Cannot open online editor: {str(e2)}")
                self.status_label.setText("❌ Failed to open online editor")
    
    def open_local_file(self):
        """Open a local file for hex editing"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select File for Hex Analysis",
            "",
            "All Files (*.*)"
        )
        
        if file_path:
            try:
                # For online editor, we can't directly load local files due to security
                # So we show instructions
                self.show_local_file_instructions(file_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Cannot process file: {str(e)}")
    
    def show_local_file_instructions(self, file_path):
        """Show instructions for loading local file"""
        instructions = f"""
📁 Local File Selected: {os.path.basename(file_path)}
📍 Full Path: {file_path}

🌐 For Online HexEd.it:
1. Click 'Open HexEd.it Online' button
2. In HexEd.it, click 'Open file' 
3. Select your file: {file_path}

🔍 For Built-in Viewer:
1. Click 'Built-in Hex Viewer' to see hex dump
2. This works offline and shows file structure

💡 Tip: The online editor has more features like editing, 
while the built-in viewer is read-only but works offline.
        """
        
        self.hex_viewer.setPlainText(instructions)
        self.hex_viewer.show()
        self.web_view.hide()
        self.status_label.setText(f"📁 File ready: {os.path.basename(file_path)}")
        
        # Store file path for built-in viewer
        self.current_file = file_path
    
    def show_builtin_viewer(self):
        """Show built-in hex viewer"""
        if not hasattr(self, 'current_file'):
            # No file selected, ask user to select one
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Select File for Hex Viewing",
                "",
                "All Files (*.*)"
            )
            if not file_path:
                return
            self.current_file = file_path
        
        try:
            self.display_hex_dump(self.current_file)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot read file: {str(e)}")
    
    def display_hex_dump(self, file_path):
        """Display hex dump of file"""
        try:
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                chunk_size = 16
                offset = 0
                hex_lines = []
                
                # Add header
                hex_lines.append("🔍 LOOK-DGC Built-in Hex Viewer")
                hex_lines.append("=" * 80)
                hex_lines.append(f"📁 File: {os.path.basename(file_path)}")
                hex_lines.append(f"📍 Path: {file_path}")
                hex_lines.append(f"📊 Size: {os.path.getsize(file_path)} bytes")
                hex_lines.append("=" * 80)
                hex_lines.append("")
                hex_lines.append("Offset    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  ASCII")
                hex_lines.append("-" * 80)
                
                # Read and display first 1024 lines (16KB) to avoid memory issues
                max_lines = 1024
                line_count = 0
                
                while line_count < max_lines:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Format hex bytes
                    hex_bytes = ' '.join(f'{b:02X}' for b in chunk)
                    hex_bytes = hex_bytes.ljust(47)  # Pad to align ASCII
                    
                    # Format ASCII representation
                    ascii_repr = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                    
                    # Create line
                    line = f"{offset:08X}  {hex_bytes}  {ascii_repr}"
                    hex_lines.append(line)
                    
                    offset += len(chunk)
                    line_count += 1
                
                if line_count >= max_lines:
                    hex_lines.append("")
                    hex_lines.append("⚠️  Display limited to first 16KB for performance")
                    hex_lines.append("💡 Use online HexEd.it for full file editing")
                
                # Display in text widget
                self.hex_viewer.setPlainText('\n'.join(hex_lines))
                self.hex_viewer.show()
                self.web_view.hide()
                self.status_label.setText(f"🔍 Hex view: {os.path.basename(file_path)} ({offset} bytes shown)")
                
        except Exception as e:
            raise Exception(f"Failed to read file: {str(e)}")