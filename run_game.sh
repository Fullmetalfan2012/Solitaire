#!/bin/bash
# Solitaire Game Launcher for Linux/Mac
# This script checks for Python and pygame, installs pygame if needed, and runs the game

echo "========================================"
echo "   Klondike Solitaire Launcher"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python 3:"
    echo "  - On Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  - On macOS: brew install python3"
    echo "  - Or visit: https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python found!"
python3 --version
echo ""

# Check if pygame is installed
echo "Checking for pygame..."
if ! python3 -c "import pygame" &> /dev/null; then
    echo "pygame not found. Installing pygame..."
    echo ""
    python3 -m pip install --upgrade pip
    python3 -m pip install pygame

    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install pygame!"
        echo "Please try running: python3 -m pip install pygame"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo ""
    echo "pygame installed successfully!"
else
    echo "pygame is already installed!"
fi

echo ""
echo "Starting game..."
echo ""
echo "========================================"
echo ""

# Run the game
python3 main.py

# Check if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "The game encountered an error."
    echo "========================================"
    read -p "Press Enter to exit..."
fi
