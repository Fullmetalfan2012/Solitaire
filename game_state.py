"""Game state management for Pygame Solitaire."""

import random
import time
import copy
import json
import os
from typing import List, Optional, Dict, Any
from card import Card
from pile import Pile, StockPile, WastePile, FoundationPile, TableauPile
from move import Move
from constants import (
    STOCK_POS, WASTE_POS, FOUNDATION_START, FOUNDATION_SPACING,
    TABLEAU_START, TABLEAU_SPACING, get_scoring_mode_name
)


class GameState:
    """Manages all game logic, state, and rules."""

    def __init__(self):
        """Initialize game state."""
        self.stock: Optional[StockPile] = None
        self.waste: Optional[WastePile] = None
        self.foundations: List[FoundationPile] = []
        self.tableaus: List[TableauPile] = []
        self.all_piles: List[Pile] = []

        # Scoring system
        self.start_time: float = 0.0
        self.move_count: int = 0
        self.move_value_score: int = 0
        self.scoring_config: Dict[str, any] = {
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

        # Undo/redo system using move tracking (unlimited undo/redo)
        self.move_history: List[Move] = []
        self.current_move_index: int = 0  # Points to next move to make (for redo)

        # Scoring factors (toggleable)
        self.time_enabled: bool = True
        self.moves_enabled: bool = True
        self.values_enabled: bool = True

        # Hint system
        self.hints_remaining: int = 3
        self.hint_targets: List[Pile] = []  # Piles to highlight
        self.sage_advice_text: Optional[str] = None
        self.sage_advice_timer: float = 0.0

        # Load sage advice from JSON
        self._sage_wisdom: Dict[str, List[str]] = {}
        self._load_sage_advice()

        # Auto-finish system
        self.auto_finish_available: bool = False
        self.auto_finishing: bool = False
        self.auto_finish_card: Optional[Card] = None
        self.auto_finish_source: Optional[Pile] = None
        self.auto_finish_target: Optional[Pile] = None
        self.auto_finish_start_time: float = 0.0

    def _load_sage_advice(self):
        """Load sage advice from JSON file."""
        try:
            advice_path = os.path.join(os.path.dirname(__file__), 'data', 'sage_advice.json')
            with open(advice_path, 'r') as f:
                self._sage_wisdom = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load sage advice: {e}")
            # Fallback to empty dict
            self._sage_wisdom = {}

    def initialize_game(self):
        """Set up a new game with shuffled deck."""
        # Reset scoring
        self.start_time = time.time()
        self.move_count = 0
        self.move_value_score = 0

        # Clear move history
        self.move_history = []
        self.current_move_index = 0

        # Reset hint system
        self.hints_remaining = 3
        self.hint_targets = []
        self.sage_advice_text = None
        self.sage_advice_timer = 0.0

        # Create stock and waste piles
        self.stock = StockPile(*STOCK_POS)
        self.waste = WastePile(*WASTE_POS)

        # Create foundation piles (one for each suit)
        self.foundations = []
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        for i, suit in enumerate(suits):
            x = FOUNDATION_START[0] + i * FOUNDATION_SPACING
            self.foundations.append(FoundationPile(x, FOUNDATION_START[1], suit))

        # Create tableau piles
        self.tableaus = []
        for i in range(7):
            x = TABLEAU_START[0] + i * TABLEAU_SPACING
            self.tableaus.append(TableauPile(x, TABLEAU_START[1]))

        # Store all piles for easy iteration
        self.all_piles = [self.stock, self.waste] + self.foundations + self.tableaus

        # Create, shuffle, and deal deck
        deck = self._create_deck()
        random.shuffle(deck)
        self._deal_cards(deck)

    def _create_deck(self) -> List[Card]:
        """
        Create a standard 52-card deck.

        Returns:
            List of 52 Card objects
        """
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return [Card(rank, suit) for suit in suits for rank in ranks]

    def _deal_cards(self, deck: List[Card]):
        """
        Deal cards Klondike-style.

        Deals cards to tableau piles:
        - Pile 1: 1 card
        - Pile 2: 2 cards
        - ...
        - Pile 7: 7 cards
        Top card in each pile is face up, rest are face down.
        Remaining cards go to stock.

        Args:
            deck: Shuffled deck of cards
        """
        # Deal to tableau
        for i in range(7):
            for j in range(i + 1):
                card = deck.pop()
                self.tableaus[i].add_card(card)

            # Flip top card face up
            self.tableaus[i].cards[-1].face_up = True

        # Remaining cards go to stock (face down)
        for card in deck:
            self.stock.add_card(card)

    def handle_stock_click(self):
        """
        Handle clicking on the stock pile.

        If stock has cards, draw one to waste.
        If stock is empty, recycle waste back to stock.
        """
        if self.stock.cards:
            # Draw card from stock to waste
            card = self.stock.draw_card()
            if card:
                self.waste.add_card(card)
                # Create move for undo/redo (single card from stock to waste)
                # Clear any "future" moves
                if self.current_move_index < len(self.move_history):
                    self.move_history = self.move_history[:self.current_move_index]
                move = Move(self.stock, self.waste, [card], None)
                self.move_history.append(move)
                self.current_move_index = len(self.move_history)
            # Note: Drawing from stock doesn't count as a scored move
        else:
            # Recycle waste back to stock
            cards_to_recycle = list(self.waste.cards)  # Copy list before clearing
            card_states = [card.face_up for card in cards_to_recycle]  # Store states before flipping

            while self.waste.cards:
                card = self.waste.cards.pop()
                card.face_up = False
                self.stock.add_card(card)

            # Create move for undo/redo (all cards from waste to stock, with original states)
            # Clear any "future" moves
            if self.current_move_index < len(self.move_history):
                self.move_history = self.move_history[:self.current_move_index]
            move = Move(self.waste, self.stock, cards_to_recycle, None, card_states)
            self.move_history.append(move)
            self.current_move_index = len(self.move_history)

            # Record the recycle action (penalty)
            self.record_stock_action(recycled=True)

    def try_move(self, cards: List[Card], source: Pile, target: Pile) -> bool:
        """
        Attempt to move cards from source pile to target pile.

        Args:
            cards: List of cards to move
            source: Source pile
            target: Target pile

        Returns:
            True if move was successful, False otherwise
        """
        # Can only move single card to foundation
        if isinstance(target, FoundationPile) and len(cards) > 1:
            return False

        # Check if move is legal using target pile's rules
        if not target.can_accept(cards[0], source):
            return False

        # Execute the move
        for card in cards:
            source.remove_card(card)
            target.add_card(card)

        # Check if we flipped a card
        revealed_card = None
        if isinstance(source, TableauPile):
            if source.flip_top_card():
                # A card was flipped - track it for undo
                revealed_card = source.cards[-1] if source.cards else None

        # Calculate score change for this move (before updating score)
        score_before = self.move_value_score
        self.record_move(source, target, cards, revealed_card is not None)
        score_delta = self.move_value_score - score_before

        # Create and store move for undo/redo
        # Clear any "future" moves if we're in the middle of history
        if self.current_move_index < len(self.move_history):
            self.move_history = self.move_history[:self.current_move_index]

        move = Move(source, target, cards, revealed_card, score_delta=score_delta)
        self.move_history.append(move)
        self.current_move_index = len(self.move_history)

        return True

    def check_win(self) -> bool:
        """
        Check if the game is won.

        Game is won when all foundations have 13 cards (full suit).

        Returns:
            True if game is won
        """
        return all(len(foundation.cards) == 13 for foundation in self.foundations)

    def check_auto_finish_available(self) -> bool:
        """
        Check if auto-finish is available.

        Auto-finish is available when all tableau cards are face-up and
        all remaining moves are to foundations (no decisions needed).

        Returns:
            True if auto-finish should be offered
        """
        # All tableau cards must be face-up
        for tableau in self.tableaus:
            for card in tableau.cards:
                if not card.face_up:
                    return False

        # Stock and waste must be empty (or we'd need to draw)
        if self.stock.cards or self.waste.cards:
            return False

        # If we get here, all cards are visible and accessible
        # Only foundation moves remain - offer auto-finish!
        return True

    def start_auto_finish_move(self) -> bool:
        """
        Find and start animating the next auto-finish move.

        Returns:
            True if a move was found, False if complete
        """
        # Look for any card that can go to foundation
        for tableau in self.tableaus:
            if tableau.cards:
                top_card = tableau.cards[-1]
                # Try each foundation
                for foundation in self.foundations:
                    if foundation.can_accept(top_card, tableau):
                        # Start animation
                        self.auto_finish_card = top_card
                        self.auto_finish_source = tableau
                        self.auto_finish_target = foundation
                        self.auto_finish_start_time = time.time()
                        return True

        # No more moves - complete!
        return False

    def complete_auto_finish_move(self):
        """Complete the current auto-finish move (called after animation)."""
        if self.auto_finish_card and self.auto_finish_source and self.auto_finish_target:
            # Execute the move
            self.try_move([self.auto_finish_card], self.auto_finish_source, self.auto_finish_target)

            # Clear animation state
            self.auto_finish_card = None
            self.auto_finish_source = None
            self.auto_finish_target = None

    def get_pile_at(self, pos: tuple) -> Optional[Pile]:
        """
        Get the pile at the given screen position.

        Args:
            pos: Screen position (x, y)

        Returns:
            Pile at that position, or None
        """
        # Check in reverse order so top piles are prioritized
        for pile in reversed(self.all_piles):
            if pile.rect.collidepoint(pos):
                return pile
        return None

    def get_valid_moves(self) -> List[tuple]:
        """
        Get all valid moves in current state for hint system.

        Returns:
            List of (card, source_pile, target_pile) tuples representing legal moves
        """
        valid_moves = []

        # Check all possible sources
        source_piles = [self.waste] + self.tableaus

        for source in source_piles:
            if not source.cards:
                continue

            # For tableau, check if we can move sequences
            if isinstance(source, TableauPile):
                # Find all face-up sequences
                clickable = source.get_clickable_cards(source.position)
                if clickable:
                    # Try moving each possible sequence to all targets
                    first_card = clickable[0]

                    # Try foundations (single card only)
                    for foundation in self.foundations:
                        if foundation.can_accept(first_card, source):
                            valid_moves.append((first_card, source, foundation))

                    # Try tableaus (can move sequences)
                    for tableau in self.tableaus:
                        if tableau != source and tableau.can_accept(first_card, source):
                            valid_moves.append((first_card, source, tableau))

            # For waste, only top card
            elif isinstance(source, WastePile):
                if source.cards:
                    top_card = source.cards[-1]

                    # Try foundations
                    for foundation in self.foundations:
                        if foundation.can_accept(top_card, source):
                            valid_moves.append((top_card, source, foundation))

                    # Try tableaus
                    for tableau in self.tableaus:
                        if tableau.can_accept(top_card, source):
                            valid_moves.append((top_card, source, tableau))

        return valid_moves

    def record_move(self, source: Pile, target: Pile, cards: List[Card], flipped_card: bool = False):
        """
        Record a move for scoring purposes.

        Args:
            source: Source pile
            target: Target pile
            cards: Cards that were moved
            flipped_card: Whether a tableau card was flipped as result
        """
        self.move_count += 1

        if not self.scoring_config['value_enabled']:
            return

        # Award points for moving to foundation
        if isinstance(target, FoundationPile):
            self.move_value_score += self.scoring_config['to_foundation']

        # Bonus for moving from waste pile
        if isinstance(source, WastePile):
            self.move_value_score += self.scoring_config['from_waste']

        # Bonus for flipping a tableau card
        if flipped_card:
            self.move_value_score += self.scoring_config['flip_card']

    def record_stock_action(self, recycled: bool = False):
        """
        Record a stock pile action for scoring.

        Args:
            recycled: Whether the waste was recycled back to stock
        """
        if recycled and self.scoring_config['value_enabled']:
            # Penalty for recycling waste back to stock
            self.move_value_score += self.scoring_config['stock_recycle']

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since game start in seconds.

        Returns:
            Elapsed time in seconds
        """
        return time.time() - self.start_time

    def get_current_score(self) -> Dict[str, any]:
        """
        Calculate current score based on enabled scoring factors.

        Returns:
            Dictionary with score components, total, and mode info
        """
        elapsed = self.get_elapsed_time()

        # Time component (bonus for fast play) - only if enabled
        time_score = 0
        if self.time_enabled and self.scoring_config['time_enabled']:
            time_bonus_base = self.scoring_config['time_bonus_base']
            time_multiplier = self.scoring_config['time_multiplier']
            time_score = max(0, time_bonus_base - int(elapsed * time_multiplier))

        # Move efficiency penalty - only if enabled
        move_penalty = 0
        if self.moves_enabled and self.scoring_config['moves_enabled']:
            move_penalty = self.move_count * self.scoring_config['move_penalty']

        # Card value score - only if enabled
        value_score = self.move_value_score if self.values_enabled else 0

        # Calculate total
        total_score = value_score + time_score - move_penalty

        # Generate scoring mode name
        mode_name = get_scoring_mode_name(self.time_enabled, self.moves_enabled, self.values_enabled)

        return {
            'total': max(0, total_score),  # Never negative
            'move_value': self.move_value_score,
            'time_bonus': time_score,
            'move_penalty': move_penalty,
            'move_count': self.move_count,
            'elapsed_time': elapsed,
            'scoring_mode': mode_name,  # Dynamic name based on enabled factors
            'time_enabled': self.time_enabled,
            'moves_enabled': self.moves_enabled,
            'values_enabled': self.values_enabled,
        }

    def calculate_final_score(self) -> Dict[str, any]:
        """
        Calculate final score at game end.

        Returns:
            Dictionary with final score breakdown
        """
        return self.get_current_score()

    def undo(self) -> bool:
        """
        Undo the last move using move tracking.

        Returns:
            True if undo was successful, False if no moves to undo
        """
        if self.current_move_index == 0:
            return False

        # Decrement index to point to move to undo
        self.current_move_index -= 1

        # Get the move to undo
        move = self.move_history[self.current_move_index]

        # Undo the move
        move.undo()

        # Update card positions for rendering
        for pile in self.all_piles:
            pile.update_card_positions()

        # Restore score to previous value
        self.move_value_score -= move.score_delta

        # Decrement move count (if it was a scored move, not stock draw)
        # We'll need to track this better, but for now just decrement if > 0
        if self.move_count > 0:
            self.move_count -= 1

        return True

    def redo(self) -> bool:
        """
        Redo the next move using move tracking.

        Returns:
            True if redo was successful, False if no moves to redo
        """
        if self.current_move_index >= len(self.move_history):
            return False

        # Get the move to redo
        move = self.move_history[self.current_move_index]

        # Re-execute the move
        move.execute()

        # Reapply score change
        self.move_value_score += move.score_delta

        # Increment move count
        self.move_count += 1

        # Increment index
        self.current_move_index += 1

        # Update card positions for rendering
        for pile in self.all_piles:
            pile.update_card_positions()

        return True

    def can_redo(self) -> bool:
        """
        Check if redo is available.

        Returns:
            True if there are moves to redo
        """
        return self.current_move_index < len(self.move_history)

    def get_redo_count(self) -> int:
        """
        Get number of redo operations available.

        Returns:
            Number of moves that can be redone
        """
        return len(self.move_history) - self.current_move_index

    def can_undo(self) -> bool:
        """
        Check if undo is available.

        Returns:
            True if there are moves to undo
        """
        return self.current_move_index > 0

    def get_undo_count(self) -> int:
        """
        Get number of undo operations available.

        Returns:
            Number of moves that can be undone
        """
        return self.current_move_index

    def use_hint(self) -> bool:
        """
        Use a hint to show valid moves.

        Highlights all valid move destinations for a few seconds.

        Returns:
            True if hint was used, False if no hints remaining
        """
        if self.hints_remaining <= 0:
            return False

        self.hints_remaining -= 1

        # Get all valid moves and extract unique target piles
        valid_moves = self.get_valid_moves()
        self.hint_targets = list(set(target for _, _, target in valid_moves))

        return True

    def clear_hints(self):
        """Clear hint highlights."""
        self.hint_targets = []

    def get_sage_advice(self) -> str:
        """
        Get sage advice (unlimited, comedic animal facts).

        Returns:
            Random useless animal wisdom
        """
        if not self._sage_wisdom:
            return "No wisdom available. The universe is silent."

        # Flatten all wisdom categories into one pool
        all_wisdom = [advice for category in self._sage_wisdom.values() for advice in category]

        if not all_wisdom:
            return "No wisdom available. The universe is silent."

        return random.choice(all_wisdom)

    def show_sage_advice(self):
        """Display sage advice on screen for a few seconds."""
        self.sage_advice_text = self.get_sage_advice()
        self.sage_advice_timer = time.time()

    def update_sage_advice(self):
        """Update sage advice timer and clear if expired."""
        if self.sage_advice_text and (time.time() - self.sage_advice_timer) > 5.0:
            self.sage_advice_text = None

    def save_game(self, filename: str = "savegame.json") -> bool:
        """
        Save current game state to file.

        Args:
            filename: Path to save file

        Returns:
            True if save successful, False otherwise
        """
        try:
            # Serialize game state
            save_data = {
                'start_time': self.start_time,
                'move_count': self.move_count,
                'move_value_score': self.move_value_score,
                'hints_remaining': self.hints_remaining,
                'scoring_config': self.scoring_config,
                'time_enabled': self.time_enabled,
                'moves_enabled': self.moves_enabled,
                'values_enabled': self.values_enabled,
                'stock': self._serialize_pile(self.stock),
                'waste': self._serialize_pile(self.waste),
                'foundations': [self._serialize_pile(f) for f in self.foundations],
                'tableaus': [self._serialize_pile(t) for t in self.tableaus],
                'move_history': [move.to_dict(self.all_piles) for move in self.move_history],
                'current_move_index': self.current_move_index,
                'saved_at': time.time()
            }

            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, filename: str = "savegame.json") -> bool:
        """
        Load game state from file.

        Args:
            filename: Path to save file

        Returns:
            True if load successful, False otherwise
        """
        if not os.path.exists(filename):
            return False

        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)

            # Restore scoring and game state
            self.start_time = save_data['start_time']
            self.move_count = save_data['move_count']
            self.move_value_score = save_data['move_value_score']
            self.hints_remaining = save_data['hints_remaining']
            self.scoring_config = save_data['scoring_config']
            # Restore scoring factors (with defaults for backward compatibility)
            self.time_enabled = save_data.get('time_enabled', True)
            self.moves_enabled = save_data.get('moves_enabled', True)
            self.values_enabled = save_data.get('values_enabled', True)

            # Restore piles
            self.stock = self._deserialize_pile(save_data['stock'], StockPile)
            self.waste = self._deserialize_pile(save_data['waste'], WastePile)
            self.foundations = [
                self._deserialize_pile(f, FoundationPile)
                for f in save_data['foundations']
            ]
            self.tableaus = [
                self._deserialize_pile(t, TableauPile)
                for t in save_data['tableaus']
            ]

            # Rebuild all_piles list
            self.all_piles = [self.stock, self.waste] + self.foundations + self.tableaus

            # Restore move history (with backward compatibility)
            if 'move_history' in save_data:
                self.move_history = [
                    Move.from_dict(move_data, self.all_piles)
                    for move_data in save_data['move_history']
                ]
                self.current_move_index = save_data.get('current_move_index', 0)
            else:
                # Old save files without move history
                self.move_history = []
                self.current_move_index = 0

            # Clear history and hints
            self.history = []
            self.hint_targets = []
            self.sage_advice_text = None

            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def _serialize_pile(self, pile: Pile) -> Dict:
        """Serialize a pile to JSON-compatible dict."""
        pile_data = {
            'type': pile.__class__.__name__,
            'position': pile.position,
            'cards': []
        }

        # Add suit for FoundationPile
        if isinstance(pile, FoundationPile):
            pile_data['suit'] = pile.suit

        # Serialize cards
        for card in pile.cards:
            pile_data['cards'].append({
                'rank': card.rank,
                'suit': card.suit,
                'face_up': card.face_up,
                'position': card.position
            })

        return pile_data

    def _deserialize_pile(self, pile_data: Dict, pile_class: type) -> Pile:
        """Deserialize a pile from JSON dict."""
        x, y = pile_data['position']

        # Create pile with appropriate constructor
        if pile_class == FoundationPile:
            pile = pile_class(x, y, pile_data['suit'])
        else:
            pile = pile_class(x, y)

        # Restore cards
        for card_data in pile_data['cards']:
            card = Card(card_data['rank'], card_data['suit'])
            card.face_up = card_data['face_up']
            card.position = tuple(card_data['position'])
            pile.cards.append(card)

        pile.update_card_positions()
        return pile

    @staticmethod
    def save_exists(filename: str = "savegame.json") -> bool:
        """Check if a save file exists."""
        return os.path.exists(filename)
