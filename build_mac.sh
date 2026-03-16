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

# Step 2: Set up Virtual Environment
echo ""
echo "[Step 1] Setting up virtual environment..."
python3 -m venv .venv_mac
source .venv_mac/bin/activate

# Step 3: Install Dependencies
echo ""
echo "[Step 2] Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Step 4: Run PyInstaller
echo ""
echo "[Step 3] Compiling application into a .app bundle..."
# Note: Using : instead of ; for paths on Mac
python3 -m PyInstaller --noconfirm --onedir --windowed \
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
    application_code/run.py

if [ $? -eq 0 ]; then
    echo ""
    echo "[Step 4] Ad-Hoc Code Signing for integrity..."
    codesign --force --deep --sign - "dist/KodysCAN.app"
    
    echo ""
    echo "==================================================="
    echo "   BUILD SUCCESSFUL!                              "
    echo "   The application can be found in dist/KodysCAN.app"
    echo "==================================================="
else
    echo "[ERROR] Build failed."
fi
