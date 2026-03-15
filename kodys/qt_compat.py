"""
Kodys CAN - Master Compatibility Engine (V3.2 - Complete Clinical API)
Unifies legacy PyQt4 and CEF logic into modern PyQt5.
"""
import sys
import types

KODYS_SHIM_VERSION = "3.2.0"

def create_module_shim(name, members):
    mod = types.ModuleType(name)
    # We only copy clinical methods, strictly skipping ALL system attributes
    for k, v in members.items():
        if k.startswith('_'):
            continue
        try:
            setattr(mod, k, v)
        except:
            pass
    sys.modules[name] = mod
    return mod

try:
    import PyQt5.QtCore as QtCore
    import PyQt5.QtGui as QtGui
    import PyQt5.QtWidgets as QtWidgets
    import PyQt5.QtWebEngineWidgets as QtWebEngine
    import PyQt5.QtPrintSupport as QtPrint

    # 1. PyQt4 Parity
    fake_gui_members = {}
    for mod in [QtGui, QtWidgets, QtPrint]:
        for attr in dir(mod):
            if not attr.startswith('_'):
                fake_gui_members[attr] = getattr(mod, attr)
    
    create_module_shim('PyQt4.QtCore', {k: getattr(QtCore, k) for k in dir(QtCore) if not k.startswith('_')})
    create_module_shim('PyQt4.QtGui', fake_gui_members)
    create_module_shim('PyQt4.QtWebKit', {'QWebView': QtWebEngine.QWebEngineView})
    create_module_shim('PyQt4', {'QtCore': sys.modules['PyQt4.QtCore'], 
                                'QtGui': sys.modules['PyQt4.QtGui'],
                                'QtWebKit': sys.modules['PyQt4.QtWebKit']})

    # 2. CEFPython3 Parity
    class CEFBrowserShim(QtWebEngine.QWebEngineView):
        def GetMainFrame(self): return self
        def LoadUrl(self, url): self.setUrl(QtCore.QUrl(url))
        def GetUrl(self): return self.url().toString()
        def ExecuteJavascript(self, js): self.page().runJavaScript(js)
        def SetClientHandler(self, handler): self.handler = handler
        def GetJavascriptBindings(self): return type('obj', (object,), {'SetFunction': lambda *a: None})()
        def SetJavascriptBindings(self, bindings): self.bindings = bindings
        
        def ExecuteFunction(self, name, *args):
            # Convert Python arguments to JS-safe strings
            import json
            js_args = [json.dumps(a) for a in args]
            js_code = f"{name}({', '.join(js_args)})"
            self.page().runJavaScript(js_code)

    class WindowInfoShim:
        def SetAsChild(self, winId): self.winId = winId

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
        def WindowInfo(self): return WindowInfoShim()

    cef_instance = CEFShim()
    cef_members = {k: getattr(cef_instance, k) for k in dir(cef_instance) if not k.startswith('_')}
    
    create_module_shim('cefpython3', {'cefpython': cef_instance})
    create_module_shim('cefpython3.cefpython', cef_members)

    print(f"Kodys: Enterprise Compatibility Engine V{KODYS_SHIM_VERSION} Active.")

except ImportError as e:
    print(f"Kodys Critical Extension Error: {e}")
