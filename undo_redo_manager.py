"""Undo/Redo manager for Pygame Solitaire."""

from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from move import Move
    from pile import Pile
    from game_board import GameBoard
    from scoring_engine import ScoringEngine


class UndoRedoManager:
    """Manages undo/redo functionality with unlimited history."""

    def __init__(self, game_state: 'GameBoard', scoring_engine: 'ScoringEngine'):
        """
        Initialize undo/redo manager.

        Args:
            game_state: Game state to manage undo/redo for
            scoring_engine: Scoring engine for score coordination
        """
        self.game_state = game_state
        self.scoring_engine = scoring_engine
        self.move_history: List['Move'] = []
        self.current_index: int = 0  # Points to next move to make (for redo)

    def record_move(self, move: 'Move'):
        """
        Record a move in history.

        Args:
            move: Move to record
        """
        # Clear any "future" moves if we're in the middle of history
        if self.current_index < len(self.move_history):
            self.move_history = self.move_history[:self.current_index]

        self.move_history.append(move)
        self.current_index = len(self.move_history)

    def undo(self) -> bool:
        """
        Undo the last move using move tracking.

        Returns:
            True if undo was successful, False if no moves to undo
        """
        if self.current_index == 0:
            return False

        # Decrement index to point to move to undo
        self.current_index -= 1

        # Get the move to undo
        move = self.move_history[self.current_index]

        # Undo the move
        move.undo()

        # Update card positions for rendering
        for pile in self.game_state.all_piles:
            pile.update_card_positions()

        # Restore score to previous value
        self.scoring_engine.move_value_score -= move.score_delta

        # Decrement move count
        if self.game_state.move_count > 0:
            self.game_state.move_count -= 1

        return True

    def redo(self) -> bool:
        """
        Redo the next move using move tracking.

        Returns:
            True if redo was successful, False if no moves to redo
        """
        if self.current_index >= len(self.move_history):
            return False

        # Get the move to redo
        move = self.move_history[self.current_index]

        # Re-execute the move
        move.execute()

        # Reapply score change
        self.scoring_engine.move_value_score += move.score_delta

        # Increment move count
        self.game_state.move_count += 1

        # Increment index
        self.current_index += 1

        # Update card positions for rendering
        for pile in self.game_state.all_piles:
            pile.update_card_positions()

        return True

    def can_undo(self) -> bool:
        """
        Check if undo is available.

        Returns:
            True if there are moves to undo
        """
        return self.current_index > 0

    def can_redo(self) -> bool:
        """
        Check if redo is available.

        Returns:
            True if there are moves to redo
        """
        return self.current_index < len(self.move_history)

    def get_undo_count(self) -> int:
        """
        Get number of undo operations available.

        Returns:
            Number of moves that can be undone
        """
        return self.current_index

    def get_redo_count(self) -> int:
        """
        Get number of redo operations available.

        Returns:
            Number of moves that can be redone
        """
        return len(self.move_history) - self.current_index

    def clear(self):
        """Clear all move history."""
        self.move_history = []
        self.current_index = 0

    def to_dict(self, all_piles: List['Pile']) -> Dict[str, Any]:
        """
        Serialize undo/redo manager state to dictionary.

        Args:
            all_piles: All piles (for move serialization)

        Returns:
            Dictionary containing serializable state
        """
        from move import Move

        return {
            'move_history': [move.to_dict(all_piles) for move in self.move_history],
            'current_index': self.current_index
        }

    @staticmethod
    def from_dict(data: Dict[str, Any], all_piles: List['Pile'], game_state: 'GameBoard', scoring_engine: 'ScoringEngine' = None) -> 'UndoRedoManager':
        """
        Deserialize undo/redo manager from dictionary.

        Args:
            data: Serialized state dictionary
            all_piles: All piles (for move deserialization)
            game_state: Game state reference
            scoring_engine: Scoring engine reference (optional)

        Returns:
            Restored UndoRedoManager instance
        """
        from move import Move

        manager = UndoRedoManager(game_state, scoring_engine)
        manager.move_history = [
            Move.from_dict(move_data, all_piles)
            for move_data in data.get('move_history', [])
        ]
        manager.current_index = data.get('current_index', 0)
        return manager
