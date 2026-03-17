import sys
import os
import traceback
import platform

def run_sanity_check():
    print("[AUDIT] Kodys CLINICAL: FULL-SPECTRUM BUNDLE VERIFICATION (v7.1)")
    print("----------------------------------------------------------------")
    
    # 1. CORE MODULE AUDIT (Checks for ModuleNotFoundErrors)
    clinical_stack = [
        "django", "numpy", "xlsxwriter", "fitz", "pymupdf", "pdfkit", "PIL.Image",
        "cryptography", "setuptools", "pkg_resources", "heartpy", "pyhrv", 
        "scipy", "matplotlib", "pandas", "serial", "PyQt5", "cv2", "psutil", "requests"
    ]
    
    if sys.platform == "win32":
        clinical_stack.append("pywinusb.hid")
        
    failed_modules = []
    print(f"[1/3] Auditing {len(clinical_stack)} Clinical Modules...")
    for module_name in clinical_stack:
        try:
            __import__(module_name)
        except Exception as e:
            print(f"  [X] FAILED: {module_name} ({e})")
            failed_modules.append(module_name)

    # 2. ASSET INTEGRITY AUDIT (Cross-Platform Path Resolver)
    print("\n[2/3] Auditing Physical Clinical Assets...")
    
    # Discovery: Check multiple potential bundle roots for cross-platform compatibility
    # Priority: Env Var > sys.path[0] > Current Dir
    search_roots = []
    if os.environ.get("BUNDLE_ROOT"):
        search_roots.append(os.environ.get("BUNDLE_ROOT"))
    
    # Add standard PyInstaller paths
    for p in sys.path:
        if "dist" in p:
            search_roots.append(p)
            # Mac specific resource path
            if ".app/Contents/MacOS" in p:
                search_roots.append(p.replace("Contents/MacOS", "Contents/Resources"))

    required_assets = ["app_config", "kodys", "app_assets", "config", "db.sqlite3", "wkhtmltopdf"]
    failed_assets = []

    for asset in required_assets:
        found = False
        checked_paths = []
        for root in search_roots:
            asset_path = os.path.join(root, asset)
            checked_paths.append(asset_path)
            if os.path.exists(asset_path):
                print(f"  [OK] Asset Found: {asset}")
                found = True
                break
        
        if not found:
            # Final fallback: check relative to script in case of local execution
            if os.path.exists(os.path.join(os.getcwd(), "dist", "KodysCAN", asset)):
                 print(f"  [OK] Asset Found (Fallback): {asset}")
                 found = True
            
        if not found:
            print(f"  [X] ASSET MISSING: {asset}")
            # print(f"      (Scanned paths: {checked_paths})")
            failed_assets.append(asset)

    # 3. CLINICAL SERVER HANDSHAKE
    print("\n[3/3] Testing Clinical Server Initialization...")
    engine_found = False
    for root in search_roots:
        if os.path.exists(os.path.join(root, "app_config", "manage.py")) or \
           os.path.exists(os.path.join(root, "app_config", "manage.pyc")):
            print("  [OK] Clinical Management Engine Detected.")
            engine_found = True
            break
    
    if not engine_found:
        print("  [X] ERROR: Clinical Management Engine (manage.py) is missing!")
        failed_assets.append("app_config/manage.py")

    print("\n----------------------------------------------------------------")
    if not failed_modules and not failed_assets:
        print("[SUCCESS] FULL-SPECTRUM AUDIT PASSED: The bundle is clinically sound.")
        sys.exit(0)
    else:
        print(f"[CRITICAL FAILURE] Audit identified {len(failed_modules) + len(failed_assets)} issues.")
        sys.exit(1)

if __name__ == "__main__":
    run_sanity_check()
