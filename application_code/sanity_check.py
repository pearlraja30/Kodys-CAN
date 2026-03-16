import sys
import os
import traceback

def run_sanity_check():
    print("[AUDIT] Kodys CLINICAL: COMPREHENSIVE BUNDLE AUDIT (v5.1)")
    print("------------------------------------------------")
    
    # List of critical libraries that must be present in the bundle
    # These cover the GUI, Server, Security, and Diagnostic layers
    clinical_stack = [
        "django",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "numpy",
        "dateutil",
        "pytz",
        "six",
        "xlsxwriter",
        "fitz",  # PyMuPDF
        "pymupdf",
        "pdfkit",
        "PIL.Image", # Pillow
        "cryptography",
        "cryptography.fernet",
        "cryptography.hazmat.backends",
        "cryptography.hazmat.primitives.asymmetric",
        "setuptools",
        "pkg_resources", # Common missing dependency
        "heartpy",
        "pyhrv",
        "pyhrv.time_domain",
        "pyhrv.frequency_domain",
        "pyhrv.nonlinear",
        "peakutils",
        "scipy",
        "scipy.signal",
        "scipy.optimize",
        "scipy.interpolate",
        "scipy.stats",
        "scipy.special",
        "matplotlib",
        "matplotlib.pyplot",
        "pandas",
        "serial",
        "PyQt5",
        "PyQt5.QtWebEngineWidgets",
        "PyQt5.QtPrintSupport",
        "cv2", # OpenCV
        "psutil",
        "requests",
        "packaging"
    ]
    
    # Windows-specific dependencies
    if sys.platform == "win32":
        clinical_stack.append("pywinusb.hid")
        clinical_stack.append("winreg")

    failed_modules = []
    
    print(f"Executing Audit on {len(clinical_stack)} clinical modules...")
    
    for module_name in clinical_stack:
        try:
            # Dynamically import the module
            __import__(module_name)
            print(f"[PASSED]: {module_name}")
        except ImportError as e:
            print(f"[FAILED]: {module_name} (Error: {e})")
            failed_modules.append((module_name, str(e)))
        except Exception as e:
            # Handle cases where sub-modules like matplotlib.pyplot might fail due to lack of display
            # during build-time checks, but are technically 'present'
            if "Display" in str(e) or "Tkinter" in str(e) or "environment" in str(e):
                print(f"[WARNING]: {module_name} (Present, but cannot initialize in build environment)")
            else:
                print(f"[ERROR]: {module_name} (Unexpected error: {e})")
                failed_modules.append((module_name, str(e)))

    print("------------------------------------------------")
    if not failed_modules:
        print("[SUCCESS] AUDIT COMPLETE: All clinical libraries are correctly bundled.")
        sys.exit(0)
    else:
        print(f"[FAILED] AUDIT FAILED: {len(failed_modules)} modules are missing or broken!")
        for mod, err in failed_modules:
            print(f"  -> {mod}: {err}")
        print("\nFATAL: Bundle validation failed. Build aborted to prevent deployment of broken software.")
        sys.exit(1)

if __name__ == "__main__":
    run_sanity_check()
