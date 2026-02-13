# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Klondike Solitaire game built with pygame using object-oriented programming. The project is designed with extensibility in mind.

**Current Status**: 0.2.7 COMPLETE!
**Recent Updates**: Auto-finish fixed, undo persistence working, pile color theming added, settings sync fixed
**Future Plans**: Polishing the game further. Turning this Solitaire clone into a fully-fledged puzzle game. 
				  Suit-based and rank-based special abilities, power-ups, creative game modes


## Design Principles

1. **Keep the modules maximally separate, implement glue modules to minimize interdependance.**
2. **Focus on extensibility and flexibility of core systems.**
3. **Reuse, what you can. If you need to design a new scoring system, check what was already built.**
4. **Don't be afraid of giving critical feedback and voicing your opinions and thoughts.**

## Architecture

### Core Design Pattern

The codebase uses a clean separation of concerns with 10 main modules:

1. **constants.py** - All configuration (screen size, positions, colors, FPS)
2. **card.py** - Card data structure with ability hooks
3. **pile.py** - Base Pile class + 4 subclasses implementing game rules
4. **game_state.py** - Game logic orchestrator (dealing, moves, win detection, save/load)
5. **input_handler.py** - Drag-and-drop state machine
6. **renderer.py** - All drawing logic (game, menus, overlays)
7. **main.py** - Main game loop coordinating all components
8. **menu_state.py** - Menu navigation and state management
9. **stats.py** - Statistics tracking and leaderboard (scores.jsonl)
10. **DEVELOPERS.md** - Comprehensive guide for modifying game mechanics

### Key Architectural Decisions

**Pile Hierarchy**: All pile types inherit from base `Pile` class. Each subclass implements `can_accept(card, source_pile)` to encode Solitaire rules. This makes rules explicit and testable.

```python
# TableauPile: descending rank, alternating colors
# FoundationPile: ascending rank, same suit, starts with Ace
# StockPile/WastePile: special drawing mechanics
```

**Card Extension Points**: The `Card` class has `special_suit_ability` and `special_rank_ability` properties (nullable) with corresponding `activate_*_ability()` methods. These are stubs ready for Phase 3 implementations.

**Image Loading**: Uses class-level cache in `Card.load_images()` - all 52 card images loaded once at startup, shared across instances. Gracefully falls back to placeholder rendering if PNGs missing.

**Drag State Management**: `InputHandler` maintains explicit state machine (idle → dragging → validate). Tracks `dragged_cards`, `source_pile`, `drag_offset`, and `original_positions` for canceling invalid moves.

### Game State Flow

```
GameState.initialize_game()
├─ Create all piles at fixed positions (from constants.py)
├─ Create 52-card deck
├─ Shuffle deck
└─ Deal Klondike-style (1-7 cards to tableau, rest to stock)

Move attempt:
InputHandler.handle_mouse_down() → start drag
InputHandler.handle_mouse_motion() → update positions
InputHandler.handle_mouse_up() → validate and execute/cancel
└─ GameState.try_move() → Pile.can_accept() → execute or reject
```

## Solitaire Rules Implementation

**Tableau Piles** (7 columns):
- Empty accepts only King
- Build down (descending rank) with alternating colors
- Can drag sequences of valid cards together
- Top card flips face-up when pile becomes empty

**Foundation Piles** (4, one per suit):
- Empty accepts only Ace
- Build up (ascending rank) within same suit (A→2→3...→K)
- Only single cards can be moved to foundation

**Stock/Waste**:
- Click stock to draw one card to waste
- When stock empty, click again to recycle waste back to stock
- Only top waste card is draggable

**Win Condition**: All 52 cards in foundation piles (13 per pile)

