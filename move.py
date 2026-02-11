"""Move tracking for undo/redo system using Command Pattern."""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from card import Card
    from pile import Pile


class Move:
    """
    Represents a single move in the game.

    Stores enough information to execute and undo the move,
    including tracking which card (if any) was revealed.
    """

    def __init__(
        self,
        from_pile: 'Pile',
        to_pile: 'Pile',
        cards: List['Card'],
        revealed_card: Optional['Card'] = None,
        card_states: Optional[List[bool]] = None
    ):
        """
        Initialize a move.

        Args:
            from_pile: Source pile
            to_pile: Destination pile
            cards: Cards that were moved (in order)
            revealed_card: Card that was revealed as result of move (if any)
            card_states: Face-up states of moved cards before move (for undo)
        """
        self.from_pile = from_pile
        self.to_pile = to_pile
        self.cards = cards
        self.revealed_card = revealed_card
        # Store original face-up states for undo
        self.card_states = card_states if card_states else [card.face_up for card in cards]

    def execute(self):
        """Execute this move (move cards from source to destination)."""
        # Remove cards from source
        for card in self.cards:
            if card in self.from_pile.cards:
                self.from_pile.cards.remove(card)

        # Add cards to destination
        self.to_pile.cards.extend(self.cards)

        # Reveal card if one was revealed during this move
        if self.revealed_card:
            self.revealed_card.face_up = True

    def undo(self):
        """Undo this move (move cards back, restore flip states)."""
        # Remove cards from destination
        for card in self.cards:
            if card in self.to_pile.cards:
                self.to_pile.cards.remove(card)

        # Add cards back to source and restore their face-up states
        self.from_pile.cards.extend(self.cards)
        for card, was_face_up in zip(self.cards, self.card_states):
            card.face_up = was_face_up

        # Hide card that was revealed during this move
        if self.revealed_card:
            self.revealed_card.face_up = False

    def to_dict(self) -> dict:
        """
        Serialize move to dictionary for saving.

        Returns:
            Dictionary representation of move
        """
        return {
            'from_pile_id': id(self.from_pile),
            'to_pile_id': id(self.to_pile),
            'card_ids': [id(card) for card in self.cards],
            'revealed_card_id': id(self.revealed_card) if self.revealed_card else None
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        cards_str = f"{len(self.cards)} card(s)"
        revealed_str = f", revealed {self.revealed_card}" if self.revealed_card else ""
        return f"Move({self.from_pile} -> {self.to_pile}: {cards_str}{revealed_str})"
