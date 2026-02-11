# CHANGELOG

## Phase 2.7 - Bug Fixes & Polish (February 11, 2026)

### 🐛 Bug Fixes
- **Fixed auto-finish crash** - Game no longer crashes when using auto-finish feature
- **Fixed difficulty toggles** - Scoring factor checkboxes now update immediately
- **Fixed undo after reload** - Undo history now persists when saving/loading games
- **Fixed settings sync** - All settings changes now apply in real-time

### ✨ New Features
- **Empty pile color theming** - Choose from 5 colors for empty pile outlines
  - Options: Green, White, Gold, Blue, Red
  - Accessible in Settings menu
  - Auto-adjusts label brightness for readability

### 🎨 Visual Improvements
- Empty pile labels now theme-aware
- Settings menu reorganized with new pile color section
- Better visual feedback throughout UI

### 🔧 Technical Improvements
- Move history serialization rewritten for reliability
- Settings system more robust
- Backward compatible with old save files

---

## Phase 2.6 - Toggle-Based Scoring (February 11, 2026)

### ✨ New Features
- **Scoring factor toggles** - Mix and match scoring components
  - Enable/disable: Time Bonus, Move Penalty, Move Values
  - 8 possible combinations (2³)
  - Separate leaderboards per mode
- **Clear all scores button** - Fresh start option in settings

### 🎨 Visual Improvements
- Checkbox UI for scoring factors
- Dynamic mode naming ("Time + Moves", "Values Only", etc.)
- Visual checkmarks for enabled factors

### 💔 Breaking Changes
- Old scoring modes (TMV, TVM, etc.) deprecated
- Players should clear old scores via settings menu

---

## Phase 2.5 - Launcher Scripts (February 11, 2026)

### ✨ New Features
- **Windows launcher** (`run_game.bat`) - Double-click to play
- **Linux/Mac launcher** (`run_game.sh`) - One command to install & run
- **Playtester instructions** - Complete setup guide for non-technical users

### 🔧 Technical Improvements
- Auto-installs pygame if missing
- Friendly error messages
- Cross-platform support

---

## Phase 2.0 - Full-Featured Game (February 9, 2026)

### ✨ New Features
- **Real-time scoring** - Time bonus, move penalty, move values
- **Post-win screen** - Arcade-style name entry
- **High scores leaderboard** - Persistent score tracking
- **Undo/redo system** - Up to 3 moves back
- **Hint system** - 3 tactical hints + unlimited sage advice
- **Full menu system** - Main menu, pause, settings, high scores
- **Save/load** - Continue games later
- **Statistics tracking** - Complete game history

### 🎨 Visual Improvements
- Pile labels for empty piles
- Accurate hitboxes
- Background themes (6 options)
- No screen flicker
- Polished UI throughout

### 🔧 Technical Improvements
- State snapshot system
- Configurable scoring
- JSON-based save files
- Backward compatible settings

---

## Phase 1.0 - MVP (February 9, 2026)

### ✨ Initial Release
- Classic Klondike Solitaire rules
- Drag-and-drop mechanics
- Win detection
- Game reset
- 7 tableau piles, 4 foundations
- Stock/waste pile mechanics

### 🎨 Visual Features
- PNG card images (or placeholder rendering)
- Green felt background
- Clean UI

---

## Upcoming Features (Phase 3)

### 🔮 Planned
- **Special card abilities** - Suit-based and rank-based powers
- **Custom game modes** - Creative rule variations
- **Enhanced animations** - Card flips, win celebrations
- **Sound effects** - Optional audio feedback
- **More polish** - Based on playtester feedback!

---

## Known Issues

None currently! All reported bugs have been fixed. 🎉

If you find any issues, please report them to Ferdi with:
1. What you were doing when it happened
2. What you expected to happen
3. What actually happened
4. Any error messages shown

---

## Thanks

Massive thanks to all playtesters who helped make this game better! Your feedback drives development. 💙

**Development Team:**
- Ferdi (Lead Developer, Game Designer)
- Claude #1 (MVP Architecture & Implementation)
- Claude #2 (Phase 2 Features & Polish)
- Claude #3 (Launcher Scripts & Accessibility)
- Claude #4 (Scoring System Redesign)
- Claude #5 (Bug Fixes & Code Review)

This is a labor of love. Keep the feedback coming! 🎴✨
