"""Pile classes for Pygame Solitaire."""

import pygame
from typing import List, Optional
from card import Card
from constants import CARD_WIDTH, CARD_HEIGHT, CARD_OVERLAP_Y


class Pile:
    """Base class for all pile types."""

    def __init__(self, x: int, y: int):
        """
        Initialize a pile.

        Args:
            x: X position on screen
            y: Y position on screen
        """
        self.cards: List[Card] = []
        self.position = (x, y)
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    def can_accept(self, card: Card, source_pile: 'Pile') -> bool:
        """
        Check if this pile can accept a card.

        Args:
            card: The card to check
            source_pile: The pile the card is coming from

        Returns:
            True if the card can be placed here
        """
        raise NotImplementedError("Subclasses must implement can_accept()")

    def add_card(self, card: Card):
        """Add a card to this pile."""
        self.cards.append(card)
        self.update_card_positions()

    def remove_card(self, card: Card) -> Card:
        """Remove and return a card from this pile."""
        self.cards.remove(card)
        self.update_card_positions()
        return card

    def get_top_card(self) -> Optional[Card]:
        """Return the top card without removing it."""
        return self.cards[-1] if self.cards else None

    def update_card_positions(self):
        """Update positions of all cards in this pile."""
        raise NotImplementedError("Subclasses must implement update_card_positions()")

    def get_clickable_cards(self, pos: tuple) -> List[Card]:
        """
        Get cards that can be picked up at the given position.

        Args:
            pos: Mouse position (x, y)

        Returns:
            List of cards that can be dragged (may be empty)
        """
        raise NotImplementedError("Subclasses must implement get_clickable_cards()")


class StockPile(Pile):
    """The stock (draw) pile where players draw cards from."""

    def can_accept(self, card: Card, source_pile: Pile) -> bool:
        """Stock pile doesn't accept cards being placed on it."""
        return False

    def update_card_positions(self):
        """All cards in stock are at the same position, face down."""
        for card in self.cards:
            card.position = self.position
            card.face_up = False

    def get_clickable_cards(self, pos: tuple) -> List[Card]:
        """Stock pile doesn't support dragging cards."""
        return []

    def draw_card(self) -> Optional[Card]:
        """
        Remove and return the top card from stock.

        Returns:
            The top card, or None if stock is empty
        """
        if self.cards:
            return self.cards.pop()
        return None


class WastePile(Pile):
    """The waste pile where cards from stock are placed."""

    def can_accept(self, card: Card, source_pile: Pile) -> bool:
        """Waste pile only accepts cards from stock pile."""
        return isinstance(source_pile, StockPile)

    def update_card_positions(self):
        """All cards in waste are at the same position, face up."""
        for card in self.cards:
            card.position = self.position
            card.face_up = True

    def get_clickable_cards(self, pos: tuple) -> List[Card]:
        """Only the top card can be dragged from waste."""
        if self.cards and self.rect.collidepoint(pos):
            return [self.cards[-1]]
        return []


class FoundationPile(Pile):
    """Foundation pile where cards are built up by suit (Ace to King)."""

    def __init__(self, x: int, y: int, suit: str):
        """
        Initialize a foundation pile.

        Args:
            x: X position
            y: Y position
            suit: The suit this foundation accepts ('hearts', 'diamonds', 'clubs', 'spades')
        """
        super().__init__(x, y)
        self.suit = suit

    def can_accept(self, card: Card, source_pile: Pile) -> bool:
        """
        Check if card can be placed on this foundation.

        Rules:
        - Must be the correct suit
        - Empty pile only accepts Ace
        - Otherwise, must be next rank in sequence (2 on A, 3 on 2, etc.)
        """
        # Must be correct suit
        if card.suit != self.suit:
            return False

        # Empty pile only accepts Ace
        if not self.cards:
            return card.rank == 'A'

        # Must be next rank in sequence
        top_card = self.get_top_card()
        return card.get_rank_value() == top_card.get_rank_value() + 1

    def update_card_positions(self):
        """All cards in foundation are at the same position, face up."""
        for card in self.cards:
            card.position = self.position
            card.face_up = True

    def get_clickable_cards(self, pos: tuple) -> List[Card]:
        """Top card can be dragged from foundation."""
        if self.cards and self.rect.collidepoint(pos):
            return [self.cards[-1]]
        return []


class TableauPile(Pile):
    """Tableau pile where main gameplay happens (7 columns)."""

    def can_accept(self, card: Card, source_pile: Pile) -> bool:
        """
        Check if card can be placed on this tableau pile.

        Rules:
        - Empty pile only accepts King
        - Otherwise, must be descending rank and alternating color
        """
        # Empty pile only accepts King
        if not self.cards:
            return card.rank == 'K'

        # Top card must be face up
        top_card = self.get_top_card()
        if not top_card.face_up:
            return False

        # Must be descending rank and alternating color
        rank_valid = card.get_rank_value() == top_card.get_rank_value() - 1
        color_valid = card.get_color() != top_card.get_color()

        return rank_valid and color_valid

    def update_card_positions(self):
        """Cards in tableau overlap vertically."""
        x, y = self.position
        for i, card in enumerate(self.cards):
            card.position = (x, y + i * CARD_OVERLAP_Y)

        # Extend pile rect to cover all stacked cards
        if self.cards:
            # Height extends from top to bottom of last card
            last_card_y = self.cards[-1].position[1]
            total_height = (last_card_y - y) + CARD_HEIGHT
            self.rect = pygame.Rect(x, y, CARD_WIDTH, total_height)
        else:
            # Empty pile - standard size
            self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    def get_clickable_cards(self, pos: tuple) -> List[Card]:
        """
        Get sequence of cards from clicked position to end.

        Returns all face-up cards from the clicked card to the bottom,
        if they form a valid descending alternating sequence.
        """
        clicked_cards = []

        # Find the clicked card (check from bottom to top to prioritize lower cards)
        for i in range(len(self.cards) - 1, -1, -1):
            card = self.cards[i]
            if not card.face_up:
                continue

            # For stacked cards, only the visible portion should be clickable
            # Last card gets full height, others get overlap height
            is_last_card = (i == len(self.cards) - 1)
            click_height = CARD_HEIGHT if is_last_card else CARD_OVERLAP_Y

            card_rect = pygame.Rect(
                card.position[0], card.position[1],
                CARD_WIDTH, click_height
            )
            if card_rect.collidepoint(pos):
                # Get all cards from this index to end
                clicked_cards = self.cards[i:]
                break

        # Validate sequence is valid before allowing drag
        if clicked_cards and self._is_valid_sequence(clicked_cards):
            return clicked_cards
        return []

    def _is_valid_sequence(self, cards: List[Card]) -> bool:
        """
        Check if cards form a valid descending alternating sequence.

        Args:
            cards: List of cards to check

        Returns:
            True if sequence is valid
        """
        if len(cards) == 1:
            return True

        for i in range(len(cards) - 1):
            current = cards[i]
            next_card = cards[i + 1]

            rank_valid = next_card.get_rank_value() == current.get_rank_value() - 1
            color_valid = next_card.get_color() != current.get_color()

            if not (rank_valid and color_valid):
                return False

        return True

    def flip_top_card(self) -> bool:
        """
        Flip the top card face up if it's face down.

        Returns:
            True if a card was flipped, False otherwise
        """
        if self.cards and not self.cards[-1].face_up:
            self.cards[-1].face_up = True
            return True
        return False
