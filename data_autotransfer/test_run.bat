@echo off
echo Testing DataAutoTransfer.exe with new paramiko SSH implementation...
echo.
echo ==================================================
echo TEST 1: Help command
echo ==================================================
DataAutoTransfer.exe --help
echo.

echo ==================================================
echo TEST 2: Connection test (will attempt SSH to configured server)
echo ==================================================
DataAutoTransfer.exe --test
echo.

echo ==================================================
echo TEST 3: Dry run transfer
echo ==================================================
DataAutoTransfer.exe --dry-run --once
echo.

echo ==================================================
echo Tests completed. Check output above for any errors.
echo ==================================================
pause