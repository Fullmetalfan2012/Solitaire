"""Scoring engine for Pygame Solitaire."""

import time
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pile import Pile, FoundationPile, WastePile, TableauPile
    from card import Card


class ScoringEngine:
    """Manages score calculation and tracking."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize scoring engine.

        Args:
            config: Scoring configuration (optional, uses defaults if not provided)
        """
        self.start_time: float = 0.0
        self.move_value_score: int = 0

        # Scoring configuration
        self.config = config or {
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

        # Scoring factors (toggleable)
        self.time_enabled: bool = True
        self.moves_enabled: bool = True
        self.values_enabled: bool = True

    def reset(self):
        """Reset scoring for a new game."""
        self.start_time = time.time()
        self.move_value_score = 0

    def record_move(self, source: 'Pile', target: 'Pile', cards: list, flipped_card: bool = False) -> int:
        """
        Record a move for scoring purposes.

        Args:
            source: Source pile
            target: Target pile
            cards: Cards that were moved
            flipped_card: Whether a tableau card was flipped as result

        Returns:
            Score delta (points gained/lost from this move)
        """
        from pile import FoundationPile, WastePile

        if not self.config['value_enabled'] or not self.values_enabled:
            return 0

        score_delta = 0

        # Award points for moving to foundation
        if isinstance(target, FoundationPile):
            score_delta += self.config['to_foundation']

        # Bonus for moving from waste pile
        if isinstance(source, WastePile):
            score_delta += self.config['from_waste']

        # Bonus for flipping a tableau card
        if flipped_card:
            score_delta += self.config['flip_card']

        self.move_value_score += score_delta
        return score_delta

    def record_stock_recycle(self) -> int:
        """
        Record a stock pile recycle action.

        Returns:
            Score delta (penalty)
        """
        if not self.config['value_enabled'] or not self.values_enabled:
            return 0

        penalty = self.config['stock_recycle']
        self.move_value_score += penalty
        return penalty

    def get_current_score(self, move_count: int, elapsed_time: float = None) -> Dict[str, Any]:
        """
        Calculate current score based on enabled scoring factors.

        Args:
            move_count: Current number of moves made
            elapsed_time: Elapsed time (if None, calculated from start_time)

        Returns:
            Dictionary with score components, total, and mode info
        """
        from constants import get_scoring_mode_name

        if elapsed_time is None:
            elapsed_time = time.time() - self.start_time

        # Time component (bonus for fast play) - only if enabled
        time_score = 0
        if self.time_enabled and self.config['time_enabled']:
            time_bonus_base = self.config['time_bonus_base']
            time_multiplier = self.config['time_multiplier']
            time_score = max(0, time_bonus_base - int(elapsed_time * time_multiplier))

        # Move efficiency penalty - only if enabled
        move_penalty = 0
        if self.moves_enabled and self.config['moves_enabled']:
            move_penalty = move_count * self.config['move_penalty']

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
            'move_count': move_count,
            'elapsed_time': elapsed_time,
            'scoring_mode': mode_name,
            'time_enabled': self.time_enabled,
            'moves_enabled': self.moves_enabled,
            'values_enabled': self.values_enabled,
        }

    def set_factor(self, factor_name: str, enabled: bool):
        """
        Set a scoring factor (replaces setattr pattern).

        Args:
            factor_name: Name of factor ('time_enabled', 'moves_enabled', 'values_enabled')
            enabled: Whether the factor should be enabled
        """
        if factor_name in ('time_enabled', 'moves_enabled', 'values_enabled'):
            setattr(self, factor_name, enabled)
        else:
            raise ValueError(f"Invalid scoring factor: {factor_name}")

    def get_factor(self, factor_name: str) -> bool:
        """
        Get a scoring factor value.

        Args:
            factor_name: Name of factor

        Returns:
            Whether the factor is enabled
        """
        if factor_name in ('time_enabled', 'moves_enabled', 'values_enabled'):
            return getattr(self, factor_name, True)
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize scoring engine state to dictionary.

        Returns:
            Dictionary containing serializable state
        """
        return {
            'start_time': self.start_time,
            'move_value_score': self.move_value_score,
            'config': self.config,
            'time_enabled': self.time_enabled,
            'moves_enabled': self.moves_enabled,
            'values_enabled': self.values_enabled,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ScoringEngine':
        """
        Deserialize scoring engine from dictionary.

        Args:
            data: Serialized state dictionary

        Returns:
            Restored ScoringEngine instance
        """
        engine = ScoringEngine(data.get('config'))
        engine.start_time = data.get('start_time', time.time())
        engine.move_value_score = data.get('move_value_score', 0)
        engine.time_enabled = data.get('time_enabled', True)
        engine.moves_enabled = data.get('moves_enabled', True)
        engine.values_enabled = data.get('values_enabled', True)
        return engine
