"""Input handling for Pygame Solitaire."""

from typing import List, Optional, TYPE_CHECKING
from card import Card
from pile import Pile
from constants import CARD_OVERLAP_Y

if TYPE_CHECKING:
    from game_state import GameState


class InputHandler:
    """Handles all mouse input and drag-and-drop logic."""

    def __init__(self, game_state: 'GameState'):
        """
        Initialize input handler.

        Args:
            game_state: Game state to interact with
        """
        self.game_state = game_state

        # Drag state
        self.dragging = False
        self.dragged_cards: List[Card] = []
        self.source_pile: Optional[Pile] = None
        self.drag_offset = (0, 0)
        self.original_positions = []

    def handle_mouse_down(self, pos: tuple):
        """
        Handle mouse button press.

        Args:
            pos: Mouse position (x, y)
        """
        # Check if clicking on stock pile
        if self.game_state.stock.rect.collidepoint(pos):
            self.game_state.handle_stock_click()
            return

        # Check all piles for clickable cards
        for pile in self.game_state.all_piles:
            cards = pile.get_clickable_cards(pos)
            if cards:
                # Start dragging these cards
                self.dragging = True
                self.dragged_cards = cards
                self.source_pile = pile

                # Calculate offset from mouse to first card's position
                first_card = cards[0]
                self.drag_offset = (
                    pos[0] - first_card.position[0],
                    pos[1] - first_card.position[1]
                )

                # Save original positions for canceling
                self.original_positions = [card.position for card in cards]
                break

    def handle_mouse_motion(self, pos: tuple):
        """
        Handle mouse movement while dragging.

        Args:
            pos: Mouse position (x, y)
        """
        if self.dragging and self.dragged_cards:
            # Calculate new base position
            base_x = pos[0] - self.drag_offset[0]
            base_y = pos[1] - self.drag_offset[1]

            # Update positions of all dragged cards
            for i, card in enumerate(self.dragged_cards):
                card.position = (base_x, base_y + i * CARD_OVERLAP_Y)

    def handle_mouse_up(self, pos: tuple):
        """
        Handle mouse button release.

        Args:
            pos: Mouse position (x, y)
        """
        if not self.dragging:
            return

        # Find target pile at drop position
        target_pile = self.game_state.get_pile_at(pos)

        move_successful = False

        if target_pile and target_pile != self.source_pile:
            # Try to move cards to target pile
            move_successful = self.game_state.try_move(
                self.dragged_cards,
                self.source_pile,
                target_pile
            )

        if not move_successful:
            # Move failed or no valid target - cancel drag
            self._cancel_drag()

        # Reset drag state
        self._reset_drag_state()

    def _cancel_drag(self):
        """Return dragged cards to their original positions."""
        for card, original_pos in zip(self.dragged_cards, self.original_positions):
            card.position = original_pos

    def _reset_drag_state(self):
        """Reset all drag-related state."""
        self.dragging = False
        self.dragged_cards = []
        self.source_pile = None
        self.drag_offset = (0, 0)
        self.original_positions = []
