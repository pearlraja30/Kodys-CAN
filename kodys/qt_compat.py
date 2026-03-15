"""
Kodys CAN - Modern Qt Compatibility Shim
Bridges the legacy PyQt4 API to modern PyQt5 to ensure 
Windows and macOS support on Python 3.11+.
"""
import sys

try:
    # First attempt native PyQt5 loading
    import PyQt5.QtCore as QtCore
    import PyQt5.QtGui as QtGui
    import PyQt5.QtWidgets as QtWidgets
    
    # Map the separated Qt5 modules back into the unified Qt4 namespace
    # In Qt5, Widgets were split out of QtGui.
    class Qt4QtGui(object):
        pass
        
    fake_gui = Qt4QtGui()
    
    # Merge QWidgets into the fake QtGui for backward compatibility
    for attr in dir(QtWidgets):
        setattr(fake_gui, attr, getattr(QtWidgets, attr))
    # Keep the original QtGui elements
    for attr in dir(QtGui):
        setattr(fake_gui, attr, getattr(QtGui, attr))
        
    # Handle the WebKit to WebEngine transition or legacy WebKit
    try:
        import PyQt5.QtWebKitWidgets as QtWebKit
    except ImportError:
        try:
            # Fallback for systems using newer WebEngine
            import PyQt5.QtWebEngineWidgets as QtWebEngine
            class FakeWebKit:
                QWebView = QtWebEngine.QWebEngineView
            QtWebKit = FakeWebKit()
        except ImportError:
            QtWebKit = None

    # Inject into sys.modules so 'from PyQt4 import ...' works automatically
    class FakePyQt4:
        def __init__(self):
            self.QtCore = QtCore
            self.QtGui = fake_gui
            self.QtWebKit = QtWebKit

    sys.modules['PyQt4'] = FakePyQt4()
    sys.modules['PyQt4.QtCore'] = QtCore
    sys.modules['PyQt4.QtGui'] = fake_gui
    sys.modules['PyQt4.QtWebKit'] = QtWebKit
    
    print("Kodys: Successfully shimmed PyQt4 to PyQt5 environment.")

except ImportError as e:
    print(f"Kodys Critical Error: Failed to shim Qt environment. {e}")
