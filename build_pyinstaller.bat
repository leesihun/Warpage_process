@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo Building PEMTRON Warpage Tool with PyInstaller
echo ========================================
echo.

set "PROJECT_ROOT=%~dp0"
pushd "%PROJECT_ROOT%" >nul 2>&1

REM Ensure Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python executable not found in PATH.
    echo         Please install Python 3.12+ and ensure it is added to PATH.
    goto :END
)

for /f "tokens=*" %%p in ('python --version 2^>^&1') do set "PY_VER=%%p"
echo Detected !PY_VER!

REM Check PyInstaller availability
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed in the current Python environment.
    echo         Install it with: pip install pyinstaller
    goto :END
)

set "OUTPUT_DIR=dist"
set "OUTPUT_NAME=PEMTRON_Warpage_Tool.exe"
set "BUILD_LOG=%OUTPUT_DIR%\pyinstaller_build.log"

if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

echo.
echo Cleaning previous build artifacts...
if exist "%OUTPUT_DIR%\%OUTPUT_NAME%" del /f /q "%OUTPUT_DIR%\%OUTPUT_NAME%" >nul 2>&1
if exist "build" rd /s /q "build" >nul 2>&1

echo.
echo Starting PyInstaller build... (log: %BUILD_LOG%)
echo This may take several minutes depending on your system.
echo.

python -m PyInstaller PEMTRON_Warpage_Tool.spec --clean --noconfirm >"%BUILD_LOG%" 2>&1

set "BUILD_EXIT=!ERRORLEVEL!"

if !BUILD_EXIT! NEQ 0 (
    echo.
    echo ========================================
    echo BUILD FAILED! See %BUILD_LOG% for details.
    echo ========================================
    powershell -Command "if(Test-Path '%BUILD_LOG%'){ $matches = Select-String -Path '%BUILD_LOG%' -SimpleMatch 'Error','ERROR','Traceback'; if($matches){ $matches | Select-Object -First 10; exit 0 } else { exit 1 } } else { exit 1 }"
    set "HAS_ERRORS=!ERRORLEVEL!"
    if !HAS_ERRORS! NEQ 0 (
        echo (No explicit errors detected in log preview.)
    ) else (
        echo ----- Error Snippet (tail) -----
        powershell -Command "if(Test-Path '%BUILD_LOG%'){Get-Content -Path '%BUILD_LOG%' -Tail 40}"
        echo ---------------------------------
    )
    goto :END
)

echo.
if exist "%OUTPUT_DIR%\%OUTPUT_NAME%" (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Executable created at: %OUTPUT_DIR%\%OUTPUT_NAME%
    echo.
    echo To test the executable:
    echo 1. Navigate to the dist folder
    echo 2. Run %OUTPUT_NAME%
    echo 3. Your browser should open http://localhost:9410072 automatically
    echo.
) else (
    echo [WARNING] Build finished but executable not found. Check %BUILD_LOG%.
)

:END
popd >nul 2>&1
echo.
pause