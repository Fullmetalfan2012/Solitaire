"""UI state management for Pygame Solitaire."""

import pygame
from typing import Dict, Optional


class UIState:
    """Manages UI element rectangles and state (separates rendering from state)."""

    def __init__(self):
        """Initialize UI state storage."""
        # Settings screen - background color swatches
        self.bg_swatch_rects: Dict[str, pygame.Rect] = {}

        # Settings screen - pile outline color swatches
        self.pile_outline_rects: Dict[str, pygame.Rect] = {}

        # Settings screen - scoring factor checkboxes
        self.scoring_factor_rects: Dict[str, pygame.Rect] = {}

        # Settings screen - purge button
        self.purge_button_rect: Optional[pygame.Rect] = None

        # Menu screen - button rectangles
        self.menu_button_rects: Dict[str, pygame.Rect] = {}

    def set_bg_swatch_rect(self, key: str, rect: pygame.Rect):
        """
        Store background swatch rectangle.

        Args:
            key: Background color key
            rect: Rectangle for click detection
        """
        self.bg_swatch_rects[key] = rect

    def set_pile_outline_rect(self, key: str, rect: pygame.Rect):
        """
        Store pile outline color swatch rectangle.

        Args:
            key: Pile outline color key
            rect: Rectangle for click detection
        """
        self.pile_outline_rects[key] = rect

    def set_scoring_factor_rect(self, key: str, rect: pygame.Rect):
        """
        Store scoring factor checkbox rectangle.

        Args:
            key: Scoring factor key
            rect: Rectangle for click detection
        """
        self.scoring_factor_rects[key] = rect

    def set_purge_button_rect(self, rect: pygame.Rect):
        """
        Store purge button rectangle.

        Args:
            rect: Rectangle for click detection
        """
        self.purge_button_rect = rect

    def set_menu_button_rect(self, option: str, rect: pygame.Rect):
        """
        Store menu button rectangle.

        Args:
            option: Menu option text
            rect: Rectangle for click detection
        """
        self.menu_button_rects[option] = rect

    def clear(self):
        """Clear all stored UI rectangles."""
        self.bg_swatch_rects.clear()
        self.pile_outline_rects.clear()
        self.scoring_factor_rects.clear()
        self.purge_button_rect = None
        self.menu_button_rects.clear()

    def get_bg_swatch_at(self, pos: tuple) -> Optional[str]:
        """
        Get background swatch key at position.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Background key if clicked, None otherwise
        """
        for key, rect in self.bg_swatch_rects.items():
            if rect.collidepoint(pos):
                return key
        return None

    def get_pile_outline_at(self, pos: tuple) -> Optional[str]:
        """
        Get pile outline color key at position.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Pile outline key if clicked, None otherwise
        """
        for key, rect in self.pile_outline_rects.items():
            if rect.collidepoint(pos):
                return key
        return None

    def get_scoring_factor_at(self, pos: tuple) -> Optional[str]:
        """
        Get scoring factor key at position.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Scoring factor key if clicked, None otherwise
        """
        for key, rect in self.scoring_factor_rects.items():
            if rect.collidepoint(pos):
                return key
        return None

    def is_purge_button_clicked(self, pos: tuple) -> bool:
        """
        Check if purge button was clicked.

        Args:
            pos: Mouse position (x, y)

        Returns:
            True if purge button clicked
        """
        if self.purge_button_rect:
            return self.purge_button_rect.collidepoint(pos)
        return False

    def get_menu_option_at(self, pos: tuple) -> Optional[str]:
        """
        Get menu option at position.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Menu option text if clicked, None otherwise
        """
        for option, rect in self.menu_button_rects.items():
            if rect.collidepoint(pos):
                return option
        return None
