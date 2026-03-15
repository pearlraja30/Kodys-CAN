"""
Kodys CAN - Advanced Enterprise Compatibility Shim
Unifies legacy PyQt4 and CEF logic into modern PyQt5.
Target: Python 3.10 - 3.14+
"""
import sys
import types

def create_module_shim(name, members):
    mod = types.ModuleType(name)
    for k, v in members.items():
        if not k.startswith('__'):
            try:
                setattr(mod, k, v)
            except (AttributeError, TypeError):
                pass
    sys.modules[name] = mod
    return mod

try:
    import PyQt5.QtCore as QtCore
    import PyQt5.QtGui as QtGui
    import PyQt5.QtWidgets as QtWidgets
    import PyQt5.QtWebEngineWidgets as QtWebEngine
    import PyQt5.QtPrintSupport as QtPrint

    # Create the modern Widget-aware QtGui for PyQt4 parity
    fake_gui_members = {}
    for mod in [QtGui, QtWidgets, QtPrint]:
        for attr in dir(mod):
            fake_gui_members[attr] = getattr(mod, attr)
    
    # Inject PyQt4 modules
    create_module_shim('PyQt4.QtCore', {k: getattr(QtCore, k) for k in dir(QtCore)})
    create_module_shim('PyQt4.QtGui', fake_gui_members)
    create_module_shim('PyQt4.QtWebKit', {'QWebView': QtWebEngine.QWebEngineView})
    create_module_shim('PyQt4', {'QtCore': sys.modules['PyQt4.QtCore'], 
                                'QtGui': sys.modules['PyQt4.QtGui'],
                                'QtWebKit': sys.modules['PyQt4.QtWebKit']})

    # Inject CEFPython3 Shim
    class CEFBrowserShim(QtWebEngine.QWebEngineView):
        def GetMainFrame(self): return self
        def LoadUrl(self, url): self.setUrl(QtCore.QUrl(url))
        def ExecuteJavascript(self, js): self.page().runJavaScript(js)

    class CEFShim:
        def __init__(self):
            self.WindowUtils = type('obj', (object,), {'OnSize': lambda *a: None, 'OnSetFocus': lambda *a: None})
            self.LOGSEVERITY_INFO = 0
            self.g_applicationSettings = {"string_encoding": "utf-8"}
        def Initialize(self, *a, **k): return True
        def CreateBrowserSync(self, *a, **k): return CEFBrowserShim()
        def MessageLoopWork(self): pass
        def Shutdown(self): pass
        def GetModuleDirectory(self): return ""
        def JavascriptBindings(self, **k): return type('obj', (object,), {'SetFunction': lambda *a: None})()
        def WindowInfo(self): return type('obj', (object,), {})()

    cef_instance = CEFShim()
    create_module_shim('cefpython3', {'cefpython': cef_instance})
    create_module_shim('cefpython3.cefpython', {k: getattr(cef_instance, k) for k in dir(cef_instance)})

    print("Kodys: Enterprise Compatibility Engine Initialized (Shim 2.0).")

except ImportError as e:
    print(f"Kodys Critical Extension Error: {e}")
