# Pygame Solitaire

A Klondike Solitaire game built with pygame, designed for extensibility and polish.

---

## Features

### Core Gameplay
- **Classic Klondike Solitaire** with all traditional rules
- **Smooth drag-and-drop** with intelligent card-based snapping (1/3 overlap threshold)
- **Click-to-place** for single-option moves - speeds up obvious plays!
- **Real-time scoring** with multiple components (time, moves, card value)

### Quality of Life
- **Unlimited undo/redo** - experiment freely! (U to undo, Ctrl+Y to redo)
- **Auto-finish detection** - when all cards are revealed, press F to watch them fly home!
- **Smart hint system** - 3 strategic hints per game + unlimited sage advice
- **Smooth snap-back animations** - cards gracefully return when dropped in invalid spots
- **Save/load** - pause and resume your game anytime

### Customization
- **Toggle-based difficulty** - Enable/disable Time, Moves, and Values scoring independently (8 combinations!)
- **Separate leaderboards** - Each scoring combination tracks its own high scores
- **6 background styles** - classic green, blue, grey, plus 3 beautiful gradients
- **Leaderboard management** - Purge all scores to start fresh
- **Persistent settings** - your preferences saved automatically


---

## Quick Start

### Running the Game

**Windows:**
```bash
# Double-click run_game.bat, or:
python main.py
```

**Mac/Linux:**
```bash
# Double-click run_game.sh, or:
./run_game.sh
# Or directly:
python3 main.py
```

The launcher scripts automatically install pygame if needed!

### Requirements
- Python 3.8+ (Python 3.13 recommended)
- pygame 2.6+ (auto-installed by launcher scripts)

### Manual Installation
```bash
pip install pygame
python main.py
```

---

## Controls

### Gameplay
- **Mouse Drag**: Move cards
- **Click**: Auto-place cards with single valid destination
- **Stock (top-left)**: Click to draw cards
- **U**: Undo (unlimited!)
- **Ctrl+Y**: Redo
- **F**: Auto-finish (when available)
- **H**: Hint (3 per game)
- **A**: Sage advice (unlimited animal wisdom!)
- **R**: New game
- **ESC**: Pause menu

### Menus
- **Arrow Keys / Mouse**: Navigate
- **Enter / Click**: Select
- **ESC**: Back

---

## Scoring System

Customize your difficulty by toggling three independent scoring factors in Settings:

### Scoring Factors
- **Time Bonus**: Rewards fast completion (15,000 base, decreases over time)
- **Move Penalty**: Penalizes inefficient play (deducts points per move)
- **Move Values**: Awards points for cards moved to foundations

### Example Modes (8 Total Combinations)
- **All Enabled**: "Time + Moves + Values" (hardest, most competitive)
- **Two Factors**: "Time + Moves", "Time + Values", "Moves + Values"
- **One Factor**: "Time Only", "Moves Only", "Values Only"
- **None**: "Complete Only" (just track wins, no scoring pressure)

Each combination has its own separate leaderboard! Mix and match to find your perfect difficulty.

## Asset Credits

- **Card assets**: [Playing Cards by hanhaechi](https://github.com/hanhaechi/playing-cards)

---

## Contributing

This is a personal learning project, but feedback is always welcome!

**Playtesting**: Run the game, play a few rounds, and report:
- Bugs or crashes
- Balance issues (is it too easy/hard?)
- UX friction (what feels awkward?)
- Feature requests

See [PLAYTEST_INSTRUCTIONS.md](PLAYTEST_INSTRUCTIONS.md) for detailed testing guide.

---

## 📝 License

Personal project - all rights reserved. Feel free to learn from the code!

---

## 🌟 Acknowledgments

Built with love, pygame, and a lot of iterative development. Special thanks to:
- Claude Code (AI pair programming partner)
- Playtesting friends providing invaluable feedback
- The pygame community

---

**Enjoy the game!**

*"Sometimes you win, sometimes you shuffle and deal again."*
