import ctypes
import sys
import os

def show_msg(message, title="Kodys Environment Diagnostic"):
    try:
        ctypes.windll.user32.MessageBoxW(0, str(message), str(title), 0)
    except Exception as e:
        print(f"FAILED TO SHOW POPUP: {message} | Error: {e}")

if __name__ == "__main__":
    msg = f"Kodys Diagnostic Tool Active\n\n"
    msg += f"Platform: {sys.platform}\n"
    msg += f"Python: {sys.version.split()[0]}\n"
    msg += f"Executable: {sys.executable}\n"
    msg += f"CWD: {os.getcwd()}\n"
    
    show_msg(msg)
    
    try:
        import PyQt5.QtCore
        show_msg("Success: PyQt5 Imported", "Dependency Check")
    except Exception as e:
        show_msg(f"FAILED: PyQt5 Import Error: {e}", "Dependency Check")

    try:
        import django
        show_msg("Success: Django Imported", "Dependency Check")
    except Exception as e:
        show_msg(f"FAILED: Django Import Error: {e}", "Dependency Check")

    show_msg("Diagnostic Complete. If you saw all popups, your build environment is functional.", "End of Test")
