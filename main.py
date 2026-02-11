"""Main game loop for Pygame Solitaire."""

import pygame
import time
from card import Card
from game_state import GameState
from renderer import Renderer
from input_handler import InputHandler
from stats import StatsTracker
from settings import Settings
from menu_state import MenuState, MenuScreen
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class SolitaireGame:
    """Main game controller."""

    def __init__(self):
        """Initialize the game."""
        # Initialize pygame
        pygame.init()

        # Create display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Solitaire")

        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()

        # Load card images once at startup
        Card.load_images()

        # Initialize game components
        self.game_state = GameState()
        self.renderer = Renderer(self.screen, self.game_state)
        self.input_handler = InputHandler(self.game_state)
        self.stats_tracker = StatsTracker()
        self.settings = Settings()
        self.menu_state = MenuState()

        # Apply settings
        self.renderer.set_background(self.settings.get_background_color())

        # Update main menu based on save file existence
        self.menu_state.update_main_menu_options(GameState.save_exists())

        # Game state flags
        self.running = True
        self.game_won = False
        self.entering_name = False
        self.player_name = ""
        self.final_score = None

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()

    def handle_events(self):
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Window close button clicked
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_state.is_in_game():
                    # In-game mouse handling
                    if not self.game_won and not self.entering_name:
                        self.input_handler.handle_mouse_down(event.pos)
                else:
                    # Menu mouse handling
                    self.handle_menu_click(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                if self.menu_state.is_in_game():
                    # In-game mouse motion
                    if not self.game_won and not self.entering_name:
                        self.input_handler.handle_mouse_motion(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.menu_state.is_in_game():
                    # In-game mouse release
                    if not self.game_won and not self.entering_name:
                        self.input_handler.handle_mouse_up(event.pos)

                        # Clear hint highlights after move
                        self.game_state.clear_hints()

                        # Check if auto-finish is available
                        if not self.game_state.auto_finishing:
                            self.game_state.auto_finish_available = self.game_state.check_auto_finish_available()

                        # Check if game is won after the move
                        if self.game_state.check_win():
                            self.game_won = True
                            self.entering_name = True
                            self.player_name = ""
                            self.final_score = self.game_state.calculate_final_score()

            elif event.type == pygame.KEYDOWN:
                if self.entering_name:
                    # Handle name entry
                    self.handle_name_entry(event)
                elif not self.menu_state.is_in_game():
                    # Menu keyboard handling
                    self.handle_menu_keyboard(event)
                else:
                    # In-game keyboard handling
                    self.handle_game_keyboard(event)

    def update(self):
        """Update game state."""
        # Update sage advice timer
        self.game_state.update_sage_advice()

        # Update snap-back animation
        self.input_handler.update_snap_back()

        # Handle auto-finish animation
        if self.game_state.auto_finishing and not self.game_won:
            # Check if current move animation is complete (0.3s per move)
            if self.game_state.auto_finish_card:
                elapsed = time.time() - self.game_state.auto_finish_start_time
                if elapsed > 0.3:  # Animation duration
                    # Complete the move
                    self.game_state.complete_auto_finish_move()

                    # Check if game is won
                    if self.game_state.check_win():
                        self.game_state.auto_finishing = False
                        self.game_won = True
                        self.entering_name = True
                        self.player_name = ""
                        self.final_score = self.game_state.calculate_final_score()
                    else:
                        # Start next move
                        if not self.game_state.start_auto_finish_move():
                            # No more moves but not won? (shouldn't happen)
                            self.game_state.auto_finishing = False
            else:
                # Start first move
                if not self.game_state.start_auto_finish_move():
                    self.game_state.auto_finishing = False

    def render(self):
        """Render the game."""
        if self.entering_name:
            # Show name entry screen (skip game board to prevent flicker)
            self.renderer.render_name_entry(self.final_score, self.player_name)
        elif self.menu_state.is_in_game():
            # Render game
            self.renderer.render(self.input_handler)
        else:
            # Render menu (pass input_handler for pause menu to show game underneath)
            self.renderer.render_menu(self.menu_state, self.stats_tracker, self.input_handler)

    def handle_game_keyboard(self, event):
        """Handle keyboard input during gameplay."""
        if event.key == pygame.K_ESCAPE:
            # Pause game
            self.menu_state.navigate_to(MenuScreen.PAUSE_MENU)
        elif event.key == pygame.K_h:
            # Show hint
            if self.game_state.use_hint():
                print(f"Hint used! ({self.game_state.hints_remaining} hints remaining)")
            else:
                print("No hints remaining!")
        elif event.key == pygame.K_a:
            # Show sage advice
            self.game_state.show_sage_advice()
            print("Sage advice displayed")
        elif event.key == pygame.K_u:
            # Undo last move
            if self.game_state.undo():
                print(f"Undo successful! ({self.game_state.get_undo_count()} undos, {self.game_state.get_redo_count()} redos available)")
            else:
                print("No moves to undo")
        elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            # Redo next move (Ctrl+Y)
            if self.game_state.redo():
                print(f"Redo successful! ({self.game_state.get_undo_count()} undos, {self.game_state.get_redo_count()} redos available)")
            else:
                print("No moves to redo")
        elif event.key == pygame.K_r:
            # Reset game
            self.reset_game()
        elif event.key == pygame.K_f:
            # Start auto-finish if available
            if self.game_state.auto_finish_available and not self.game_state.auto_finishing:
                self.game_state.auto_finishing = True
                self.game_state.auto_finish_available = False
                print("Auto-finish started!")

    def handle_menu_keyboard(self, event):
        """Handle keyboard input in menus."""
        if event.key == pygame.K_ESCAPE:
            # Back/Resume
            if self.menu_state.current_screen == MenuScreen.PAUSE_MENU:
                self.menu_state.navigate_to(MenuScreen.NONE)
            elif self.menu_state.current_screen in [MenuScreen.HIGH_SCORES, MenuScreen.SETTINGS]:
                self.menu_state.navigate_to(MenuScreen.MAIN_MENU)
                self.menu_state.update_main_menu_options(GameState.save_exists())
        elif event.key == pygame.K_UP:
            self.menu_state.select_previous()
        elif event.key == pygame.K_DOWN:
            self.menu_state.select_next()
        elif event.key == pygame.K_RETURN:
            self.execute_menu_action()

    def handle_menu_click(self, pos):
        """Handle mouse click in menu."""
        # Check for settings screen clicks (background and scoring mode)
        if self.menu_state.current_screen == MenuScreen.SETTINGS:
            # Check background swatch clicks
            if hasattr(self.renderer, 'bg_swatch_rects'):
                for bg_key, rect in self.renderer.bg_swatch_rects.items():
                    if rect.collidepoint(pos):
                        # Set new background
                        self.settings.set_background_color(bg_key)
                        self.renderer.set_background(bg_key)
                        return

            # Check scoring factor checkbox clicks
            if hasattr(self.renderer, 'scoring_factor_rects'):
                for factor_key, rect in self.renderer.scoring_factor_rects.items():
                    if rect.collidepoint(pos):
                        # Toggle scoring factor
                        current_value = self.settings.get(factor_key, True)
                        self.settings.set_scoring_factor(factor_key, not current_value)
                        return

            # Check purge button click
            if hasattr(self.renderer, 'purge_button_rect'):
                if self.renderer.purge_button_rect.collidepoint(pos):
                    # Purge all scores
                    if self.stats_tracker.purge_all_scores():
                        print("All scores have been purged!")
                    else:
                        print("Failed to purge scores!")
                    return

        # Check for menu button clicks
        if not hasattr(self.menu_state, 'button_rects'):
            return

        for option, rect in self.menu_state.button_rects.items():
            if rect.collidepoint(pos):
                # Find option index and select it
                options = self.menu_state.get_options()
                if option in options:
                    self.menu_state.selected_option = options.index(option)
                    self.execute_menu_action()
                break

    def execute_menu_action(self):
        """Execute the selected menu action."""
        selected = self.menu_state.get_selected_option()
        if not selected:
            return

        if self.menu_state.current_screen == MenuScreen.MAIN_MENU:
            if selected == "New Game":
                self.start_new_game()
            elif selected == "Continue":
                self.continue_game()
            elif selected == "High Scores":
                self.menu_state.navigate_to(MenuScreen.HIGH_SCORES)
            elif selected == "Settings":
                self.menu_state.navigate_to(MenuScreen.SETTINGS)
            elif selected == "Quit":
                self.running = False

        elif self.menu_state.current_screen == MenuScreen.PAUSE_MENU:
            if selected == "Resume":
                self.menu_state.navigate_to(MenuScreen.NONE)
            elif selected == "Save & Quit":
                self.save_and_quit()
            elif selected == "Restart":
                self.reset_game()
            elif selected == "Main Menu":
                self.return_to_main_menu()

        elif self.menu_state.current_screen in [MenuScreen.HIGH_SCORES, MenuScreen.SETTINGS]:
            if selected == "Back":
                self.menu_state.navigate_to(MenuScreen.MAIN_MENU)
                self.menu_state.update_main_menu_options(GameState.save_exists())

    def start_new_game(self):
        """Start a new game."""
        self.game_state.initialize_game()
        # Apply scoring factors from settings
        factors = self.settings.get_scoring_factors()
        self.game_state.time_enabled = factors['time_enabled']
        self.game_state.moves_enabled = factors['moves_enabled']
        self.game_state.values_enabled = factors['values_enabled']
        self.input_handler = InputHandler(self.game_state)
        self.game_won = False
        self.entering_name = False
        self.menu_state.navigate_to(MenuScreen.NONE)

    def continue_game(self):
        """Load and continue saved game."""
        if self.game_state.load_game():
            self.input_handler = InputHandler(self.game_state)
            self.game_won = False
            self.entering_name = False
            self.menu_state.navigate_to(MenuScreen.NONE)
            print("Game loaded successfully!")
        else:
            print("Failed to load game!")

    def save_and_quit(self):
        """Save current game and return to main menu."""
        if self.game_state.save_game():
            print("Game saved successfully!")
            self.menu_state.navigate_to(MenuScreen.MAIN_MENU)
            self.menu_state.update_main_menu_options(GameState.save_exists())
        else:
            print("Failed to save game!")

    def return_to_main_menu(self):
        """Return to main menu without saving."""
        self.menu_state.navigate_to(MenuScreen.MAIN_MENU)
        self.menu_state.update_main_menu_options(GameState.save_exists())

    def handle_name_entry(self, event):
        """
        Handle keyboard input for name entry.

        Args:
            event: Pygame KEYDOWN event
        """
        if event.key == pygame.K_RETURN and len(self.player_name) == 3:
            # Save score and return to main menu
            self.stats_tracker.save_score(self.player_name, self.final_score)
            print(f"\nScore saved! {self.player_name}: {self.final_score['total']:,} points")

            # Clear win state and return to main menu
            self.game_won = False
            self.entering_name = False
            self.player_name = ""
            self.final_score = None
            self.return_to_main_menu()

        elif event.key == pygame.K_BACKSPACE and len(self.player_name) > 0:
            # Delete last character
            self.player_name = self.player_name[:-1]

        elif len(self.player_name) < 3:
            # Add letter if A-Z
            if event.unicode.isalpha():
                self.player_name += event.unicode.upper()

    def reset_game(self):
        """Reset the game to initial state."""
        self.game_state.initialize_game()
        # Apply scoring factors from settings
        factors = self.settings.get_scoring_factors()
        self.game_state.time_enabled = factors['time_enabled']
        self.game_state.moves_enabled = factors['moves_enabled']
        self.game_state.values_enabled = factors['values_enabled']
        self.input_handler = InputHandler(self.game_state)
        self.game_won = False
        self.entering_name = False
        self.player_name = ""
        self.final_score = None
        self.menu_state.navigate_to(MenuScreen.NONE)


def main():
    """Entry point for the game."""
    game = SolitaireGame()
    game.run()


if __name__ == "__main__":
    main()
