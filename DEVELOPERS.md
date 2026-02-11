# Developer Documentation - Pygame Solitaire

**For developers modifying game mechanics, adding abilities, and extending the game.**

This guide is optimized for developers working on Phase 3 (special abilities) and beyond. It explains the architecture, patterns, and best practices that make this codebase maintainable and extensible.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Adding Special Abilities](#adding-special-abilities)
3. [Modifying Game Rules](#modifying-game-rules)
4. [Creating New Pile Types](#creating-new-pile-types)
5. [Extending the Scoring System](#extending-the-scoring-system)
6. [State Management](#state-management)
7. [UI and Rendering](#ui-and-rendering)
8. [Common Patterns](#common-patterns)
9. [Testing Your Changes](#testing-your-changes)

---

## Architecture Overview

### Module Structure

The codebase is organized into 11 core modules plus supporting files:

```
solitaire/
├── constants.py          # All configuration values (colors, positions, scoring factors)
├── card.py              # Card data structure with ability hooks
├── pile.py              # Pile hierarchy (4 types: Stock, Waste, Foundation, Tableau)
├── move.py              # Move tracking for undo/redo (Command Pattern)
├── game_state.py        # Game logic orchestrator
├── input_handler.py     # Drag-and-drop with overlap detection
├── renderer.py          # All drawing logic (game, menus, animations)
├── settings.py          # User settings persistence (background, scoring factors)
├── main.py              # Game loop coordinator
├── menu_state.py        # Menu navigation
└── stats.py             # Statistics tracking (per-mode leaderboards)
```

### Design Philosophy

**Separation of Concerns**: Each module has a single, clear responsibility. Game logic never touches rendering. Rendering never modifies game state.

**Pile-Based Rules**: Game rules are encoded in pile classes via `can_accept()`. This makes rules explicit, testable, and modifiable.

**Move Tracking (Command Pattern)**: The undo/redo system uses lightweight Move objects instead of state snapshots. Each move knows how to execute and undo itself. This enables unlimited undo/redo, smaller save files, and future replay functionality.

**Settings-Driven Behavior**: Game configuration (background color, scoring mode) is stored in `settings.py` and persisted to JSON. This makes the game customizable without code changes.

**Extension Points**: The Card class has `special_suit_ability` and `special_rank_ability` properties specifically designed for Phase 3.

---

## Phase 2 Systems (Current Features)

### Unlimited Undo/Redo System

**Architecture**: Command Pattern with move tracking
- Each move is stored as a lightweight `Move` object (~100 bytes)
- `move_history` stores all moves, `current_move_index` tracks position
- Undo: decrement index, call `move.undo()`
- Redo: increment index, call `move.execute()`
- New moves clear any "future" redo history

**Memory**: 33-66x less memory than deepcopy snapshots (was 3KB per state, now 100 bytes per move)

**Key Files**: `move.py`, `game_state.py` (undo/redo methods)

### Toggle-Based Scoring System

**Architecture**: Players independently enable/disable three scoring factors:
- **Time Bonus**: Rewards fast completion (15,000 base minus elapsed time)
- **Move Penalty**: Penalizes inefficient play (points deducted per move)
- **Move Values**: Awards points for cards moved to foundations

**8 Possible Modes** (2³ combinations):
- All three enabled: "Time + Moves + Values" (hardest, highest scores)
- Two enabled: "Time + Moves", "Time + Values", "Moves + Values"
- One enabled: "Time Only", "Moves Only", "Values Only"
- None enabled: "Complete Only" (just track wins, no scoring)

**Dynamic Mode Naming**: `get_scoring_mode_name()` generates display names based on enabled factors

**Separate Leaderboards**: Each combination has its own high score table in `scores.jsonl`

**Settings Persistence**: Saved to `game_settings.json` as three boolean flags

**Extending**: To add new scoring factors, modify:
1. Add boolean flag to `game_state.py` (e.g., `self.combo_enabled`)
2. Update `get_current_score()` to conditionally calculate the new factor
3. Add to `get_scoring_mode_name()` function
4. Add checkbox to settings UI in `renderer.py`

**Key Files**: `constants.py` (get_scoring_mode_name), `settings.py` (persistence), `stats.py` (per-mode leaderboards), `game_state.py` (scoring logic)

### Auto-Finish System

**Detection**: Triggers when all tableau cards are face-up and stock/waste are empty
- Method: `game_state.check_auto_finish_available()`
- Button appears at bottom center

**Animation**: Cards fly to foundations in sequence with arc trajectory (0.3s per card)
- Updates in `main.py → update()` every frame
- Animation rendering in `renderer.py → _draw_auto_finish_animation()`

**Trigger**: Press F or click "Auto-Finish" button

**Key Files**: `game_state.py` (detection, move finding), `renderer.py` (UI/animation), `main.py` (update loop)

### Card-Based Overlap Snapping

**Algorithm**: 1/3 overlap threshold
1. Get dragged card rect
2. Check overlap with all pile rects
3. If overlap >= 33% of card area, that pile is a candidate
4. Return pile with **most** overlap

**Extended Hitboxes**: Tableau pile rects extend to cover entire visible stack

**Why Better**: More forgiving than mouse-based snapping. Players can release near pile edges.

**Key Files**: `input_handler.py` (_find_target_pile_by_overlap, _get_effective_pile_rect)

### Smooth Animations

**Snap-Back**: 200ms ease-out cubic when cards dropped in invalid zones
**Auto-Finish**: 300ms arc animation per card
**Both**: Run in `main.py → update()` every frame for smooth 60fps

---

## Adding Special Abilities

### Overview

Special abilities are the core feature of Phase 3. The architecture is already set up to support them.

### Card Ability Properties

Every Card has these properties:
```python
self.special_suit_ability: Optional[str] = None    # e.g., "hearts_heal"
self.special_rank_ability: Optional[str] = None    # e.g., "king_castle"
```

And activation methods:
```python
def activate_suit_ability(self, game_state: 'GameState') -> bool:
    """Activate this card's suit ability."""

def activate_rank_ability(self, game_state: 'GameState') -> bool:
    """Activate this card's rank ability."""
```

### Step-by-Step: Adding a Suit Ability

**Example:** Let's add a "Hearts Heal" ability that grants bonus points when Hearts cards are moved to foundation.

#### Step 1: Assign the Ability

In `game_state.py`, when creating the deck in `_create_deck()`:

```python
def _create_deck(self) -> List[Card]:
    """Create a standard 52-card deck."""
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    deck = []
    for suit in suits:
        for rank in ranks:
            card = Card(rank, suit)

            # Assign suit abilities
            if suit == 'hearts':
                card.special_suit_ability = "hearts_heal"

            deck.append(card)

    return deck
```

#### Step 2: Implement the Ability Logic

In `card.py`, implement `activate_suit_ability()`:

```python
def activate_suit_ability(self, game_state: 'GameState') -> bool:
    """
    Activate this card's suit ability.

    Returns:
        True if ability was activated
    """
    if not self.special_suit_ability:
        return False

    if self.special_suit_ability == "hearts_heal":
        # Grant bonus points when hearts reach foundation
        game_state.move_value_score += 20
        print(f"💖 Hearts Heal! +20 bonus points!")
        return True

    return False
```

#### Step 3: Trigger the Ability

In `game_state.py`, in the `try_move()` method, trigger abilities when appropriate:

```python
def try_move(self, cards: List[Card], source: Pile, target: Pile) -> bool:
    # ... existing move validation ...

    # Execute the move
    for card in cards:
        source.remove_card(card)
        target.add_card(card)

    # Trigger abilities
    if isinstance(target, FoundationPile):
        # Card reached foundation - activate suit ability!
        cards[0].activate_suit_ability(self)

    # ... rest of method ...
```

### Step-by-Step: Adding a Rank Ability

**Example:** "King's Castle" - When a King is placed on an empty tableau, draw an extra card from stock.

#### Step 1: Assign the Ability

```python
def _create_deck(self) -> List[Card]:
    deck = []
    for suit in suits:
        for rank in ranks:
            card = Card(rank, suit)

            if rank == 'K':
                card.special_rank_ability = "kings_castle"

            deck.append(card)
    return deck
```

#### Step 2: Implement the Logic

```python
def activate_rank_ability(self, game_state: 'GameState') -> bool:
    if not self.special_rank_ability:
        return False

    if self.special_rank_ability == "kings_castle":
        # Draw extra card from stock
        if game_state.stock.cards:
            card = game_state.stock.draw_card()
            if card:
                game_state.waste.add_card(card)
                print(f"🏰 King's Castle! Drew bonus card from stock!")
        return True

    return False
```

#### Step 3: Trigger the Ability

```python
def try_move(self, cards: List[Card], source: Pile, target: Pile) -> bool:
    # ... move execution ...

    # Trigger rank abilities
    if isinstance(target, TableauPile) and not target.cards:
        # King placed on empty tableau
        if cards[0].rank == 'K':
            cards[0].activate_rank_ability(self)
```

### Ability Design Guidelines

**Balance**: Abilities should be powerful but not game-breaking. Test thoroughly with playtesting.

**Clarity**: Print clear messages when abilities trigger so players understand what happened.

**State Access**: Abilities receive `game_state` and can modify any game state (piles, score, etc.).

**Flexibility**: You can trigger abilities on:
- Move to foundation
- Move to tableau
- Card flip
- Draw from stock
- Any custom event

### Advanced: Passive Abilities

Some abilities might be passive (always active) rather than triggered:

```python
class Card:
    def get_move_bonus(self) -> int:
        """Get bonus points for moving this card."""
        if self.special_suit_ability == "diamonds_wealth":
            return 5  # Diamonds worth extra
        return 0
```

Then in `game_state.py`:
```python
def record_move(self, source: Pile, target: Pile, cards: List[Card], ...):
    # Add passive ability bonuses
    for card in cards:
        self.move_value_score += card.get_move_bonus()
```

---

## Modifying Game Rules

### Pile Rules System

All game rules are encoded in pile classes via the `can_accept()` method. This makes rules explicit and easy to modify.

### Example: Relaxing Tableau Rules

**Current rule**: Tableau requires descending rank and alternating colors.

**New rule**: Allow same-color placements (harder variant).

In `pile.py`, modify `TableauPile.can_accept()`:

```python
def can_accept(self, card: Card, source_pile: Pile) -> bool:
    """Check if card can be placed on this tableau pile."""
    # Empty pile only accepts King
    if not self.cards:
        return card.rank == 'K'

    top_card = self.get_top_card()
    if not top_card.face_up:
        return False

    # Must be descending rank
    rank_valid = card.get_rank_value() == top_card.get_rank_value() - 1

    # MODIFIED: Remove color requirement for harder game
    # color_valid = card.get_color() != top_card.get_color()
    # return rank_valid and color_valid

    return rank_valid  # Now only requires descending rank
```

### Example: Foundation Rule Variant

**New rule**: Foundations can build down (descending) instead of up.

```python
class FoundationPile(Pile):
    def can_accept(self, card: Card, source_pile: Pile) -> bool:
        # Must be correct suit
        if card.suit != self.suit:
            return False

        # Empty pile accepts King (changed from Ace)
        if not self.cards:
            return card.rank == 'K'

        top_card = self.get_top_card()

        # Must be DESCENDING rank (changed from ascending)
        return card.get_rank_value() == top_card.get_rank_value() - 1
```

### Rule Modification Checklist

When modifying rules:
1. ✅ Update `can_accept()` method in appropriate pile class
2. ✅ Test with various card combinations
3. ✅ Check if win condition needs updating (`check_win()`)
4. ✅ Update any UI hints or help text
5. ✅ Document the variant in comments

---

## Creating New Pile Types

### Pile Hierarchy

```
Pile (base class)
├── StockPile
├── WastePile
├── FoundationPile
└── TableauPile
```

All piles inherit from `Pile` and must implement:
- `can_accept(card, source_pile) -> bool`
- `update_card_positions()`

Optionally override:
- `get_clickable_cards(pos) -> List[Card]`

### Example: Creating a "Reserve Pile"

Let's add a reserve pile (like in FreeCell) that holds one card temporarily.

#### Step 1: Define the Pile Class

In `pile.py`:

```python
class ReservePile(Pile):
    """Reserve pile that holds exactly one card temporarily."""

    def can_accept(self, card: Card, source_pile: Pile) -> bool:
        """Only accepts cards if empty (max 1 card)."""
        return len(self.cards) == 0

    def update_card_positions(self):
        """Single card at pile position."""
        for card in self.cards:
            card.position = self.position
            card.face_up = True

    def get_clickable_cards(self, pos: tuple) -> List[Card]:
        """Only the card (if present) is clickable."""
        if self.cards and self.rect.collidepoint(pos):
            return [self.cards[-1]]
        return []
```

#### Step 2: Add to Game State

In `game_state.py`:

```python
class GameState:
    def __init__(self):
        # ... existing piles ...
        self.reserves: List[ReservePile] = []

    def initialize_game(self):
        # ... existing initialization ...

        # Create 4 reserve piles
        self.reserves = []
        reserve_y = 50
        for i in range(4):
            x = 1000 + i * 60  # Position at right side
            self.reserves.append(ReservePile(x, reserve_y))

        # Add to all_piles for rendering
        self.all_piles = ([self.stock, self.waste] +
                         self.foundations +
                         self.tableaus +
                         self.reserves)
```

#### Step 3: Rendering

The pile will automatically be rendered if it's in `all_piles`. Add a label if needed:

```python
# In renderer.py, _draw_pile_outlines()
elif isinstance(pile, ReservePile):
    label_text = "RESERVE"
```

---

## Extending the Scoring System

### Scoring Configuration

All scoring values are in `game_state.scoring_config`:

```python
self.scoring_config = {
    'time_enabled': True,
    'moves_enabled': True,
    'value_enabled': True,
    'to_foundation': 10,
    'from_waste': 5,
    'flip_card': 5,
    'stock_recycle': -20,
    'time_multiplier': 10,
    'move_penalty': 2,
    'time_bonus_base': 15000
}
```

### Adding a New Scoring Component

**Example:** Bonus for completing a full suit.

#### Step 1: Track the Event

In `game_state.py`, in `try_move()`:

```python
def try_move(self, cards: List[Card], source: Pile, target: Pile) -> bool:
    # ... existing move logic ...

    # Check for completed suit
    if isinstance(target, FoundationPile):
        if len(target.cards) == 13:  # Full suit (A through K)
            # Suit completed!
            self.move_value_score += self.scoring_config.get('suit_completion_bonus', 500)
            print(f"🎉 Suit completed! +500 bonus!")
```

#### Step 2: Add to Config

```python
self.scoring_config = {
    # ... existing config ...
    'suit_completion_bonus': 500
}
```

#### Step 3: Display in UI

In `renderer.py`, update score breakdown display to show suit bonuses if desired.

### Score Balancing

After adding new scoring:
1. Playtest extensively
2. Compare scores to previous games
3. Adjust multipliers to maintain balance
4. Document expected score ranges

---

## State Management

### Undo System

The undo system uses deep copies of game state:

```python
def save_state(self):
    """Save current state for undo."""
    state_snapshot = {
        'stock': copy.deepcopy(self.stock),
        'waste': copy.deepcopy(self.waste),
        # ... all game state ...
    }
    self.history.append(state_snapshot)
```

**Important**: When adding new game state, add it to `save_state()` and `undo()`.

### Save/Load System

Game state is serialized to JSON:

```python
def _serialize_pile(self, pile: Pile) -> Dict:
    """Convert pile to JSON-compatible dict."""
    # Serialize all pile data
```

**When adding new pile types**: Implement serialization in `_serialize_pile()` and `_deserialize_pile()`.

### Custom Deepcopy

Cards implement custom `__deepcopy__` to skip pygame surfaces:

```python
def __deepcopy__(self, memo):
    """Skip copying pygame.Surface objects (images are cached)."""
    new_card = Card(self.rank, self.suit)
    new_card.face_up = self.face_up
    new_card.position = copy.deepcopy(self.position, memo)
    return new_card
```

**When adding new attributes**: Update `__deepcopy__` to include them.

---

## UI and Rendering

### Rendering Pipeline

```
main.py: render()
    → renderer.py: render(input_handler)
        → _draw_pile_outlines()
        → Draw cards (from all_piles)
        → _draw_hint_highlights()
        → _draw_score_info()
        → _draw_sage_advice()
        → pygame.display.flip()
```

### Adding Visual Effects

**Example:** Glow effect when ability triggers

```python
class Renderer:
    def __init__(self, screen, game_state):
        # ... existing init ...
        self.ability_glow = []  # List of (card, timer) tuples

    def trigger_ability_glow(self, card: Card):
        """Add glowing effect to card."""
        self.ability_glow.append((card, time.time()))

    def render(self, input_handler):
        # ... existing rendering ...

        # Draw ability glows
        self._draw_ability_glows()

    def _draw_ability_glows(self):
        """Draw glowing effects on cards with active abilities."""
        current_time = time.time()
        self.ability_glow = [
            (card, t) for card, t in self.ability_glow
            if current_time - t < 2.0  # 2 second duration
        ]

        for card, start_time in self.ability_glow:
            # Pulsing gold glow
            alpha = int(128 + 127 * abs(math.sin((current_time - start_time) * 3)))
            glow = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            glow.set_alpha(alpha)
            glow.fill((255, 215, 0))  # Gold
            self.screen.blit(glow, card.position)
```

### UI Best Practices

1. **Don't block the game loop** - Visual effects should be time-based, not frame-based
2. **Clear visual hierarchy** - Important info (score, hints) should be easily visible
3. **Consistent styling** - Use colors and fonts from constants.py
4. **Accessibility** - Use text labels, not just colors or symbols

---

## Common Patterns

### Pattern 1: Iterating Over All Cards

```python
# Iterate over all cards in game
for pile in game_state.all_piles:
    for card in pile.cards:
        # Do something with card
        pass
```

### Pattern 2: Finding Specific Cards

```python
# Find all Aces
aces = []
for pile in game_state.all_piles:
    for card in pile.cards:
        if card.rank == 'A':
            aces.append(card)
```

### Pattern 3: Checking Valid Moves

```python
# Get all valid moves for hints
valid_moves = game_state.get_valid_moves()
for card, source, target in valid_moves:
    print(f"Can move {card.rank} of {card.suit} from {source} to {target}")
```

### Pattern 4: Modifying Game State Safely

```python
# Always save state before modifications (for undo)
game_state.save_state()

# Modify state
card = source.cards.pop()
target.cards.append(card)

# Update positions
source.update_card_positions()
target.update_card_positions()
```

### Pattern 5: Triggering Events

```python
# Check if event occurred, then trigger
if len(foundation.cards) == 13:
    # Trigger suit completion event
    self.on_suit_completed(foundation)
```

---

## Testing Your Changes

### Manual Testing Checklist

When modifying game mechanics:

✅ **Basic gameplay**
- Can you start a new game?
- Can you drag and drop cards?
- Do moves validate correctly?

✅ **Edge cases**
- Empty piles
- Full piles
- Invalid moves
- Undo after special move

✅ **Scoring**
- Points awarded correctly?
- Score displays properly?
- Stats save correctly?

✅ **Save/Load**
- Can you save mid-game?
- Does load restore exact state?
- Are new attributes serialized?

✅ **UI**
- No visual glitches?
- Labels clear and readable?
- Responsive controls?

### Debugging Tips

**Print debugging**:
```python
print(f"DEBUG: Card {card.rank} of {card.suit} moved to {target.__class__.__name__}")
```

**Game state inspection**:
```python
# In renderer.py, add to render_debug_info()
text = f"Abilities active: {sum(1 for p in self.game_state.all_piles for c in p.cards if c.special_suit_ability)}"
```

**Undo/Redo testing**: Make changes, undo, verify state restored.

---

## Advanced Topics

### Performance Considerations

**Card image caching**: Images are loaded once and cached at class level. Don't reload images per card.

**Deep copy cost**: `save_state()` uses deepcopy which is expensive. Called on every move, so keep game state lean.

**Rendering optimization**: Only redraw when state changes (current implementation redraws every frame - room for optimization).

### Extending to New Solitaire Variants

**Spider Solitaire**: Use 2 decks, different pile rules
**FreeCell**: Add reserve piles, all cards visible from start
**Pyramid**: Different pile layout, different pairing rules

The architecture supports these - create new pile types and modify dealing.

### Multiplayer Considerations

The current architecture is single-player, but could be extended:
- Separate `GameState` per player
- Shared deck or separate decks
- Turn-based or simultaneous play

---

## Quick Reference

### Key Files and Their Purpose

| File | Purpose | Modify for... |
|------|---------|---------------|
| `constants.py` | Config values | Positions, colors, sizes |
| `card.py` | Card logic | Special abilities |
| `pile.py` | Game rules | Rule variants, new pile types |
| `game_state.py` | Game orchestration | Game flow, win conditions |
| `input_handler.py` | User input | New input methods |
| `renderer.py` | Visual display | UI changes, effects |
| `main.py` | Game loop | Menu navigation, flow |
| `stats.py` | Statistics | New stat tracking |

### Useful Code Locations

| Task | File | Method/Class |
|------|------|--------------|
| Add ability to card | `card.py` | `activate_suit_ability()` |
| Modify tableau rules | `pile.py` | `TableauPile.can_accept()` |
| Change scoring | `game_state.py` | `scoring_config`, `record_move()` |
| Trigger on move | `game_state.py` | `try_move()` |
| Add UI element | `renderer.py` | `render()` |
| New menu screen | `menu_state.py`, `renderer.py` | Add to MenuScreen enum |

---

## Getting Help

**Common Issues**:

- **"Card won't move"**: Check `can_accept()` in target pile
- **"Undo not working"**: Check `save_state()` includes new state
- **"Save/load broken"**: Check serialization methods
- **"Visual glitch"**: Check rendering order in `render()`
- **"Ability not triggering"**: Check where you call `activate_*_ability()`

**Best Practices**:
1. Read existing code before adding new code
2. Follow the established patterns
3. Test edge cases thoroughly
4. Document your changes
5. Keep separation of concerns

---

## Final Notes

This codebase was built with extensibility in mind. The architecture supports:
- ✅ Multiple ability systems
- ✅ Rule variants
- ✅ New pile types
- ✅ Custom scoring
- ✅ Save/load/undo

The key is understanding the module responsibilities and working within the established patterns.

**Have fun building Phase 3!** 🎴✨

---

*Documentation last updated: Phase 2 completion (February 2026)*
*Codebase version: 1.0.0*
*For questions or issues: See CLAUDE.md for project history*
