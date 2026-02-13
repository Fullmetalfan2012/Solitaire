"""Save/load coordinator for Pygame Solitaire with v1/v2 format support."""

import json
import os
import time
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game_board import GameBoard
    from scoring_engine import ScoringEngine
    from hint_system import HintSystem
    from undo_redo_manager import UndoRedoManager


class SaveLoadCoordinator:
    """Coordinates saving/loading game state across all subsystems."""

    SAVE_VERSION = 2  # Current save format version

    def __init__(self, game_state: 'GameBoard', scoring_engine: 'ScoringEngine',
                 hint_system: 'HintSystem', undo_manager: 'UndoRedoManager'):
        """
        Initialize save/load coordinator.

        Args:
            game_state: Game state to save/load
            scoring_engine: Scoring engine for game scoring
            hint_system: Hint system for tracking hints
            undo_manager: Undo/redo manager for move history
        """
        self.game_state = game_state
        self.scoring_engine = scoring_engine
        self.hint_system = hint_system
        self.undo_manager = undo_manager

    def save_game(self, filename: str = "savegame.json") -> bool:
        """
        Save current game state to file (v2 format).

        Args:
            filename: Path to save file

        Returns:
            True if save successful, False otherwise
        """
        try:
            # Build v2 save format
            save_data = {
                'version': self.SAVE_VERSION,
                'saved_at': time.time(),
                'game_board': self._serialize_game_board(),
            }

            # Add subsystem data
            save_data['scoring_engine'] = self.scoring_engine.to_dict()
            save_data['hint_system'] = self.hint_system.to_dict()
            save_data['undo_manager'] = self.undo_manager.to_dict(self.game_state.all_piles)

            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, filename: str = "savegame.json") -> bool:
        """
        Load game state from file (supports v1 and v2 formats).

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

            # Detect version and load accordingly
            version = save_data.get('version', 1)  # Default to v1 if no version field

            if version == 2:
                return self._load_v2_format(save_data)
            else:
                return self._load_v1_format_legacy(save_data)

        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def _serialize_game_board(self) -> Dict[str, Any]:
        """
        Serialize game board state.

        Returns:
            Dictionary with game board data
        """
        from pile import StockPile, WastePile, FoundationPile, TableauPile

        board_data = {
            'move_count': self.game_state.move_count,
            'stock': self._serialize_pile(self.game_state.stock),
            'waste': self._serialize_pile(self.game_state.waste),
            'foundations': [self._serialize_pile(f) for f in self.game_state.foundations],
            'tableaus': [self._serialize_pile(t) for t in self.game_state.tableaus],
        }

        return board_data

    def _serialize_pile(self, pile) -> Dict[str, Any]:
        """
        Serialize a pile to JSON-compatible dict.

        Args:
            pile: Pile to serialize

        Returns:
            Dictionary with pile data
        """
        from pile import FoundationPile

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

    def _deserialize_pile(self, pile_data: Dict[str, Any], pile_class: type):
        """
        Deserialize a pile from JSON dict.

        Args:
            pile_data: Pile data dictionary
            pile_class: Pile class to instantiate

        Returns:
            Restored pile instance
        """
        from card import Card
        from pile import FoundationPile

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

    def _load_v2_format(self, save_data: Dict[str, Any]) -> bool:
        """
        Load v2 format save file.

        Args:
            save_data: Loaded save data dictionary

        Returns:
            True if successful
        """
        from pile import StockPile, WastePile, FoundationPile, TableauPile

        # Restore game board
        board_data = save_data['game_board']
        self.game_state.move_count = board_data['move_count']

        # Restore piles
        self.game_state.stock = self._deserialize_pile(board_data['stock'], StockPile)
        self.game_state.waste = self._deserialize_pile(board_data['waste'], WastePile)
        self.game_state.foundations = [
            self._deserialize_pile(f, FoundationPile)
            for f in board_data['foundations']
        ]
        self.game_state.tableaus = [
            self._deserialize_pile(t, TableauPile)
            for t in board_data['tableaus']
        ]

        # Rebuild all_piles list
        self.game_state.all_piles = [self.game_state.stock, self.game_state.waste] + \
                                      self.game_state.foundations + self.game_state.tableaus

        # Restore subsystems
        if 'scoring_engine' in save_data and self.scoring_engine:
            from scoring_engine import ScoringEngine
            restored_engine = ScoringEngine.from_dict(save_data['scoring_engine'])
            # Copy state to existing scoring_engine
            self.scoring_engine.start_time = restored_engine.start_time
            self.scoring_engine.move_value_score = restored_engine.move_value_score
            self.scoring_engine.time_enabled = restored_engine.time_enabled
            self.scoring_engine.moves_enabled = restored_engine.moves_enabled
            self.scoring_engine.values_enabled = restored_engine.values_enabled

        if 'hint_system' in save_data and self.hint_system:
            from hint_system import HintSystem
            restored_hints = HintSystem.from_dict(save_data['hint_system'], self.game_state)
            self.hint_system.hints_remaining = restored_hints.hints_remaining

        if 'undo_manager' in save_data and self.undo_manager:
            from undo_redo_manager import UndoRedoManager
            restored_undo = UndoRedoManager.from_dict(
                save_data['undo_manager'],
                self.game_state.all_piles,
                self.game_state,
                self.scoring_engine
            )
            self.undo_manager.move_history = restored_undo.move_history
            self.undo_manager.current_index = restored_undo.current_index

        return True

    def _load_v1_format_legacy(self, save_data: Dict[str, Any]) -> bool:
        """
        Load v1 format save file (backward compatibility).

        Maps old monolithic structure to new subsystems.

        Args:
            save_data: Loaded save data dictionary

        Returns:
            True if successful
        """
        from pile import StockPile, WastePile, FoundationPile, TableauPile
        from move import Move

        # Restore game board state
        self.game_state.move_count = save_data['move_count']

        # Restore scoring state
        self.scoring_engine.start_time = save_data['start_time']
        self.scoring_engine.move_value_score = save_data['move_value_score']
        self.scoring_engine.config = save_data.get('scoring_config', self.scoring_engine.config)
        self.scoring_engine.time_enabled = save_data.get('time_enabled', True)
        self.scoring_engine.moves_enabled = save_data.get('moves_enabled', True)
        self.scoring_engine.values_enabled = save_data.get('values_enabled', True)

        # Restore hint system state
        self.hint_system.hints_remaining = save_data.get('hints_remaining', 3)

        # Restore piles
        self.game_state.stock = self._deserialize_pile(save_data['stock'], StockPile)
        self.game_state.waste = self._deserialize_pile(save_data['waste'], WastePile)
        self.game_state.foundations = [
            self._deserialize_pile(f, FoundationPile)
            for f in save_data['foundations']
        ]
        self.game_state.tableaus = [
            self._deserialize_pile(t, TableauPile)
            for t in save_data['tableaus']
        ]

        # Rebuild all_piles list
        self.game_state.all_piles = [self.game_state.stock, self.game_state.waste] + \
                                      self.game_state.foundations + self.game_state.tableaus

        # Restore move history
        if 'move_history' in save_data:
            self.undo_manager.move_history = [
                Move.from_dict(move_data, self.game_state.all_piles)
                for move_data in save_data['move_history']
            ]
            self.undo_manager.current_index = save_data.get('current_move_index', 0)

        return True

    @staticmethod
    def save_exists(filename: str = "savegame.json") -> bool:
        """
        Check if a save file exists.

        Args:
            filename: Path to save file

        Returns:
            True if file exists
        """
        return os.path.exists(filename)
