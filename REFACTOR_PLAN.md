# Refactor Plan - Pygame Solitaire

## Philosophy

This plan focuses on:
- **Bugs** that affect gameplay
- **Maintainability** issues that make adding features harder
- **Code clarity** improvements that reduce confusion

It does NOT focus on:
- Security
- Perfect test coverage

---

## Completed Work ✅

The following technical debt items have been resolved:

1. **✅ Removed Dual Undo/Redo Systems** - GameBoard now uses only UndoRedoManager
2. **✅ Removed Legacy Scoring System** - GameBoard now uses only ScoringEngine
3. **✅ Extracted Magic Numbers** - Added constants to constants.py for animations, UI layout, and rendering
4. **✅ Deleted Dead Code** - Removed deprecated methods, backward compatibility branches, and unused imports

All subsystems (GameBoard, ScoringEngine, UndoRedoManager, HintSystem, SaveLoadCoordinator) are now working correctly with the refactored architecture.

---

## Priority 0: Actual Bugs (Fix These)

### 1. Broken Move Count in Undo
**File:** `game_board.py:421-422`, `undo_redo_manager.py:71-73`

**Problem:** Comment says "We'll need to track this better" - undo decrements move_count even for stock draws that didn't increment it.

**Fix:**
```python
# In Move class
def __init__(self, ..., increments_move_count: bool = True):
    self.increments_move_count = increments_move_count

# When creating stock draw moves
move = Move(..., increments_move_count=False)

# In undo
if move.increments_move_count and self.game_state.move_count > 0:
    self.game_state.move_count -= 1
```

**Effort:** 30 minutes

---

### 2. Multiple display.flip() Per Frame
**File:** `renderer.py:178, 399, 470, 550`

**Problem:** Calling `pygame.display.flip()` in multiple render methods can cause screen tearing and wastes CPU.

**Fix:** Remove all flip() calls from Renderer methods, let main.py handle it:
```python
# main.py render() method
def render(self):
    if self.entering_name:
        self.renderer.render_name_entry(...)
    elif self.menu_state.is_in_game():
        self.renderer.render(...)
    else:
        self.renderer.render_menu(...)

    pygame.display.flip()  # Single flip at the end
```

**Effort:** 15 minutes

---

### 3. Auto-Finish Detection Too Conservative
**File:** `auto_finish.py:30-52`

**Problem:** Disables auto-finish if waste pile has any cards, even if those cards can't be played.

**Fix:** Add logic to check if waste card is actually playable:
```python
def check_available(self) -> bool:
    # All tableau cards must be face-up
    for tableau in self.game_state.tableaus:
        for card in tableau.cards:
            if not card.face_up:
                return False

    # Stock must be empty
    if self.game_state.stock.cards:
        return False

    # Waste can have cards if they can't be played
    if self.game_state.waste.cards:
        waste_card = self.game_state.waste.cards[-1]
        # Check if waste card can go anywhere
        for foundation in self.game_state.foundations:
            if foundation.can_accept(waste_card, self.game_state.waste):
                return False  # Still playable moves from waste
        for tableau in self.game_state.tableaus:
            if tableau.can_accept(waste_card, self.game_state.waste):
                return False  # Still playable moves from waste

    return True
```

**Effort:** 30 minutes

---

### 4. Hint Algorithm Highlights Bad Moves
**File:** `hint_system.py:26-77`

**Problem:** Returns ALL legal moves, including terrible ones (moving Kings to empty tableaus, moving foundationable cards to tableaus).

**Fix:** Add move scoring and filter:
```python
def _score_move(self, card, source, target) -> int:
    """Score move quality (higher = better)."""
    score = 0

    # Foundation moves are always good
    if isinstance(target, FoundationPile):
        score += 100

    # Revealing face-down cards is good
    if source.cards and source.cards[-1] == card and len(source.cards) > 1:
        if not source.cards[-2].face_up:
            score += 50

    # Moving to empty tableau only good for Kings
    if isinstance(target, TableauPile) and not target.cards:
        if card.rank == 'K':
            score += 30
        else:
            score -= 50  # Bad move

    # Tableau-to-tableau that doesn't reveal is low priority
    if isinstance(target, TableauPile) and target.cards:
        score += 10

    return score

def get_valid_moves(self) -> List[Tuple['Card', 'Pile', 'Pile']]:
    valid_moves = []
    # ... existing move generation ...

    # Filter to only good moves (score > 0)
    scored_moves = [(card, src, tgt, self._score_move(card, src, tgt))
                    for card, src, tgt in valid_moves]
    good_moves = [(c, s, t) for c, s, t, score in scored_moves if score > 0]

    return good_moves if good_moves else valid_moves  # Fallback to any move
```

**Effort:** 1 hour

---

## Priority 1: Technical Debt (Do Soon)

### 5. Break Up _render_settings() Method
**File:** `renderer.py:651-887` (237 lines!)

**Problem:** Unmaintainable mega-method.

**Fix:** Split into smaller methods:
```python
def _render_settings(self, ...):
    self._render_settings_header()
    self._render_background_swatches(current_bg)
    self._render_pile_outline_swatches()
    self._render_scoring_checkboxes(scoring_factors)
    self._render_purge_button()
    self._render_back_button()

def _render_color_swatches(self, options, current, y_offset, storage_key):
    """Generic method for rendering color swatches."""
    # Reusable logic for both background and pile colors
```

**Effort:** 1-2 hours

---

### 6. Fix Type Hints
**Files:** Multiple

**Changes:**
- `any` → `Any` (with proper import)
- Add missing return type hints
- Specify Dict/List contents: `Dict[str, int]` not just `Dict`

**Effort:** 1 hour

---

### 7. Add Logging Framework
**Files:** All files currently using `print()`

**Why:** Makes debugging game state issues WAY easier. You can see what happened before a bug without print statements everywhere.

**Setup:** Create `logger.py`:
```python
import logging
import sys
from pathlib import Path

def setup_logging(debug_mode: bool = False):
    """Initialize logging for the game."""
    log_dir = Path.home() / '.solitaire' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / 'game.log'

    # Configure root logger
    level = logging.DEBUG if debug_mode else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout) if debug_mode else logging.NullHandler()
        ]
    )

    # Reduce pygame noise
    logging.getLogger('pygame').setLevel(logging.WARNING)

    logging.info("="*60)
    logging.info("Game started")
    logging.info("="*60)
```

**Usage in modules:**
```python
import logging
logger = logging.getLogger(__name__)

# Replace print() calls:
# print(f"Undo successful! {self.move_count} moves, Score: {current_score}")
logger.info(f"Undo successful! {self.move_count} moves, Score: {current_score}")

# For debugging:
logger.debug(f"Checking if {card} can move from {source} to {target}")

# For errors:
try:
    move.execute()
except Exception as e:
    logger.error(f"Failed to execute move: {e}", exc_info=True)
```

**In main.py:**
```python
from logger import setup_logging

def main():
    setup_logging(debug_mode=False)  # Set True when debugging
    # ... rest of game
```

**Benefits:**
- Logs saved to `~/.solitaire/logs/game.log` (persistent across runs)
- Can review what happened before a crash
- Easy to enable/disable debug output
- Timestamps show when things happened
- Can grep logs for specific issues

**Effort:** 2-3 hours (setup + replacing print statements)

---

## Priority 2: Nice to Have (Future)

### 11. Add Bounds to Undo Stack
**File:** `undo_redo_manager.py`

**Why:** Prevent memory growth in very long sessions (10,000+ moves).

**Fix:** Add max history size (e.g., 1000 moves) with FIFO eviction.

**Effort:** 30 minutes

---

### 12. Cache Gradient Swatches in Settings Menu
**File:** `renderer.py:706-716`

**Why:** You already cache the main background gradient beautifully. Apply same technique to settings swatches.

**Effort:** 30 minutes

---

### 13. Improve Test Suite
**Files:** `test_phase1.py`, `test_undo_redo_detailed.py`

**Changes:**
- Adopt pytest framework
- Make tests deterministic (seed random or use fixtures)
- Add unit tests for Pile subclasses
- Test edge cases (empty history undo, etc.)

**Effort:** 4-8 hours (ongoing)

---

### 14. Split GameBoard Class
**File:** `game_board.py` (644 lines)

**Why:** It does too many things. Consider splitting into:
- `Board` (pile management)
- `MoveExecutor` (move logic)
- Keep save/load in `SaveLoadCoordinator`

**Effort:** 4-6 hours (big refactor)

---

### 15. Add Game State Validation
**File:** `save_load_coordinator.py`

**Why:** Detect corrupted saves early.

**Add:**
```python
def validate_game_state(self, game_state) -> bool:
    """Check game state is valid."""
    # All 52 cards exist
    all_cards = [card for pile in game_state.all_piles for card in pile.cards]
    if len(all_cards) != 52:
        return False

    # No duplicate cards
    card_ids = [(c.rank, c.suit) for c in all_cards]
    if len(card_ids) != len(set(card_ids)):
        return False

    return True
```

**Effort:** 1 hour

---

### 16. Move get_scoring_mode_name() Out of constants.py
**File:** `constants.py:66-84`

**Why:** Logic doesn't belong in constants module.

**Fix:** Move to `scoring_engine.py` as a method or to `utils.py`.

**Effort:** 15 minutes

---

### 17. Use Enums for Card Suits/Ranks
**File:** `card.py`

**Why:** Prevent invalid cards like `Card("banana", "invalid")`.

**Fix:**
```python
from enum import Enum

class Suit(Enum):
    HEARTS = 'hearts'
    DIAMONDS = 'diamonds'
    CLUBS = 'clubs'
    SPADES = 'spades'

class Rank(Enum):
    ACE = 'A'
    TWO = '2'
    # ... etc
```

**Effort:** 2 hours (touches many files)

---

### 18. Make UIState Required
**File:** `renderer.py`

**Why:** Remove all "if self.ui_state:" fallback code.

**Effort:** 30 minutes

---

### 19. Flatten Sage Advice JSON or Use Categories
**Files:** `sage_advice.py`, `data/sage_advice.json`

**Why:** Categories exist but aren't used. Either use them or flatten JSON to simple array.

**Effort:** 15 minutes

---

## Priority 3: Polish

- Add keyboard navigation in settings menu
- Replace emoji in code with text/icons
- Add .gitignore for .pyc files, __pycache__, etc.
- Add docstrings to modules (not just functions)
- Consider using `time.monotonic()` instead of `time.time()` for intervals
- Add proper `__repr__` methods to Card, Pile for debugging
- Consider click sound effects (you have the hooks already!)

---

## Suggested Order of Attack

**Completed (✅):**
- ✅ Extract magic numbers to constants.py
- ✅ Remove dual undo/redo systems
- ✅ Remove legacy scoring system
- ✅ Delete dead code and backward compatibility branches

**Next Up - Priority 0 (Bug Fixes):**
- Days 1-2: Fix P0 issues #1-4 (actual bugs)
  - Broken move count in undo
  - Multiple display.flip() per frame
  - Auto-finish detection too conservative
  - Hint algorithm highlights bad moves

**After Bugs - Priority 1 (Code Quality):**
- Days 1-2: Break up mega-methods (#5)
- Day 3: Fix type hints (#6)
- Days 4-5: Add logging framework (#7)

**Future - Priority 2/3 (Polish):**
- Pick P2/P3 items based on what annoys you most
- Focus on items that will help with adding puzzle features


---
