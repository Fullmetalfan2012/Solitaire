"""Statistics tracking for Pygame Solitaire."""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class StatsTracker:
    """Manages game statistics and high scores."""

    def __init__(self, filename: str = "scores.jsonl"):
        """
        Initialize stats tracker.

        Args:
            filename: Path to JSONL file for storing scores
        """
        self.filename = filename
        self.scores: List[Dict] = []
        self.load_scores()

    def load_scores(self):
        """Load scores from JSONL file."""
        if not os.path.exists(self.filename):
            self.scores = []
            return

        self.scores = []
        try:
            with open(self.filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.scores.append(json.loads(line))
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading scores: {e}")
            self.scores = []

    def save_score(self, name: str, score_data: Dict) -> Dict:
        """
        Save a new score to the file.

        Args:
            name: Player name (3 letters)
            score_data: Score breakdown from game_state.get_current_score()

        Returns:
            The complete score entry that was saved
        """
        entry = {
            'name': name.upper(),
            'total_score': score_data['total'],
            'move_value': score_data['move_value'],
            'time_bonus': score_data['time_bonus'],
            'move_penalty': score_data['move_penalty'],
            'move_count': score_data['move_count'],
            'elapsed_time': score_data['elapsed_time'],
            'timestamp': datetime.now().isoformat()
        }

        # Append to file
        try:
            with open(self.filename, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            self.scores.append(entry)
        except IOError as e:
            print(f"Error saving score: {e}")

        return entry

    def get_statistics(self) -> Dict:
        """
        Calculate statistics from all saved scores.

        Returns:
            Dictionary with averages and best scores
        """
        if not self.scores:
            return {
                'total_games': 0,
                'avg_time': 0,
                'avg_moves': 0,
                'avg_score': 0,
                'best_time': None,
                'best_moves': None,
                'best_score': None
            }

        total_games = len(self.scores)
        avg_time = sum(s['elapsed_time'] for s in self.scores) / total_games
        avg_moves = sum(s['move_count'] for s in self.scores) / total_games
        avg_score = sum(s['total_score'] for s in self.scores) / total_games

        # Find best scores
        best_time = min(self.scores, key=lambda s: s['elapsed_time'])
        best_moves = min(self.scores, key=lambda s: s['move_count'])
        best_score = max(self.scores, key=lambda s: s['total_score'])

        return {
            'total_games': total_games,
            'avg_time': avg_time,
            'avg_moves': avg_moves,
            'avg_score': avg_score,
            'best_time': best_time,
            'best_moves': best_moves,
            'best_score': best_score
        }

    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """
        Get top scores sorted by total score.

        Args:
            limit: Maximum number of scores to return

        Returns:
            List of top score entries
        """
        sorted_scores = sorted(
            self.scores,
            key=lambda s: s['total_score'],
            reverse=True
        )
        return sorted_scores[:limit]

    def get_fastest_times(self, limit: int = 10) -> List[Dict]:
        """
        Get fastest completion times.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of fastest time entries
        """
        sorted_times = sorted(
            self.scores,
            key=lambda s: s['elapsed_time']
        )
        return sorted_times[:limit]

    def get_fewest_moves(self, limit: int = 10) -> List[Dict]:
        """
        Get games with fewest moves.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of fewest moves entries
        """
        sorted_moves = sorted(
            self.scores,
            key=lambda s: s['move_count']
        )
        return sorted_moves[:limit]
