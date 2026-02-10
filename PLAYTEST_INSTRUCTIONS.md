# 🎴 Solitaire Playtest Instructions

Thank you for helping test this game! This guide will get you up and running in just a few minutes.

## Quick Start (One-Time Setup)

### Step 1: Install Python (If You Haven't Already)

**Windows:**
1. Download Python from: https://www.python.org/downloads/
2. Run the installer
3. ⚠️ **IMPORTANT**: Check the box that says "Add Python to PATH" before clicking Install!

**Mac:**
1. Open Terminal
2. Install Homebrew if you don't have it: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
3. Install Python: `brew install python3`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Run the Game!

**Windows:**
- Double-click `run_game.bat`
- That's it! The script will automatically install pygame if needed and launch the game.

**Mac/Linux:**
- Double-click `run_game.sh` (or run `./run_game.sh` in Terminal)
- If double-clicking doesn't work, open Terminal in this folder and run: `./run_game.sh`

---

## Game Controls

- **Mouse**: Click and drag cards to move them
- **Stock pile (top left)**: Click to draw cards
- **H**: Show hint (3 hints per game - use wisely!)
- **A**: Get sage advice (unlimited strategic tips)
- **U**: Undo last move (up to 3 moves back)
- **R**: Reset/new game
- **ESC**: Pause menu (during game) / Back (in menus)
- **↑↓ / Mouse**: Navigate menus
- **Enter / Click**: Select menu option

---

## What to Test & Report

Please play a few games and note:

1. **Bugs**: Anything that crashes, freezes, or behaves strangely
2. **Balance**: Does the scoring feel fair? Too easy/hard?
3. **Controls**: Are the drag-and-drop mechanics smooth?
4. **Hints**: Are they helpful? Too revealing or not enough?
5. **Fun Factor**: What feels good? What's frustrating?

---

## Troubleshooting

**"Python is not installed or not in PATH"**
- Windows: Reinstall Python and make sure to check "Add Python to PATH"
- Mac/Linux: Python 3 should be pre-installed, try running `python3 --version` in Terminal

**"Failed to install pygame"**
- Try manually: `python -m pip install pygame` (Windows) or `python3 -m pip install pygame` (Mac/Linux)
- On Linux, you may need: `sudo apt install python3-pygame`

**Game window is too small/large**
- The game runs at 1024x768 by default
- This will be configurable in settings soon!

**Game runs slowly**
- Make sure no other heavy programs are running
- The game requires pygame and a decent GPU

---

## Sending Feedback

Please send:
- Your operating system (Windows/Mac/Linux)
- Any error messages you see
- Screenshots of bugs (if applicable)
- Your high score! 🎉

Thank you for playtesting! Your feedback makes this game better! 💙
