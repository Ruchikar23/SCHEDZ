@echo off
setlocal
title SCHEDZ Launcher
cd /d "%~dp0"

:: If run from the parent directory, navigate to the SCHEDZ folder
if exist "SCHEDZ\main.py" cd /d "%~dp0SCHEDZ"

:: Verify Python is available
where python >nul 2>&1
if errorlevel 1 goto :NO_PYTHON

echo Starting SCHEDZ Application...
python main.py
if errorlevel 1 goto :APP_ERROR
goto :EOF

:NO_PYTHON
echo ========================================================
echo   [ERROR] Python was not found in your system PATH.
echo   Please install Python 3.8 or newer from https://python.org
echo   Make sure to check "Add Python to PATH" during installation.
echo ========================================================
pause
exit /b 1

:APP_ERROR
echo.
echo [NOTICE] SCHEDZ encountered an issue or closed with an error.
pause
exit /b 1
