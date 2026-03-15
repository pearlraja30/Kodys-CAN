import os
import sys
try:
    import kodys.qt_compat
except ImportError:
    pass
import json
import urllib.request
import threading
import subprocess
from PyQt4 import QtGui, QtCore

CURRENT_VERSION = "2.0.0"

# Change this URL to the actual location where you host your update JSON
# The JSON should look like:
# {
#   "version": "2.1.0",
#   "url": "https://example.com/downloads/Kodys_Setup_v2.1.0.exe",
#   "release_notes": "Added new HRV visualization features and fixed bugs."
# }
UPDATE_JSON_URL = "https://kodys-update-server.com/version.json"

class UpdateCheckerThread(QtCore.QThread):
    update_available_signal = QtCore.pyqtSignal(str, str, str)

    def run(self):
        try:
            req = urllib.request.Request(UPDATE_JSON_URL)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                remote_version = data.get("version")
                download_url = data.get("url")
                release_notes = data.get("release_notes", "A new update is available for Kodys CAN.")

                if remote_version and remote_version != CURRENT_VERSION:
                    self.update_available_signal.emit(remote_version, download_url, release_notes)
        except Exception as e:
            print("Auto-update check failed silently in background:", e)

class UpdateDownloader(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal(int)
    finished_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)

    def __init__(self, download_url):
        super(UpdateDownloader, self).__init__()
        self.download_url = download_url
        self.temp_exe_path = os.path.join(os.environ.get("TEMP", "C:\\temp"), "Kodys_Update_Package.exe")

    def run(self):
        try:
            req = urllib.request.Request(self.download_url, headers={'User-Agent': 'Kodys-AutoUpdater/1.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                total_size = int(response.info().get('Content-Length', 0))
                downloaded = 0
                chunk_size = 8192

                with open(self.temp_exe_path, 'wb') as out_file:
                    while True:
                        buffer = response.read(chunk_size)
                        if not buffer:
                            break
                        out_file.write(buffer)
                        downloaded += len(buffer)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress_signal.emit(percent)
                
            self.finished_signal.emit(self.temp_exe_path)
        except Exception as e:
            self.error_signal.emit(str(e))

class AutoUpdaterUI(QtCore.QObject):
    def __init__(self, parent_widget):
        super(AutoUpdaterUI, self).__init__()
        self.parent_widget = parent_widget
        self.checker = UpdateCheckerThread()
        self.checker.update_available_signal.connect(self.prompt_update)
        
    def check_updates(self):
        self.checker.start()

    def prompt_update(self, version, download_url, notes):
        msg_box = QtGui.QMessageBox(self.parent_widget)
        msg_box.setIcon(QtGui.QMessageBox.Information)
        msg_box.setWindowTitle("Kodys System Update Available")
        msg_box.setText("Version {} is now available.\n\nRelease Notes:\n{}".format(version, notes))
        msg_box.setInformativeText("Would you like to download and install this remote patch now?")
        msg_box.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msg_box.setDefaultButton(QtGui.QMessageBox.Yes)

        if msg_box.exec_() == QtGui.QMessageBox.Yes:
            self.start_download(download_url)

    def start_download(self, download_url):
        self.progress_dialog = QtGui.QProgressDialog("Downloading remote patch...", "Cancel", 0, 100, self.parent_widget)
        self.progress_dialog.setWindowTitle("Kodys Updater")
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)

        self.downloader = UpdateDownloader(download_url)
        self.downloader.progress_signal.connect(self.progress_dialog.setValue)
        self.downloader.finished_signal.connect(self.apply_update)
        self.downloader.error_signal.connect(self.download_error)
        
        self.progress_dialog.canceled.connect(self.downloader.terminate)

        self.progress_dialog.show()
        self.downloader.start()

    def apply_update(self, exe_path):
        self.progress_dialog.close()
        
        msg_box = QtGui.QMessageBox(self.parent_widget)
        msg_box.setIcon(QtGui.QMessageBox.Information)
        msg_box.setWindowTitle("Update Ready")
        msg_box.setText("The patch has been successfully downloaded.")
        msg_box.setInformativeText("The application will now safely restart to apply the remote updates. Please ensure your patient tests are finalized.")
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.exec_()
        
        # Launch the new installer silently overlaying the current install directory
        # Example using typical Inno Setup arguments
        try:
            install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            # /SILENT /SUPPRESSMSGBOXES runs in background without interacting.
            # /DIR overrides installation directory
            install_command = [exe_path, '/SILENT', '/SUPPRESSMSGBOXES', '/DIR="{}"'.format(install_dir)]
            subprocess.Popen(install_command, creationflags=subprocess.CREATE_NEW_CONSOLE | 0x00000008)  # 0x00000008 = DETACHED_PROCESS
            
            # Terminate the current application immediately so files can be overwritten
            QtGui.QApplication.quit()
            os._exit(0)
        except Exception as e:
            self.download_error("Failed to launch patching sequence: " + str(e))

    def download_error(self, err_msg):
        self.progress_dialog.close()
        QtGui.QMessageBox.critical(self.parent_widget, "Update Failed", "Could not download the patch.\nError: " + err_msg)

def initialize_updater(parent_window):
    """
    Hook to initialize the remote auto-updater ecosystem.
    """
    updater_ui = AutoUpdaterUI(parent_window)
    # Keep reference to prevent garbage collection
    parent_window.updater_instance = updater_ui
    updater_ui.check_updates()
