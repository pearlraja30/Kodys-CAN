#!/bin/bash
echo "==================================================="
echo "   Kodys Foot Clinik V2 - macOS Build Automation   "
echo "==================================================="

# Step 1: Check Python
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 is not installed."
    exit 1
fi

# Step 2: Clean previous builds
echo ""
echo "[Step 0] Cleaning previous build artifacts..."
rm -rf build dist .venv_mac

# Step 3: Set up Virtual Environment
echo ""
echo "[Step 1] Setting up virtual environment..."
python3 -m venv .venv_mac
source .venv_mac/bin/activate

# Step 3: Install Dependencies
echo ""
echo "[Step 2] Installing requirements..."
python3 -m pip install --upgrade pip setuptools==69.0.3 wheel
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller packaging

# Step 4: Run PyInstaller
echo ""
echo "[Step 3] Compiling application into a .app bundle..."
# Note: Using : instead of ; for paths on Mac
python3 -m PyInstaller --noconfirm --onedir --windowed \
    --osx-bundle-identifier "com.kodys.can" \
    --add-data "app_config:app_config" \
    --add-data "kodys:kodys" \
    --add-data "app_assets:app_assets" \
    --add-data "config:config" \
    --add-data "db.sqlite3:." \
    --name "KodysCAN" \
    --hidden-import "PyQt5.QtWebEngineWidgets" \
    --hidden-import "PyQt5.QtPrintSupport" \
    --hidden-import "cv2" \
    --hidden-import "setuptools" \
    --hidden-import "distutils" \
    --hidden-import "fitz" \
    --hidden-import "pymupdf" \
    --hidden-import "cryptography.fernet" \
    --hidden-import "cryptography.hazmat.backends" \
    --hidden-import "pkg_resources" \
    --hidden-import "heartpy" \
    --hidden-import "pyhrv" \
    --hidden-import "pyhrv.time_domain" \
    --hidden-import "pyhrv.frequency_domain" \
    --hidden-import "pyhrv.nonlinear" \
    --hidden-import "peakutils" \
    --hidden-import "scipy.signal" \
    --hidden-import "scipy.optimize" \
    --hidden-import "scipy.interpolate" \
    --hidden-import "scipy.stats" \
    --hidden-import "matplotlib" \
    --hidden-import "matplotlib.pyplot" \
    --hidden-import "pandas" \
    --hidden-import "serial" \
    --hidden-import "xlsxwriter" \
    --hidden-import "pdfkit" \
    --hidden-import "requests" \
    --hidden-import "psutil" \
    --hidden-import "biosppy" \
    --hidden-import "django.contrib.admin" \
    --hidden-import "django.contrib.auth" \
    --hidden-import "django.contrib.contenttypes" \
    --hidden-import "django.contrib.sessions" \
    --hidden-import "django.contrib.messages" \
    --hidden-import "django.contrib.staticfiles" \
    --collect-all "heartpy" \
    --collect-all "pyhrv" \
    --collect-all "biosppy" \
    --collect-all "xlsxwriter" \
    --collect-all "pdfkit" \
    --collect-all "pkg_resources" \
    --collect-all "setuptools" \
    --copy-metadata "setuptools" \
    --copy-metadata "heartpy" \
    application_code/run.py

if [ $? -eq 0 ]; then
    echo ""
    echo "[Step 4] Running Full-Spectrum Clinical Audit (v7.0)..."
    export PYTHONPATH="dist/KodysCAN.app/Contents/MacOS:dist:application_code"
    python3 application_code/sanity_check.py
    if [ $? -ne 0 ]; then
        echo ""
        echo "[FATAL] CLINICAL BUNDLE AUDIT FAILED!"
        echo "Missing modules detected. Build aborted."
        exit 1
    fi
    echo "[SUCCESS] Audit passed. All clinical modules verified in the .app bundle."

    echo ""
    echo "[Step 5] Ad-Hoc Code Signing for integrity with Hardened Runtime..."
    codesign --force --options runtime --deep --sign - "dist/KodysCAN.app"
    
    echo ""
    echo "==================================================="
    echo "   BUILD SUCCESSFUL!                              "
    echo "   The application can be found in dist/KodysCAN.app"
    echo "==================================================="
else
    echo "[ERROR] Build failed."
fi
