"""Input handling for Pygame Solitaire."""

import pygame
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

        # Snap-back animation
        self.snapping_back = False
        self.snap_back_cards: List[Card] = []
        self.snap_back_start_positions = []
        self.snap_back_target_positions = []
        self.snap_back_start_time = 0.0

        # Click detection (for click-to-place)
        self.mouse_down_pos = None
        self.mouse_moved = False

    def handle_mouse_down(self, pos: tuple):
        """
        Handle mouse button press.

        Args:
            pos: Mouse position (x, y)
        """
        # Track mouse down position for click detection
        self.mouse_down_pos = pos
        self.mouse_moved = False

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
        # Check if mouse has moved significantly (for click detection)
        if self.mouse_down_pos and not self.mouse_moved:
            dx = abs(pos[0] - self.mouse_down_pos[0])
            dy = abs(pos[1] - self.mouse_down_pos[1])
            if dx > 5 or dy > 5:  # 5 pixel threshold
                self.mouse_moved = True

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

        # Check if this was a click (not a drag)
        if not self.mouse_moved and self.mouse_down_pos:
            # This was a click! Try auto-placement
            if self._try_auto_place():
                self._reset_drag_state()
                return

        # Normal drag behavior
        # Find target pile using card overlap detection (not mouse position)
        target_pile = self._find_target_pile_by_overlap()

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

    def _find_target_pile_by_overlap(self) -> Optional[Pile]:
        """
        Find target pile by checking card overlap (not mouse position).

        Returns the pile with the most overlap if overlap >= 1/3 of card area.

        Returns:
            Target pile with most overlap, or None if no sufficient overlap
        """
        if not self.dragged_cards:
            return None

        # Use first dragged card for overlap detection
        first_card = self.dragged_cards[0]
        from constants import CARD_WIDTH, CARD_HEIGHT

        # Create rect for the dragged card's current position
        card_rect = pygame.Rect(
            int(first_card.position[0]),
            int(first_card.position[1]),
            CARD_WIDTH,
            CARD_HEIGHT
        )

        card_area = CARD_WIDTH * CARD_HEIGHT
        overlap_threshold = card_area / 3.0  # 1/3 overlap required

        best_pile = None
        best_overlap = 0

        # Check all piles for overlap
        for pile in self.game_state.all_piles:
            if pile == self.source_pile:
                continue

            # For tableau piles, extend the rect to cover stacked cards
            pile_rect = self._get_effective_pile_rect(pile)

            # Calculate overlap
            if card_rect.colliderect(pile_rect):
                # Get intersection rect
                intersection = card_rect.clip(pile_rect)
                overlap_area = intersection.width * intersection.height

                # Track pile with most overlap if it meets threshold
                if overlap_area >= overlap_threshold and overlap_area > best_overlap:
                    best_overlap = overlap_area
                    best_pile = pile

        return best_pile

    def _get_effective_pile_rect(self, pile: Pile) -> pygame.Rect:
        """
        Get the effective rect for a pile, extended to cover stacked cards.

        Args:
            pile: The pile to get rect for

        Returns:
            Extended rect covering all cards in the pile
        """
        from pile import TableauPile

        # Start with base pile rect
        rect = pile.rect.copy()

        # For tableau piles with cards, extend rect to cover visible stack
        if isinstance(pile, TableauPile) and pile.cards:
            num_cards = len(pile.cards)
            if num_cards > 1:
                # Extend height to cover all overlapping cards
                stack_height = (num_cards - 1) * CARD_OVERLAP_Y
                rect.height += stack_height

        return rect

    def _try_auto_place(self) -> bool:
        """
        Try to automatically place clicked card if it has only one valid destination.

        Returns:
            True if auto-placement succeeded
        """
        from pile import FoundationPile, TableauPile

        if not self.dragged_cards or not self.source_pile:
            return False

        # Only auto-place single cards
        if len(self.dragged_cards) != 1:
            return False

        card = self.dragged_cards[0]
        valid_destinations = []

        # Check foundations
        for foundation in self.game_state.foundations:
            if foundation.can_accept(card, self.source_pile):
                valid_destinations.append(foundation)

        # Check tableau piles
        for tableau in self.game_state.tableaus:
            if tableau != self.source_pile and tableau.can_accept(card, self.source_pile):
                valid_destinations.append(tableau)

        # If exactly one valid destination, move there!
        if len(valid_destinations) == 1:
            return self.game_state.try_move([card], self.source_pile, valid_destinations[0])

        return False

    def _cancel_drag(self):
        """Start snap-back animation to return cards to original positions."""
        import time

        # Store current positions as start
        self.snap_back_start_positions = [card.position for card in self.dragged_cards]
        self.snap_back_target_positions = self.original_positions
        self.snap_back_cards = self.dragged_cards.copy()

        # Start animation
        self.snapping_back = True
        self.snap_back_start_time = time.time()

    def update_snap_back(self):
        """Update snap-back animation (call every frame)."""
        if not self.snapping_back:
            return

        import time

        # Calculate animation progress (0.0 to 1.0)
        elapsed = time.time() - self.snap_back_start_time
        duration = 0.2  # 200ms animation
        progress = min(1.0, elapsed / duration)

        # Ease-out cubic for smooth deceleration
        eased_progress = 1 - pow(1 - progress, 3)

        # Interpolate positions
        for card, start_pos, target_pos in zip(
            self.snap_back_cards,
            self.snap_back_start_positions,
            self.snap_back_target_positions
        ):
            current_x = start_pos[0] + (target_pos[0] - start_pos[0]) * eased_progress
            current_y = start_pos[1] + (target_pos[1] - start_pos[1]) * eased_progress
            card.position = (current_x, current_y)

        # Complete animation if done
        if progress >= 1.0:
            # Ensure final positions are exact
            for card, target_pos in zip(self.snap_back_cards, self.snap_back_target_positions):
                card.position = target_pos

            # Clear animation state
            self.snapping_back = False
            self.snap_back_cards = []
            self.snap_back_start_positions = []
            self.snap_back_target_positions = []

    def _reset_drag_state(self):
        """Reset all drag-related state."""
        self.dragging = False
        self.dragged_cards = []
        self.source_pile = None
        self.drag_offset = (0, 0)
        self.original_positions = []
