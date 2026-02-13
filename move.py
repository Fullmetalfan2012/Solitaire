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
        card_states: Optional[List[bool]] = None,
        score_delta: int = 0
    ):
        """
        Initialize a move.

        Args:
            from_pile: Source pile
            to_pile: Destination pile
            cards: Cards that were moved (in order)
            revealed_card: Card that was revealed as result of move (if any)
            card_states: Face-up states of moved cards before move (for undo)
            score_delta: Score change caused by this move (for undo/redo)
        """
        self.from_pile = from_pile
        self.to_pile = to_pile
        self.cards = cards
        self.revealed_card = revealed_card
        # Store original face-up states for undo
        self.card_states = card_states if card_states else [card.face_up for card in cards]
        # Store score change for proper undo/redo
        self.score_delta = score_delta

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

    def to_dict(self, all_piles: List['Pile']) -> dict:
        """
        Serialize move to dictionary for saving.

        Args:
            all_piles: List of all piles to use for pile indexing

        Returns:
            Dictionary representation of move with pile indices and card identifiers
        """
        return {
            'from_pile_index': all_piles.index(self.from_pile),
            'to_pile_index': all_piles.index(self.to_pile),
            'cards': [(card.rank, card.suit) for card in self.cards],
            'card_states': self.card_states,
            'revealed_card': (self.revealed_card.rank, self.revealed_card.suit) if self.revealed_card else None,
            'score_delta': self.score_delta
        }

    @classmethod
    def from_dict(cls, data: dict, all_piles: List['Pile']) -> 'Move':
        """
        Deserialize move from dictionary.

        Args:
            data: Dictionary representation of move
            all_piles: List of all piles to use for pile indexing

        Returns:
            Reconstructed Move object
        """
        from_pile = all_piles[data['from_pile_index']]
        to_pile = all_piles[data['to_pile_index']]

        # Find card objects by rank+suit
        cards = []
        for rank, suit in data['cards']:
            # Search through all piles for matching card
            found = False
            for pile in all_piles:
                for card in pile.cards:
                    if card.rank == rank and card.suit == suit:
                        cards.append(card)
                        found = True
                        break
                if found:
                    break

        # Find revealed card if any
        revealed_card = None
        if data['revealed_card']:
            rev_rank, rev_suit = data['revealed_card']
            for pile in all_piles:
                for card in pile.cards:
                    if card.rank == rev_rank and card.suit == rev_suit:
                        revealed_card = card
                        break
                if revealed_card:
                    break

        return cls(from_pile, to_pile, cards, revealed_card, data.get('card_states'), data.get('score_delta', 0))

    def __repr__(self) -> str:
        """String representation for debugging."""
        cards_str = f"{len(self.cards)} card(s)"
        revealed_str = f", revealed {self.revealed_card}" if self.revealed_card else ""
        return f"Move({self.from_pile} -> {self.to_pile}: {cards_str}{revealed_str})"
