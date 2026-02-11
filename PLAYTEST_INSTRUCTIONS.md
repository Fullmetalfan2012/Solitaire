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

### Basic Controls
- **Mouse Drag**: Drag cards to move them
- **Click**: Click cards with only one valid move to auto-place them!
- **Stock pile (top left)**: Click to draw cards
- **ESC**: Pause menu (during game) / Back (in menus)
- **↑↓ / Mouse**: Navigate menus
- **Enter / Click**: Select menu option

### Helpful Features
- **H**: Show hint (3 hints per game - use wisely!)
- **A**: Get sage advice (unlimited animal wisdom! 🐱🐶🐦🐭)
- **U**: Undo move (unlimited undo!)
- **Ctrl+Y**: Redo move
- **F**: Auto-finish (when all cards are revealed)
- **R**: Reset/new game

### New in Phase 2!
- **Unlimited Undo/Redo**: Make mistakes? No problem! Undo as much as you want!
- **Smart Snapping**: Cards snap when overlapping 1/3 with a pile - much more forgiving!
- **Click-to-Place**: Click cards that have only one valid move - they'll go there automatically!
- **Auto-Finish**: When all cards are face-up, press F to watch them fly to foundations automatically!
- **Customizable Difficulty**: Toggle Time/Moves/Values scoring independently - 8 combinations!
- **Beautiful Backgrounds**: Pick your favorite color scheme in Settings!
- **Leaderboard Purge**: Clear all scores to start fresh with the new scoring system!

---

## What to Test & Report

Please play a few games and help us test these features:

### Core Gameplay
1. **Bugs**: Anything that crashes, freezes, or behaves strangely
2. **Drag & Drop**: Is it smooth? Does the card snapping feel natural?
3. **Balance**: Does the scoring feel fair? Too easy/hard?

### NEW Phase 2 Features to Test!

**Undo/Redo:**
- [ ] Try undoing many moves (it's unlimited!)
- [ ] Redo moves with Ctrl+Y
- [ ] Make a new move - redo history should clear
- Does unlimited undo make the game too easy?

**Click-to-Place:**
- [ ] Click an Ace - it should go to foundation automatically
- [ ] Click cards with only one valid move
- Does this feel smooth or confusing?

**Auto-Finish:**
- [ ] Play until all cards are face-up and stock is empty
- [ ] Press F to trigger auto-finish
- [ ] Watch the animation - does it look good?

**Snapping System:**
- [ ] Drag cards near pile edges - do they snap when they should?
- [ ] Try releasing cards halfway over a pile
- Is the 1/3 overlap threshold good, or should it be more/less forgiving?

**Scoring Factors (NEW!):**
- [ ] Go to Settings, toggle different scoring factors on/off
- [ ] Try "Time + Moves" (disable Values) - does it feel different?
- [ ] Try "Values Only" (disable Time and Moves) - more strategic?
- [ ] Try "Complete Only" (disable all) - just track wins
- [ ] Play games and check scores save to correct mode-specific leaderboards
- [ ] Use "Clear All Scores" button to purge leaderboards
- Do the 8 different combinations feel meaningfully different?
- Which is your favorite mode?

**Backgrounds:**
- [ ] Try different background colors in Settings
- [ ] Check out the gradients!
- Which is your favorite?

**Sage Advice:**
- [ ] Press A a bunch of times
- [ ] Do the animal facts make you smile? 🐱
- Want more variety?

### Fun Factor
- What feels **great**? What's **frustrating**?
- Which new features do you use most?
- Any features you never use?
- What would make the game more fun?

---

## Troubleshooting

**"Python is not installed or not in PATH"**
- Windows: Reinstall Python and make sure to check "Add Python to PATH"
- Mac/Linux: Python 3 should be pre-installed, try running `python3 --version` in Terminal

**"Failed to install pygame"**
- Try manually: `python -m pip install pygame` (Windows) or `python3 -m pip install pygame` (Mac/Linux)
- On Linux, you may need: `sudo apt install python3-pygame`

**Game window is too small/large**
- The game runs at 1400x900 (optimized for long card stacks!)
- If it doesn't fit your screen, let us know your resolution!

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
