from PySide6.QtWidgets import QVBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import QThread, Signal

from pyexiftool import exiftool
from table import TableWidget
from tools import ToolWidget
from utility import exiftool_exe
import os

class ExifWorker(QThread):
    finished = Signal(list)
    error = Signal(str)
    
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        
    def run(self):
        try:
            table = []
            last = None
            exiftool_path = exiftool_exe()
            if not exiftool_path or not os.path.exists(exiftool_path):
                self.error.emit("ExifTool not found")
                return
                
            with exiftool.ExifTool(exiftool_path) as et:
                metadata = et.get_metadata(self.filename)
                for tag, value in metadata.items():
                    ignore = [
                        "SourceFile", "ExifTool:ExifTool", "File:FileName",
                        "File:Directory", "File:FileSize", "File:FileModifyDate",
                        "File:FileInodeChangeDate", "File:FileAccessDate",
                        "File:FileType", "File:FilePermissions",
                        "File:FileTypeExtension", "File:MIMEType",
                    ]
                    if not value or any(t in tag for t in ignore):
                        continue
                    value = str(value).replace(", use -b option to extract", "")
                    value = value.replace("Binary data ", "Binary data: ")
                    group, desc = tag.split(":")
                    if last is None or group != last:
                        table.append([group, desc, value])
                        last = group
                    else:
                        table.append([None, desc, value])
            self.finished.emit(table)
        except Exception as e:
            self.error.emit(str(e))


class ExifWidget(ToolWidget):
    def __init__(self, filename, parent=None):
        super(ExifWidget, self).__init__(parent)
        
        self.loading_label = QLabel("Loading EXIF data...")
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.loading_label)
        self.setLayout(main_layout)
        self.setMinimumSize(740, 500)
        
        self.worker = ExifWorker(filename)
        self.worker.finished.connect(self.on_data_ready)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_data_ready(self, table):
        headers = [self.tr("Group"), self.tr("Description"), self.tr("Value")]
        table_widget = TableWidget(table, headers)
        
        # Clear layout and add table
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        layout.addWidget(table_widget)
        
    def on_error(self, error_msg):
        error_label = QLabel(f"Error loading EXIF data: {error_msg}")
        error_label.setStyleSheet("color: red;")
        
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        layout.addWidget(error_label)
