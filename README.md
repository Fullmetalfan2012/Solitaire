# 🎴 Pygame Solitaire

A modern, feature-rich Klondike Solitaire game built with pygame, designed for extensibility and polish.

---

## ✨ Features

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

### Polish
- **80+ animal facts** for sage advice (cats, dogs, birds, mice themes!) 🐱🐶🐦🐭
- **Professional menus** with clickable UI
- **Comprehensive statistics tracking** across all scoring modes
- **Post-game arcade-style name entry** with score breakdown

---

## 🚀 Quick Start

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

## 🎮 Controls

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

## 📊 Scoring System

Customize your difficulty by toggling three independent scoring factors in Settings:

### Scoring Factors
- **⏱️ Time Bonus**: Rewards fast completion (15,000 base, decreases over time)
- **🎯 Move Penalty**: Penalizes inefficient play (deducts points per move)
- **💎 Move Values**: Awards points for cards moved to foundations

### Example Modes (8 Total Combinations)
- **All Enabled**: "Time + Moves + Values" (hardest, most competitive)
- **Two Factors**: "Time + Moves", "Time + Values", "Moves + Values"
- **One Factor**: "Time Only", "Moves Only", "Values Only"
- **None**: "Complete Only" (just track wins, no scoring pressure)

Each combination has its own separate leaderboard! Mix and match to find your perfect difficulty.

---

## 🏗️ Architecture

### Module Structure (11 core modules)

```
solitaire/
├── constants.py          # Configuration (positions, colors, scoring factors)
├── card.py              # Card data structure with ability hooks
├── pile.py              # Pile hierarchy (Stock, Waste, Foundation, Tableau)
├── move.py              # Move tracking for undo/redo (Command Pattern)
├── game_state.py        # Game logic orchestrator
├── input_handler.py     # Drag-and-drop with overlap detection
├── renderer.py          # All drawing logic
├── settings.py          # User settings persistence
├── stats.py             # Statistics tracking (per-mode leaderboards)
├── menu_state.py        # Menu navigation
└── main.py              # Game loop coordinator
```

### Key Design Patterns
- **Command Pattern**: Move tracking for unlimited undo/redo
- **Strategy Pattern**: Pile-based rules via `can_accept()`
- **Settings-Driven**: JSON persistence for user preferences
- **Separation of Concerns**: Clean module boundaries

---

## 📈 Development Phases

### ✅ Phase 1: Classic Solitaire (COMPLETE)
- Full Klondike implementation
- All standard rules
- Drag-and-drop mechanics
- Win detection

### ✅ Phase 2: Polish & Enhancement (COMPLETE)
**Phase 2.5 Additions:**
- Unlimited undo/redo system (Command Pattern)
- Toggle-based scoring (8 difficulty combinations)
- Per-mode separate leaderboards with purge functionality
- Auto-finish detection + smooth animations
- Card-based overlap snapping (1/3 threshold)
- Click-to-place for single-option moves
- Snap-back animations
- 80+ animal-themed sage advice facts
- 6 background color options (including gradients)
- Extended window size (1400×900) for long stacks
- Complete settings system with persistence

### 🔜 Phase 3: Special Abilities (PLANNED)
- Suit-based abilities (Hearts, Diamonds, Clubs, Spades)
- Rank-based abilities (Aces, Kings, etc.)
- Power-ups and special cards
- Modified base rules for increased difficulty
- Custom card artwork (animal-themed: cats, dogs, birds, mice)
- Stochastic fairness balancing

### 🔮 Phase 4: Advanced Features (FUTURE)
- Loss/unwinnable detection (NP-complete challenge!)
- Advanced animations (dealing, card flips)
- AI opponent / auto-solver
- Alternative variants (Spider, Freecell, Pyramid)

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)**: Project instructions for Claude Code (development history, architecture decisions)
- **[DEVELOPERS.md](DEVELOPERS.md)**: Comprehensive guide for modifying game mechanics and adding abilities
- **[PLAYTEST_INSTRUCTIONS.md](PLAYTEST_INSTRUCTIONS.md)**: Quick-start guide for playtesters

---

## 🧪 For Developers

### Adding Special Abilities (Phase 3)

Cards have built-in extension points:
```python
card.special_suit_ability = "hearts_heal"
card.special_rank_ability = "king_castle"
```

See [DEVELOPERS.md](DEVELOPERS.md) for step-by-step guides on:
- Implementing suit/rank abilities
- Modifying game rules
- Creating new pile types
- Extending the scoring system

### Tuning Scoring Modes

Edit `constants.py → SCORING_MODES`:
```python
'TMV': {
    'scale': 1.0,  # Adjust this to normalize scores
    'order': ['time', 'moves', 'value'],
    ...
}
```

### Performance Notes
- **Move tracking**: ~100 bytes per move (vs 3KB with deepcopy)
- **Overlap detection**: O(n) where n = number of piles (~13)
- **Target**: 60 FPS (achieved with smooth animations)

---

## 🎨 Asset Credits

- **Card rendering**: Placeholder graphics (PNG support ready)
- **Recommended card assets**: [Playing Cards by hanhaechi](https://github.com/hanhaechi/playing-cards)
- **Custom artwork**: Animal-themed cards (cats, dogs, birds, mice) coming in Phase 3!

---

## 🤝 Contributing

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

**Enjoy the game! 🎴✨**

*"Sometimes you win, sometimes you shuffle and deal again."*
