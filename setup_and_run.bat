@echo off
cd /d "%~dp0"
title Gesture to Meme
color 0A

echo ========================================
echo       GESTURE TO MEME
echo ========================================
echo.
echo Current folder: %cd%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Download Python 3.11 from:
    echo https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
    echo.
    echo After installing, run this file again.
    echo.
    pause
    exit /b
)

echo [OK] Python found!
echo.

REM Check if meme_gesture.py exists
if not exist "meme_gesture.py" (
    echo [ERROR] meme_gesture.py not found!
    echo Make sure this file is in the same folder as this batch file.
    echo.
    pause
    exit /b
)

REM Create virtual environment if needed
if not exist "gesture_env\" (
    echo First time setup - Creating virtual environment...
    python -m venv gesture_env
    echo.
    echo Installing packages...
    call gesture_env\Scripts\activate.bat
    pip install mediapipe==0.10.9 opencv-python==4.9.0.80 numpy==1.26.4
    echo.
    echo Setup complete!
    echo.
) else (
    echo Loading environment...
    call gesture_env\Scripts\activate.bat
)

echo.
echo ========================================
echo    STARTING GESTURE TO MEME
echo ========================================
echo.
echo Make a gesture and hold it!
echo Press 'q' to quit.
echo.

python meme_gesture.py

echo.
echo Program finished.
pause