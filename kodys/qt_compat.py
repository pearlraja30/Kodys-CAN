"""
Kodys CAN - Master Clinical Compatibility shim
Bridges legacy PyQt4 AND cefpython3 to modern PyQt5/WebEngine.
Ensures support on Python 3.10+ and cross-platform (Mac/Win) reliability.
"""
import sys

try:
    # 1. Initialize Modern PyQt5
    import PyQt5.QtCore as QtCore
    import PyQt5.QtGui as QtGui
    import PyQt5.QtWidgets as QtWidgets
    import PyQt5.QtWebEngineWidgets as QtWebEngine
    
    # --- PyQt4 Shim Logic ---
    class Qt4QtGuiShim(object):
        pass
        
    fake_gui = Qt4QtGuiShim()
    for attr in dir(QtWidgets):
        setattr(fake_gui, attr, getattr(QtWidgets, attr))
    for attr in dir(QtGui):
        setattr(fake_gui, attr, getattr(QtGui, attr))

    # --- CEFPython3 Shim Logic ---
    class CEFShim:
        def __init__(self):
            self.WindowUtils = type('obj', (object,), {'OnSize': lambda *a: None, 'OnSetFocus': lambda *a: None})
            self.LOGSEVERITY_INFO = 0
            self.g_applicationSettings = {"string_encoding": "utf-8"}
            
        def Initialize(self, *a, **k): return True
        def CreateBrowserSync(self, *a, **k): 
            view = QtWebEngine.QWebEngineView()
            # Dynamic method injection to match CEF signatures
            view.GetMainFrame = lambda: view
            view.LoadUrl = view.setUrl
            return view
        def MessageLoopWork(self): pass
        def QuitMessageLoop(self): pass
        def Shutdown(self): pass
        def GetModuleDirectory(self): return ""
        def JavascriptBindings(self, **k): return type('obj', (object,), {'SetFunction': lambda *a: None})()
        def WindowInfo(self): return type('obj', (object,), {})()

    # 2. Inject into Global Namespace
    cef_instance = CEFShim()
    
    # Map both PyQt4 and cefpython3
    sys.modules['PyQt4'] = type('obj', (object,), {'QtCore': QtCore, 'QtGui': fake_gui, 'QtWebKit': type('obj', (object,), {'QWebView': QtWebEngine.QWebEngineView})})
    sys.modules['PyQt4.QtCore'] = QtCore
    sys.modules['PyQt4.QtGui'] = fake_gui
    sys.modules['cefpython3'] = type('obj', (object,), {'cefpython': cef_instance})
    
    # Handle direct 'import cefpython3'
    sys.modules['cefpython3.cefpython'] = cef_instance

    print("Kodys: Global Compatibility Shim (PyQt4 + CEF) Active.")

except ImportError as e:
    print(f"Kodys Critical Error: Failed to shim modern environment. {e}")
