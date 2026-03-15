import os
import sys
import threading
import requests
try:
    import kodys.qt_compat
except ImportError:
    pass
from PyQt4 import QtGui, QtCore

# Import shared core licensing logic
try:
    import kodys.license_core as license_core
except ImportError:
    # Handle the fact we might be running from application_code
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    import kodys.license_core as license_core

class LicenseActivationUI(QtGui.QDialog):
    """A PyQt Dialog that blocks the application until a valid license is entered."""
    def __init__(self, hardware_id):
        super(LicenseActivationUI, self).__init__()
        self.hardware_id = hardware_id
        self.is_activated = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Kodys - Software Activation Required")
        self.setFixedSize(500, 250)
        self.setStyleSheet("background-color: #f4f6f9; font-family: Arial;")
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        layout = QtGui.QVBoxLayout()

        # Header
        lbl_msg = QtGui.QLabel("This installation of Kodys CAN is completely secured.\nYou must activate the software with a valid license key.")
        lbl_msg.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        lbl_msg.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl_msg)
        layout.addSpacing(15)

        # Hardware ID Display
        hw_layout = QtGui.QHBoxLayout()
        lbl_hw = QtGui.QLabel("Your Hardware ID:")
        lbl_hw.setStyleSheet("font-size: 12px; color: #555; font-weight: bold;")
        self.txt_hw = QtGui.QLineEdit(self.hardware_id)
        self.txt_hw.setReadOnly(True)
        self.txt_hw.setStyleSheet("font-size: 14px; background: #e0e0e0; color: #000; padding: 5px; border: 1px solid #ccc;")
        hw_layout.addWidget(lbl_hw)
        hw_layout.addWidget(self.txt_hw)
        layout.addLayout(hw_layout)

        layout.addSpacing(10)

        # License Key Input
        key_layout = QtGui.QHBoxLayout()
        lbl_key = QtGui.QLabel("Enter License Key:")
        lbl_key.setStyleSheet("font-size: 12px; color: #555; font-weight: bold;")
        self.txt_key = QtGui.QLineEdit()
        self.txt_key.setPlaceholderText("XXXX-XXXX-XXXX-XXXX-XXXX")
        self.txt_key.setStyleSheet("font-size: 14px; padding: 5px; border: 1px solid #00bdb6; background: #fff;")
        key_layout.addWidget(lbl_key)
        key_layout.addWidget(self.txt_key)
        layout.addLayout(key_layout)

        layout.addSpacing(20)

        # Buttons
        btn_layout = QtGui.QHBoxLayout()
        self.btn_activate = QtGui.QPushButton("Activate Software")
        self.btn_activate.setStyleSheet("background-color: #00bdb6; color: white; font-weight: bold; padding: 8px 15px; border: none; font-size: 14px;")
        self.btn_activate.clicked.connect(self.attempt_activation)
        
        self.btn_exit = QtGui.QPushButton("Exit")
        self.btn_exit.setStyleSheet("background-color: #ccc; color: #333; padding: 8px 15px; border: none; font-size: 14px;")
        self.btn_exit.clicked.connect(self.reject)

        self.btn_import = QtGui.QPushButton("Import License File (.dat)")
        self.btn_import.setStyleSheet("background-color: #fff; color: #00bdb6; font-weight: bold; padding: 8px 15px; border: 1.5px solid #00bdb6; font-size: 14px;")
        self.btn_import.clicked.connect(self.import_license_file)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_import)
        btn_layout.addWidget(self.btn_activate)
        btn_layout.addWidget(self.btn_exit)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def import_license_file(self):
        file_path = QtGui.QFileDialog.getOpenFileName(self, "Select License File", "", "License Files (*.dat);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    key = f.read().strip()
                self.txt_key.setText(key)
                self.attempt_activation()
            except Exception as e:
                QtGui.QMessageBox.warning(self, "Import Error", f"Could not read the license file: {e}")

    def attempt_activation(self):
        user_key = self.txt_key.text().strip()
        if license_core.verify_license(self.hardware_id, user_key):
            license_core.save_license(user_key)
            self.is_activated = True
            
            # Proactively background sync with Admin Server if reachable
            # Path: http://127.0.0.1:8000/api/license/activate/
            # (In production, replace with cloud URL)
            threading.Thread(target=self.sync_activation_with_server, args=(user_key,), daemon=True).start()
            
            QtGui.QMessageBox.information(self, "Success", "Software activated successfully! Thank you.")
            self.accept()
        else:
            QtGui.QMessageBox.critical(self, "Activation Failed", "Invalid License Key. Please contact Kodys Administrator and provide your Hardware ID.")
            self.txt_key.clear()

    def sync_activation_with_server(self, key):
        """Attempts to notify the central office that this machine is now active."""
        try:
            # We try local 8000 first, or any pre-configured central server IP
            server_urls = ["http://127.0.0.1:8000/api/license/activate/"]
            for url in server_urls:
                try:
                    requests.post(url, data={
                        'hardware_id': self.hardware_id,
                        'key': key
                    }, timeout=5)
                    break 
                except:
                    continue
        except:
            pass # Silent fail: do not block clinician if central server is offline

def ensure_licensed(app_instance):
    """
    Checks the license. If invalid, shows the UI blocking startup.
    If the user fails or clicks exit, exits the app.
    MUST be called after QApplication is created, but before the main window starts.
    """
    if license_core.is_system_licensed():
        return True # Authorized

    hw_id = license_core.get_hardware_id()
    # Need user interaction
    dialog = LicenseActivationUI(hw_id)
    result = dialog.exec_()
    
    if dialog.is_activated:
        return True
    
    # User canceled or closed without activating
    sys.exit(0)
    return False
