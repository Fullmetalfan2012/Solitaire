"""Main game loop for Pygame Solitaire."""

import pygame
import time
from card import Card
from game_board import GameBoard
from renderer import Renderer
from input_handler import InputHandler
from stats import StatsTracker
from settings import Settings
from menu_state import MenuState, MenuScreen
from sage_advice import SageAdviceSystem
from auto_finish import AutoFinishSystem
from hint_system import HintSystem
from scoring_engine import ScoringEngine
from undo_redo_manager import UndoRedoManager
from ui_state import UIState
from save_load_coordinator import SaveLoadCoordinator
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
        self.scoring_engine = ScoringEngine()
        self.game_board = GameBoard(self.scoring_engine)
        self.undo_manager = UndoRedoManager(self.game_board, self.scoring_engine)
        self.game_board.set_undo_manager(self.undo_manager)  # Link undo manager to game state
        self.sage_advice = SageAdviceSystem()
        self.auto_finish = AutoFinishSystem(self.game_board)
        self.hint_system = HintSystem(self.game_board)
        self.ui_state = UIState()
        self.save_load = SaveLoadCoordinator(self.game_board, self.scoring_engine, self.hint_system, self.undo_manager)
        self.renderer = Renderer(self.screen, self.game_board, self.sage_advice, self.auto_finish, self.hint_system, self.scoring_engine, self.ui_state)
        self.input_handler = InputHandler(self.game_board)
        self.stats_tracker = StatsTracker()
        self.settings = Settings()
        self.menu_state = MenuState()

        # Apply settings
        self.renderer.set_background(self.settings.get_background_color())
        self.renderer.set_pile_outline_color(self.settings.get_pile_outline_color())

        # Update main menu based on save file existence
        self.menu_state.update_main_menu_options(SaveLoadCoordinator.save_exists())

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
                        self.hint_system.clear_highlights()

                        # Check if auto-finish is available
                        if not self.auto_finish.active:
                            self.auto_finish.available = self.auto_finish.check_available()

                        # Check if game is won after the move
                        if self.game_board.check_win():
                            self.game_won = True
                            self.entering_name = True
                            self.player_name = ""
                            self.final_score = self.scoring_engine.get_current_score(self.game_board.move_count)

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
        self.sage_advice.update()

        # Update snap-back animation
        self.input_handler.update_snap_back()

        # Handle auto-finish animation
        if self.auto_finish.active and not self.game_won:
            # Check if current move animation is complete (0.3s per move)
            if self.auto_finish.current_card:
                elapsed = time.time() - self.auto_finish.start_time
                if elapsed > 0.3:  # Animation duration
                    # Complete the move
                    self.auto_finish.complete_current_move()

                    # Check if game is won
                    if self.game_board.check_win():
                        self.auto_finish.stop()
                        self.game_won = True
                        self.entering_name = True
                        self.player_name = ""
                        self.final_score = self.scoring_engine.get_current_score(self.game_board.move_count)
                    else:
                        # Start next move
                        if not self.auto_finish.start_next_move():
                            # No more moves but not won? (shouldn't happen)
                            self.auto_finish.stop()
            else:
                # Start first move
                if not self.auto_finish.start_next_move():
                    self.auto_finish.stop()

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
            if self.hint_system.use_hint():
                print(f"Hint used! ({self.hint_system.hints_remaining} hints remaining)")
            else:
                print("No hints remaining!")
        elif event.key == pygame.K_a:
            # Show sage advice
            self.sage_advice.show_advice()
            print("Sage advice displayed")
        elif event.key == pygame.K_u:
            # Undo last move
            if self.undo_manager.undo():
                print(f"Undo successful! ({self.undo_manager.get_undo_count()} undos, {self.undo_manager.get_redo_count()} redos available)")
            else:
                print("No moves to undo")
        elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            # Redo next move (Ctrl+Y)
            if self.undo_manager.redo():
                print(f"Redo successful! ({self.undo_manager.get_undo_count()} undos, {self.undo_manager.get_redo_count()} redos available)")
            else:
                print("No moves to redo")
        elif event.key == pygame.K_r:
            # Reset game
            self.reset_game()
        elif event.key == pygame.K_f:
            # Start auto-finish if available
            if self.auto_finish.available and not self.auto_finish.active:
                self.auto_finish.start()
                print("Auto-finish started!")

    def handle_menu_keyboard(self, event):
        """Handle keyboard input in menus."""
        if event.key == pygame.K_ESCAPE:
            # Back/Resume
            if self.menu_state.current_screen == MenuScreen.PAUSE_MENU:
                self.menu_state.navigate_to(MenuScreen.NONE)
            elif self.menu_state.current_screen in [MenuScreen.HIGH_SCORES, MenuScreen.SETTINGS]:
                self.menu_state.navigate_to(MenuScreen.MAIN_MENU)
                self.menu_state.update_main_menu_options(GameBoard.save_exists())
        elif event.key == pygame.K_UP:
            self.menu_state.select_previous()
        elif event.key == pygame.K_DOWN:
            self.menu_state.select_next()
        elif event.key == pygame.K_RETURN:
            self.execute_menu_action()

    def handle_menu_click(self, pos):
        """Handle mouse click in menu."""
        # Check for settings screen clicks (background, pile outline, and scoring mode)
        if self.menu_state.current_screen == MenuScreen.SETTINGS:
            # Check background swatch clicks
            bg_key = self.ui_state.get_bg_swatch_at(pos)
            if bg_key:
                self.settings.set_background_color(bg_key)
                self.renderer.set_background(bg_key)
                return

            # Check pile outline color swatch clicks
            pile_key = self.ui_state.get_pile_outline_at(pos)
            if pile_key:
                self.settings.set_pile_outline_color(pile_key)
                self.renderer.set_pile_outline_color(pile_key)
                return

            # Check scoring factor checkbox clicks
            factor_key = self.ui_state.get_scoring_factor_at(pos)
            if factor_key:
                # Toggle scoring factor
                current_value = self.settings.get(factor_key, True)
                new_value = not current_value
                self.settings.set_scoring_factor(factor_key, new_value)
                # Update scoring_engine immediately so renderer shows correct state
                self.scoring_engine.set_factor(factor_key, new_value)
                return

            # Check purge button click
            if self.ui_state.is_purge_button_clicked(pos):
                # Purge all scores
                if self.stats_tracker.purge_all_scores():
                    print("All scores have been purged!")
                else:
                    print("Failed to purge scores!")
                return

        # Check for menu button clicks
        option = self.ui_state.get_menu_option_at(pos)
        if option:
            # Find option index and select it
            options = self.menu_state.get_options()
            if option in options:
                self.menu_state.selected_option = options.index(option)
                self.execute_menu_action()

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
                self.menu_state.update_main_menu_options(SaveLoadCoordinator.save_exists())

    def start_new_game(self):
        """Start a new game."""
        self.game_board.initialize_game()
        # Apply scoring factors from settings
        factors = self.settings.get_scoring_factors()
        self.scoring_engine.reset()
        self.scoring_engine.time_enabled = factors['time_enabled']
        self.scoring_engine.moves_enabled = factors['moves_enabled']
        self.scoring_engine.values_enabled = factors['values_enabled']
        # Reinitialize subsystems
        self.undo_manager = UndoRedoManager(self.game_board, self.scoring_engine)
        self.game_board.set_undo_manager(self.undo_manager)
        self.hint_system = HintSystem(self.game_board)
        self.auto_finish = AutoFinishSystem(self.game_board)
        self.input_handler = InputHandler(self.game_board)
        self.game_won = False
        self.entering_name = False
        self.menu_state.navigate_to(MenuScreen.NONE)

    def continue_game(self):
        """Load and continue saved game."""
        if self.save_load.load_game():
            # Reinitialize subsystems after load
            self.auto_finish = AutoFinishSystem(self.game_board)
            self.input_handler = InputHandler(self.game_board)
            self.game_won = False
            self.entering_name = False
            self.menu_state.navigate_to(MenuScreen.NONE)
            print("Game loaded successfully!")
        else:
            print("Failed to load game!")

    def save_and_quit(self):
        """Save current game and return to main menu."""
        if self.save_load.save_game():
            print("Game saved successfully!")
            self.menu_state.navigate_to(MenuScreen.MAIN_MENU)
            self.menu_state.update_main_menu_options(SaveLoadCoordinator.save_exists())
        else:
            print("Failed to save game!")

    def return_to_main_menu(self):
        """Return to main menu without saving."""
        self.menu_state.navigate_to(MenuScreen.MAIN_MENU)
        self.menu_state.update_main_menu_options(SaveLoadCoordinator.save_exists())

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
        self.game_board.initialize_game()
        # Apply scoring factors from settings
        factors = self.settings.get_scoring_factors()
        self.scoring_engine.reset()
        self.scoring_engine.time_enabled = factors['time_enabled']
        self.scoring_engine.moves_enabled = factors['moves_enabled']
        self.scoring_engine.values_enabled = factors['values_enabled']
        # Reinitialize subsystems
        self.undo_manager = UndoRedoManager(self.game_board, self.scoring_engine)
        self.game_board.set_undo_manager(self.undo_manager)
        self.hint_system = HintSystem(self.game_board)
        self.auto_finish = AutoFinishSystem(self.game_board)
        self.input_handler = InputHandler(self.game_board)
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
