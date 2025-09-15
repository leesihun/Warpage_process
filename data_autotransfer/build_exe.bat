@echo off
echo Building Data Auto Transfer System Executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is available
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Install dependencies if not already installed
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may not have installed correctly
    echo Continuing with build...
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "DataAutoTransfer.exe" del "DataAutoTransfer.exe"

REM Build the executable
echo Building executable...
python -m PyInstaller data_autotransfer.spec --clean --noconfirm

REM Check if build was successful
if exist "dist\DataAutoTransfer.exe" (
    echo.
    echo ===============================================
    echo BUILD SUCCESSFUL!
    echo ===============================================
    echo.
    echo Executable created: dist\DataAutoTransfer.exe
    echo.
    echo To use the executable:
    echo 1. Copy dist\DataAutoTransfer.exe to your desired location
    echo 2. Copy config.txt to the same directory as the exe
    echo 3. Edit config.txt with your settings
    echo 4. Run: DataAutoTransfer.exe --test
    echo.
    echo For help: DataAutoTransfer.exe --help
    echo.
    
    REM Copy config.txt to dist folder
    copy "config.txt" "dist\" >nul 2>&1
    echo Config file copied to dist folder.
    echo.
    
) else (
    echo.
    echo ===============================================
    echo BUILD FAILED!
    echo ===============================================
    echo.
    echo Check the output above for errors.
    echo Common issues:
    echo - Missing dependencies
    echo - Python version compatibility
    echo - Insufficient disk space
    echo.
)

pause