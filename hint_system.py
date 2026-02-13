"""Hint system for Pygame Solitaire."""

from typing import List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from card import Card
    from pile import Pile, TableauPile, WastePile, FoundationPile
    from game_board import GameBoard


class HintSystem:
    """Manages hint functionality (valid move detection and highlighting)."""

    def __init__(self, game_state: 'GameBoard', max_hints: int = 3):
        """
        Initialize hint system.

        Args:
            game_state: Game state to analyze for valid moves
            max_hints: Maximum number of hints available per game
        """
        self.game_state = game_state
        self.hints_remaining: int = max_hints
        self.highlighted_targets: List['Pile'] = []

    def get_valid_moves(self) -> List[Tuple['Card', 'Pile', 'Pile']]:
        """
        Get all valid moves in current state for hint system.

        Returns:
            List of (card, source_pile, target_pile) tuples representing legal moves
        """
        from pile import TableauPile, WastePile

        valid_moves = []

        # Check all possible sources
        source_piles = [self.game_state.waste] + self.game_state.tableaus

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
                    for foundation in self.game_state.foundations:
                        if foundation.can_accept(first_card, source):
                            valid_moves.append((first_card, source, foundation))

                    # Try tableaus (can move sequences)
                    for tableau in self.game_state.tableaus:
                        if tableau != source and tableau.can_accept(first_card, source):
                            valid_moves.append((first_card, source, tableau))

            # For waste, only top card
            elif isinstance(source, WastePile):
                if source.cards:
                    top_card = source.cards[-1]

                    # Try foundations
                    for foundation in self.game_state.foundations:
                        if foundation.can_accept(top_card, source):
                            valid_moves.append((top_card, source, foundation))

                    # Try tableaus
                    for tableau in self.game_state.tableaus:
                        if tableau.can_accept(top_card, source):
                            valid_moves.append((top_card, source, tableau))

        return valid_moves

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
        self.highlighted_targets = list(set(target for _, _, target in valid_moves))

        return True

    def clear_highlights(self):
        """Clear hint highlights."""
        self.highlighted_targets = []

    def to_dict(self) -> Dict:
        """
        Serialize hint system state to dictionary.

        Returns:
            Dictionary containing serializable state
        """
        return {
            'hints_remaining': self.hints_remaining
        }

    @staticmethod
    def from_dict(data: Dict, game_state: 'GameBoard') -> 'HintSystem':
        """
        Deserialize hint system from dictionary.

        Args:
            data: Serialized state dictionary
            game_state: Game state reference

        Returns:
            Restored HintSystem instance
        """
        hint_system = HintSystem(game_state)
        hint_system.hints_remaining = data.get('hints_remaining', 3)
        return hint_system
