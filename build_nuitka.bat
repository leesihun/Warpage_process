@echo off
echo Building PEMTRON Warpage Tool with Nuitka...

REM Simple Nuitka build for Python 3.13
python -c "
import sys
print('Python version:', sys.version)
if sys.version_info < (3, 13):
    print('Recommended: Use Python 3.12 for better Nuitka compatibility')
"

echo.
echo Option 1: Try Nuitka (may fail with Python 3.13)
echo python -m nuitka --standalone --onefile --assume-yes-for-downloads --output-filename=PEMTRON_Warpage_Tool.exe --output-dir=dist --include-data-dir=templates=templates --include-data-dir=data=data --windows-console-mode=attach --msvc=latest --follow-imports --remove-output web_server.py

echo.
echo Option 2: Use PyInstaller (recommended for Python 3.13)
echo python -m PyInstaller web_server.spec --clean

echo.
echo Note: Nuitka may not fully support Python 3.13 yet
echo Consider downgrading to Python 3.12 or using PyInstaller

pause