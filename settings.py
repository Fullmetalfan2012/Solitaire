"""User settings management for Pygame Solitaire."""

import json
import os
from typing import Any, Dict
from constants import DEFAULT_SCORING_FACTORS


# Default settings
DEFAULT_SETTINGS = {
    'background_color': 'green',  # green, blue, grey, gradient_sunset, gradient_ocean, gradient_forest
    'pile_outline_color': 'green',  # green, white, gold, blue, red
    'time_enabled': DEFAULT_SCORING_FACTORS['time_enabled'],
    'moves_enabled': DEFAULT_SCORING_FACTORS['moves_enabled'],
    'values_enabled': DEFAULT_SCORING_FACTORS['values_enabled'],
}


class Settings:
    """Manages user settings with file persistence."""

    SETTINGS_FILE = 'game_settings.json'

    def __init__(self):
        """Initialize settings, loading from file if exists."""
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        """Load settings from file."""
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except (json.JSONDecodeError, IOError):
                # If file is corrupt, use defaults
                pass

    def save(self):
        """Save settings to file."""
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError:
            pass  # Fail silently if can't save

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value and save."""
        self.settings[key] = value
        self.save()

    def get_background_color(self) -> str:
        """Get current background color setting."""
        return self.settings.get('background_color', 'green')

    def set_background_color(self, color: str):
        """Set background color setting."""
        self.set('background_color', color)

    def cycle_background_color(self):
        """Cycle to next background color option."""
        colors = ['green', 'blue', 'grey', 'gradient_sunset', 'gradient_ocean', 'gradient_forest']
        current = self.get_background_color()
        try:
            current_index = colors.index(current)
            next_index = (current_index + 1) % len(colors)
        except ValueError:
            next_index = 0
        self.set_background_color(colors[next_index])

    def get_scoring_factors(self) -> Dict[str, bool]:
        """Get enabled scoring factors."""
        return {
            'time_enabled': self.settings.get('time_enabled', True),
            'moves_enabled': self.settings.get('moves_enabled', True),
            'values_enabled': self.settings.get('values_enabled', True),
        }

    def set_scoring_factor(self, factor: str, enabled: bool):
        """Toggle a scoring factor on/off."""
        if factor in ['time_enabled', 'moves_enabled', 'values_enabled']:
            self.set(factor, enabled)

    def get_pile_outline_color(self) -> str:
        """Get current pile outline color setting."""
        return self.settings.get('pile_outline_color', 'green')

    def set_pile_outline_color(self, color: str):
        """Set pile outline color setting."""
        self.set('pile_outline_color', color)
