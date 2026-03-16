@echo off
echo ===================================================
echo   Kodys Foot Clinik V2 - Windows Build Automation  
echo ===================================================

:: Ensure python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b
)

:: Step 1: Create and activate virtual environment
echo.
echo [Step 1] Setting up virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

:: Step 2: Install dependencies
echo.
echo [Step 2] Installing project requirements and PyInstaller...
pip install -r requirements.txt
pip install pyinstaller

:: Step 3: Run PyInstaller to create the Windows .exe
echo.
echo [Step 3] Compiling application using PyInstaller...
python -m PyInstaller --noconfirm --onedir --windowed --name "Kodys Foot Clinik" ^
  --add-data "app_config;app_config" ^
  --add-data "kodys;kodys" ^
  --add-data "app_assets;app_assets" ^
  --add-data "config;config" ^
  --add-data "db.sqlite3;." ^
  --add-data "wkhtmltopdf;wkhtmltopdf" ^
  --hidden-import "PyQt5.QtWebEngineWidgets" ^
  --hidden-import "PyQt5.QtPrintSupport" ^
  --hidden-import "cv2" ^
  --hidden-import "pywinusb.hid" ^
  --hidden-import "setuptools" ^
  --hidden-import "distutils" ^
  --hidden-import "fitz" ^
  --hidden-import "pymupdf" ^
  application_code\run.py

if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller compilation failed.
    pause
    exit /b
)

:: Step 4: Run Inno Setup Compiler
echo.
echo [Step 4] Bundling the compiled code into an Installer via Inno Setup...
:: Assumes Inno Setup is installed in its default location
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if exist %INNO_PATH% (
    %INNO_PATH% application_code\kodys_inno_setup.iss
    echo.
    echo ===================================================
    echo   BUILD SUCCESSFUL!                              
    echo   Installer generated successfully.              
    echo ===================================================
) else (
    echo.
    echo [WARNING] Inno Setup compiler (ISCC.exe) not found at %INNO_PATH%.
    echo Please install Inno Setup or compile the .iss script manually using the GUI.
)

pause
