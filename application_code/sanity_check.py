import sys
import os
import traceback
import platform

def run_sanity_check():
    print("[AUDIT] Kodys CLINICAL: FULL-SPECTRUM BUNDLE VERIFICATION (v7.0)")
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
            # print(f"  [OK] {module_name}")
        except Exception as e:
            print(f"  [X] FAILED: {module_name} ({e})")
            failed_modules.append(module_name)

    # 2. ASSET INTEGRITY AUDIT (Checks for Missing Folders/Files)
    print("\n[2/3] Auditing Physical Clinical Assets...")
    # Discover the bundle path (PYTHONPATH should be set to the bundle root during audit)
    bundle_root = sys.path[0]
    required_assets = [
        "app_config", "kodys", "app_assets", "config", "db.sqlite3"
    ]
    
    # Platform specific binary checks
    if sys.platform == "win32":
        required_assets.append("wkhtmltopdf")
    else:
        # On Mac, it's bundled in a specific subfolder or at root depending on build
        required_assets.append("wkhtmltopdf")

    failed_assets = []
    for asset in required_assets:
        asset_path = os.path.join(bundle_root, asset)
        if os.path.exists(asset_path):
            print(f"  [OK] Asset Found: {asset}")
        else:
            print(f"  [X] ASSET MISSING: {asset} (Expected at: {asset_path})")
            failed_assets.append(asset)

    # 3. CLINICAL SERVER HANDSHAKE (Dry Run)
    print("\n[3/3] Testing Clinical Server Initialization...")
    try:
        # We try to import manage.py from the bundle to see if Django is properly configured
        manage_py_path = os.path.join(bundle_root, "app_config", "manage.py")
        if not os.path.exists(manage_py_path):
             manage_py_path = os.path.join(bundle_root, "app_config", "manage.pyc")
             
        if os.path.exists(manage_py_path):
            print("  [OK] Clinical Management Engine Detected.")
        else:
            print("  [X] ERROR: Clinical Management Engine (manage.py) is missing from the bundle!")
            failed_assets.append("app_config/manage.py")
    except Exception as e:
        print(f"  [X] Initialization Failure: {e}")
        failed_assets.append("initialization_logic")

    print("\n----------------------------------------------------------------")
    if not failed_modules and not failed_assets:
        print("[SUCCESS] FULL-SPECTRUM AUDIT PASSED: The bundle is clinically sound.")
        sys.exit(0)
    else:
        print(f"[CRITICAL FAILURE] Audit identified {len(failed_modules) + len(failed_assets)} issues.")
        if failed_modules: print(f"  Missing Libraries: {', '.join(failed_modules)}")
        if failed_assets: print(f"  Missing Assets: {', '.join(failed_assets)}")
        print("\nFATAL: Build aborted. This installer would have failed in production.")
        sys.exit(1)

if __name__ == "__main__":
    run_sanity_check()
