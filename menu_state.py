"""Menu system for Pygame Solitaire."""

from enum import Enum
from typing import Optional


class MenuScreen(Enum):
    """Different menu screens."""
    MAIN_MENU = "main_menu"
    HIGH_SCORES = "high_scores"
    SETTINGS = "settings"
    PAUSE_MENU = "pause_menu"
    NONE = "none"  # In-game


class MenuState:
    """Manages menu navigation and state."""

    def __init__(self):
        """Initialize menu state."""
        self.current_screen = MenuScreen.MAIN_MENU
        self.selected_option = 0
        self.menu_options = {
            MenuScreen.MAIN_MENU: [],
            MenuScreen.HIGH_SCORES: ["Back"],
            MenuScreen.SETTINGS: ["Back"],
            MenuScreen.PAUSE_MENU: ["Resume", "Save & Quit", "Restart", "Main Menu"]
        }
        self.update_main_menu_options(save_exists=False)

    def update_main_menu_options(self, save_exists: bool):
        """Update main menu options based on whether save exists."""
        if save_exists:
            self.menu_options[MenuScreen.MAIN_MENU] = [
                "New Game", "Continue", "High Scores", "Settings", "Quit"
            ]
        else:
            self.menu_options[MenuScreen.MAIN_MENU] = [
                "New Game", "High Scores", "Settings", "Quit"
            ]

    def get_options(self) -> list:
        """Get current menu options."""
        return self.menu_options.get(self.current_screen, [])

    def select_next(self):
        """Move selection down."""
        options = self.get_options()
        if options:
            self.selected_option = (self.selected_option + 1) % len(options)

    def select_previous(self):
        """Move selection up."""
        options = self.get_options()
        if options:
            self.selected_option = (self.selected_option - 1) % len(options)

    def get_selected_option(self) -> Optional[str]:
        """Get currently selected option text."""
        options = self.get_options()
        if options and 0 <= self.selected_option < len(options):
            return options[self.selected_option]
        return None

    def navigate_to(self, screen: MenuScreen):
        """Navigate to a different menu screen."""
        self.current_screen = screen
        self.selected_option = 0

    def is_in_game(self) -> bool:
        """Check if currently in-game (not in menu)."""
        return self.current_screen == MenuScreen.NONE
