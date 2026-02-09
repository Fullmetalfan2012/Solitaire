"""Rendering logic for Pygame Solitaire."""

import pygame
from typing import TYPE_CHECKING, Dict, List
from constants import GREEN_FELT, DARKER_GREEN, WHITE, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from game_state import GameState
    from input_handler import InputHandler
    from menu_state import MenuState, MenuScreen
    from stats import StatsTracker


class Renderer:
    """Handles all drawing/rendering logic."""

    def __init__(self, screen: pygame.Surface, game_state: 'GameState'):
        """
        Initialize renderer.

        Args:
            screen: Pygame display surface
            game_state: Game state to render
        """
        self.screen = screen
        self.game_state = game_state
        self.background_color = GREEN_FELT
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

    def render(self, input_handler: 'InputHandler'):
        """
        Render the entire game state.

        Args:
            input_handler: Input handler (to know which cards are being dragged)
        """
        # Clear screen
        self.screen.fill(self.background_color)

        # Draw pile outlines for empty piles
        self._draw_pile_outlines()

        # Draw all cards in piles (except dragged cards)
        for pile in self.game_state.all_piles:
            for card in pile.cards:
                if card not in input_handler.dragged_cards:
                    card.draw(self.screen)

        # Draw dragged cards last (so they appear on top)
        for card in input_handler.dragged_cards:
            card.draw(self.screen)

        # Draw hint highlights
        self._draw_hint_highlights()

        # Draw score info
        self._draw_score_info()

        # Draw sage advice
        self._draw_sage_advice()

        # Update display
        pygame.display.flip()

    def _draw_pile_outlines(self):
        """Draw rectangles and labels showing where empty piles are."""
        from pile import StockPile, WastePile, FoundationPile

        outline_color = DARKER_GREEN
        label_color = (100, 150, 100)  # Lighter green for labels

        # Suit names for foundations (more compatible than Unicode symbols)
        suit_names = {
            'hearts': 'Hearts',
            'diamonds': 'Diamonds',
            'clubs': 'Clubs',
            'spades': 'Spades'
        }

        for pile in self.game_state.all_piles:
            if not pile.cards:
                # Draw outline for empty pile
                pygame.draw.rect(self.screen, outline_color, pile.rect, 2)

                # Add label based on pile type
                label_text = None

                if isinstance(pile, StockPile):
                    label_text = "STOCK"
                elif isinstance(pile, WastePile):
                    label_text = "WASTE"
                elif isinstance(pile, FoundationPile):
                    # Show suit name for foundation
                    label_text = suit_names.get(pile.suit, pile.suit.upper())

                # Render label if we have one
                if label_text:
                    text_surface = self.small_font.render(label_text, True, label_color)
                    text_rect = text_surface.get_rect(center=pile.rect.center)
                    self.screen.blit(text_surface, text_rect)

    def _draw_score_info(self):
        """Draw score, moves, time, and undo counter at top."""
        score_data = self.game_state.get_current_score()
        elapsed = score_data['elapsed_time']

        # Format time as MM:SS
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        # Format score with commas for readability
        score_str = f"{score_data['total']:,}"

        # Create display text (top-right)
        text = f"Score: {score_str}  |  Moves: {score_data['move_count']}  |  Time: {time_str}"
        surface = self.small_font.render(text, True, WHITE)
        text_rect = surface.get_rect(topright=(SCREEN_WIDTH - 20, 10))
        self.screen.blit(surface, text_rect)

        # Undo counter (top-left)
        undo_count = self.game_state.get_undo_count()
        undo_text = f"Undo (U): {undo_count}/3"
        undo_surface = self.small_font.render(undo_text, True, WHITE)
        self.screen.blit(undo_surface, (20, 10))

        # Hint counter (below undo)
        hint_count = self.game_state.hints_remaining
        hint_text = f"Hints (H): {hint_count}/3  |  Advice (A): ∞"
        hint_surface = self.small_font.render(hint_text, True, WHITE)
        self.screen.blit(hint_surface, (20, 40))

    def _draw_hint_highlights(self):
        """Draw glowing highlights on valid move destinations."""
        if not self.game_state.hint_targets:
            return

        # Pulsing glow effect
        import math
        pulse = abs(math.sin(pygame.time.get_ticks() / 300.0))
        alpha = int(128 + 127 * pulse)

        for pile in self.game_state.hint_targets:
            # Create semi-transparent overlay
            highlight = pygame.Surface((pile.rect.width, pile.rect.height))
            highlight.set_alpha(alpha)
            highlight.fill((255, 255, 0))  # Yellow glow

            self.screen.blit(highlight, pile.rect.topleft)

            # Draw bright border
            pygame.draw.rect(self.screen, (255, 255, 0), pile.rect, 4)

    def _draw_sage_advice(self):
        """Draw sage advice text at bottom of screen."""
        if not self.game_state.sage_advice_text:
            return

        # Semi-transparent background panel
        panel_height = 80
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - panel_height, SCREEN_WIDTH, panel_height)
        overlay = pygame.Surface((SCREEN_WIDTH, panel_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, SCREEN_HEIGHT - panel_height))

        # Advice label
        label = self.small_font.render("💡 Sage Advice:", True, (255, 215, 0))  # Gold
        self.screen.blit(label, (20, SCREEN_HEIGHT - panel_height + 10))

        # Advice text (word-wrapped if needed)
        advice = self.game_state.sage_advice_text
        advice_surface = self.small_font.render(advice, True, WHITE)
        self.screen.blit(advice_surface, (20, SCREEN_HEIGHT - panel_height + 40))

    def render_win_message(self):
        """Display win message overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Win text
        text = self.font.render("You Win!", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text, text_rect)

        # Instruction text
        instruction = self.small_font.render("Press R to play again", True, WHITE)
        instruction_rect = instruction.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
        )
        self.screen.blit(instruction, instruction_rect)

        pygame.display.flip()

    def render_name_entry(self, score_data: Dict, current_name: str):
        """
        Display name entry screen with score breakdown.

        Args:
            score_data: Final score breakdown from game_state
            current_name: Current name being typed (0-3 characters)
        """
        # Clear screen with solid dark background (no flicker)
        self.screen.fill((0, 0, 0))

        y_offset = 150

        # Title
        title = self.font.render("Victory!", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(title, title_rect)
        y_offset += 80

        # Score breakdown
        elapsed = score_data['elapsed_time']
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        breakdown = [
            f"Final Score: {score_data['total']:,}",
            "",
            f"Move Value: +{score_data['move_value']}",
            f"Time Bonus: +{score_data['time_bonus']}",
            f"Move Penalty: -{score_data['move_penalty']}",
            "",
            f"Moves: {score_data['move_count']}",
            f"Time: {minutes:02d}:{seconds:02d}"
        ]

        for line in breakdown:
            if line:
                text = self.small_font.render(line, True, WHITE)
            else:
                text = self.small_font.render(" ", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30

        y_offset += 20

        # Name entry prompt
        prompt = self.small_font.render("Enter your name (3 letters):", True, WHITE)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(prompt, prompt_rect)
        y_offset += 50

        # Name display with underscores
        name_display = current_name + "_" * (3 - len(current_name))
        # Add spaces between letters for arcade feel
        spaced_name = "  ".join(name_display)
        name_text = self.font.render(spaced_name, True, WHITE)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(name_text, name_rect)
        y_offset += 60

        # Instructions
        if len(current_name) == 3:
            instruction = self.small_font.render("Press ENTER to save", True, WHITE)
        else:
            instruction = self.small_font.render("Type letters A-Z | BACKSPACE to delete", True, WHITE)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(instruction, instruction_rect)

        pygame.display.flip()

    def render_debug_info(self, input_handler: 'InputHandler'):
        """
        Draw debug information (optional, for development).

        Args:
            input_handler: Input handler to show drag state
        """
        y = 10

        # Show drag state
        if input_handler.dragging:
            text = f"Dragging: {len(input_handler.dragged_cards)} card(s)"
            surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(surface, (10, y))
            y += 25

        # Show pile card counts
        pile_names = ['Stock', 'Waste'] + \
                     [f'F{i+1}' for i in range(4)] + \
                     [f'T{i+1}' for i in range(7)]

        for i, (pile, name) in enumerate(zip(self.game_state.all_piles, pile_names)):
            text = f"{name}: {len(pile.cards)}"
            surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(surface, (10, y))
            y += 20

            if y > SCREEN_HEIGHT - 30:
                break

    def render_menu(self, menu_state: 'MenuState', stats_tracker: 'StatsTracker' = None):
        """
        Render menu screens.

        Args:
            menu_state: Current menu state
            stats_tracker: Stats tracker for high scores display
        """
        from menu_state import MenuScreen

        # Clear screen
        self.screen.fill((20, 20, 40))  # Dark blue background

        if menu_state.current_screen == MenuScreen.MAIN_MENU:
            self._render_main_menu(menu_state)
        elif menu_state.current_screen == MenuScreen.HIGH_SCORES:
            self._render_high_scores(stats_tracker)
        elif menu_state.current_screen == MenuScreen.SETTINGS:
            self._render_settings()
        elif menu_state.current_screen == MenuScreen.PAUSE_MENU:
            self._render_pause_menu(menu_state)

        pygame.display.flip()

    def _render_main_menu(self, menu_state: 'MenuState'):
        """Render main menu."""
        # Title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("SOLITAIRE", True, (255, 215, 0))  # Gold
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.small_font.render("Klondike Edition", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)

        # Menu options
        self._render_menu_options(menu_state, start_y=320)

        # Controls hint
        hint = self.small_font.render("Use ↑↓ arrows or mouse to select, ENTER or click to confirm", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint, hint_rect)

    def _render_pause_menu(self, menu_state: 'MenuState'):
        """Render pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.font.render("PAUSED", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        # Menu options
        self._render_menu_options(menu_state, start_y=300)

    def _render_high_scores(self, stats_tracker: 'StatsTracker'):
        """Render high scores screen."""
        # Title
        title = self.font.render("High Scores", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        y_offset = 150

        if stats_tracker and stats_tracker.scores:
            # Get top 10 scores
            top_scores = stats_tracker.get_top_scores(10)

            # Headers
            header_text = "RANK    NAME    SCORE       MOVES    TIME"
            header = self.small_font.render(header_text, True, (200, 200, 200))
            header_rect = header.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(header, header_rect)
            y_offset += 40

            # Scores
            for i, score in enumerate(top_scores, 1):
                minutes = int(score['elapsed_time'] // 60)
                seconds = int(score['elapsed_time'] % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"

                score_text = f"{i:2d}.     {score['name']:3s}    {score['total_score']:6,d}      {score['move_count']:4d}    {time_str}"

                color = (255, 215, 0) if i == 1 else WHITE  # Gold for #1
                score_surface = self.small_font.render(score_text, True, color)
                score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(score_surface, score_rect)
                y_offset += 35

        else:
            # No scores yet
            no_scores = self.small_font.render("No games played yet!", True, WHITE)
            no_scores_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, y_offset + 50))
            self.screen.blit(no_scores, no_scores_rect)

        # Back button
        back_text = self.small_font.render("Press ESC or click here to go back", True, (150, 150, 150))
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def _render_settings(self):
        """Render settings screen."""
        # Title
        title = self.font.render("Settings", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        y_offset = 200

        # Scoring toggles (for future implementation)
        settings_text = [
            "Scoring Categories:",
            "",
            "✓ Time-based scoring: Enabled",
            "✓ Move count penalty: Enabled",
            "✓ Move value scoring: Enabled",
            "",
            "(Settings customization coming soon!)"
        ]

        for line in settings_text:
            text = self.small_font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35

        # Back button
        back_text = self.small_font.render("Press ESC or click here to go back", True, (150, 150, 150))
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def _render_menu_options(self, menu_state: 'MenuState', start_y: int):
        """Render menu option buttons."""
        options = menu_state.get_options()
        button_height = 50
        button_width = 300
        spacing = 20

        for i, option in enumerate(options):
            y = start_y + i * (button_height + spacing)
            x = (SCREEN_WIDTH - button_width) // 2

            # Button background
            is_selected = (i == menu_state.selected_option)
            button_color = (100, 100, 200) if is_selected else (60, 60, 100)
            border_color = (150, 150, 255) if is_selected else (100, 100, 150)

            button_rect = pygame.Rect(x, y, button_width, button_height)
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, border_color, button_rect, 3)

            # Button text
            text = self.font.render(option, True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

            # Store rect for click detection (attach to menu_state for later)
            if not hasattr(menu_state, 'button_rects'):
                menu_state.button_rects = {}
            menu_state.button_rects[option] = button_rect
