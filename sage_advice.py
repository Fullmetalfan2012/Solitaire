"""Sage advice system for Pygame Solitaire."""

import json
import os
import random
import time
from typing import Dict, List, Optional


class SageAdviceSystem:
    """Manages sage advice display (comedic animal facts)."""

    def __init__(self, advice_file: str = 'data/sage_advice.json'):
        """
        Initialize sage advice system.

        Args:
            advice_file: Path to JSON file containing advice categories
        """
        self.advice_text: Optional[str] = None
        self.advice_timer: float = 0.0
        self._wisdom: Dict[str, List[str]] = {}
        self._load_advice(advice_file)

    def _load_advice(self, advice_file: str):
        """
        Load sage advice from JSON file.

        Args:
            advice_file: Path to advice JSON file
        """
        try:
            advice_path = os.path.join(os.path.dirname(__file__), advice_file)
            with open(advice_path, 'r') as f:
                self._wisdom = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load sage advice: {e}")
            # Fallback to empty dict
            self._wisdom = {}

    def get_random_advice(self) -> str:
        """
        Get random sage advice (unlimited, comedic animal facts).

        Returns:
            Random useless animal wisdom
        """
        if not self._wisdom:
            return "No wisdom available. The universe is silent."

        # Flatten all wisdom categories into one pool
        all_wisdom = [advice for category in self._wisdom.values() for advice in category]

        if not all_wisdom:
            return "No wisdom available. The universe is silent."

        return random.choice(all_wisdom)

    def show_advice(self):
        """Display sage advice on screen for a few seconds."""
        self.advice_text = self.get_random_advice()
        self.advice_timer = time.time()

    def update(self):
        """Update sage advice timer and clear if expired."""
        if self.advice_text and (time.time() - self.advice_timer) > 5.0:
            self.advice_text = None

    def is_visible(self) -> bool:
        """
        Check if advice is currently visible.

        Returns:
            True if advice is being displayed
        """
        return self.advice_text is not None

    def clear(self):
        """Clear currently displayed advice."""
        self.advice_text = None
        self.advice_timer = 0.0
