"""Auto-finish system for Pygame Solitaire."""

import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from card import Card
    from pile import Pile, TableauPile, FoundationPile
    from game_board import GameBoard


class AutoFinishSystem:
    """Manages auto-finish detection and animation."""

    def __init__(self, game_state: 'GameBoard'):
        """
        Initialize auto-finish system.

        Args:
            game_state: Game state to check and execute moves on
        """
        self.game_state = game_state
        self.available: bool = False
        self.active: bool = False
        self.current_card: Optional['Card'] = None
        self.source_pile: Optional['Pile'] = None
        self.target_pile: Optional['Pile'] = None
        self.start_time: float = 0.0

    def check_available(self) -> bool:
        """
        Check if auto-finish is available.

        Auto-finish is available when all tableau cards are face-up and
        all remaining moves are to foundations (no decisions needed).

        Returns:
            True if auto-finish should be offered
        """
        # All tableau cards must be face-up
        for tableau in self.game_state.tableaus:
            for card in tableau.cards:
                if not card.face_up:
                    return False

        # Stock and waste must be empty (or we'd need to draw)
        if self.game_state.stock.cards or self.game_state.waste.cards:
            return False

        # If we get here, all cards are visible and accessible
        # Only foundation moves remain - offer auto-finish!
        return True

    def start(self) -> bool:
        """
        Start auto-finish mode and find first move.

        Returns:
            True if auto-finish started, False if no moves available
        """
        if not self.available:
            return False

        self.active = True
        self.available = False
        return self.start_next_move()

    def start_next_move(self) -> bool:
        """
        Find and start animating the next auto-finish move.

        Returns:
            True if a move was found, False if complete
        """
        # Look for any card that can go to foundation
        for tableau in self.game_state.tableaus:
            if tableau.cards:
                top_card = tableau.cards[-1]
                # Try each foundation
                for foundation in self.game_state.foundations:
                    if foundation.can_accept(top_card, tableau):
                        # Start animation
                        self.current_card = top_card
                        self.source_pile = tableau
                        self.target_pile = foundation
                        self.start_time = time.time()
                        return True

        # No more moves - complete!
        return False

    def complete_current_move(self):
        """Complete the current auto-finish move (called after animation)."""
        if self.current_card and self.source_pile and self.target_pile:
            # Execute the move
            self.game_state.try_move([self.current_card], self.source_pile, self.target_pile)

            # Clear animation state
            self.current_card = None
            self.source_pile = None
            self.target_pile = None

    def get_animation_progress(self) -> float:
        """
        Get current animation progress (0.0 to 1.0).

        Returns:
            Animation progress as a ratio
        """
        if not self.current_card:
            return 1.0

        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / 0.3)  # 0.3s animation duration

    def stop(self):
        """Stop auto-finish mode."""
        self.active = False
        self.current_card = None
        self.source_pile = None
        self.target_pile = None

    def is_animating(self) -> bool:
        """
        Check if currently animating a card.

        Returns:
            True if animation is in progress
        """
        return self.current_card is not None
