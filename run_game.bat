@echo off
REM Solitaire Game Launcher for Windows
REM This script checks for Python and pygame, installs pygame if needed, and runs the game

echo ========================================
echo    Klondike Solitaire Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Check if pygame is installed
echo Checking for pygame...
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo pygame not found. Installing pygame...
    echo.
    python -m pip install --upgrade pip
    python -m pip install pygame
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install pygame!
        echo Please try running: python -m pip install pygame
        echo.
        pause
        exit /b 1
    )
    echo.
    echo pygame installed successfully!
) else (
    echo pygame is already installed!
)

echo.
echo Starting game...
echo.
echo ========================================
echo.

REM Run the game
python main.py

REM Pause if there was an error
if errorlevel 1 (
    echo.
    echo ========================================
    echo The game encountered an error.
    echo ========================================
    pause
)
