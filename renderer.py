"""Rendering logic for Pygame Solitaire."""

import pygame
from typing import TYPE_CHECKING, Dict, List, Optional
from constants import (
    GREEN_FELT, DARKER_GREEN, WHITE, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT,
    BACKGROUND_COLORS, GRADIENTS, PILE_OUTLINE_COLORS
)

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
        self.background_name = 'green'  # Current background setting
        self.pile_outline_color = DARKER_GREEN  # Default pile outline color
        self.pile_outline_name = 'green'  # Current pile outline setting
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

    def set_background(self, background_name: str):
        """
        Set the background color/gradient by name.

        Args:
            background_name: Name from BACKGROUND_COLORS dict
        """
        self.background_name = background_name
        # Set solid color if not a gradient
        if background_name in BACKGROUND_COLORS and BACKGROUND_COLORS[background_name]:
            self.background_color = BACKGROUND_COLORS[background_name]
        elif background_name.startswith('gradient_'):
            # For gradients, we'll use a default solid color as fallback
            self.background_color = (50, 50, 50)

    def set_pile_outline_color(self, color_name: str):
        """
        Set the pile outline color by name.

        Args:
            color_name: Name from PILE_OUTLINE_COLORS dict
        """
        self.pile_outline_name = color_name
        if color_name in PILE_OUTLINE_COLORS:
            self.pile_outline_color = PILE_OUTLINE_COLORS[color_name]
        else:
            self.pile_outline_color = DARKER_GREEN  # Fallback to default

    def _draw_background(self):
        """Draw the background (solid or gradient)."""
        if self.background_name.startswith('gradient_') and self.background_name in GRADIENTS:
            # Draw gradient
            top_color, bottom_color = GRADIENTS[self.background_name]
            self._draw_gradient(top_color, bottom_color)
        else:
            # Draw solid color
            self.screen.fill(self.background_color)

    def _draw_gradient(self, top_color: tuple, bottom_color: tuple):
        """
        Draw a vertical gradient background.

        Args:
            top_color: RGB tuple for top of screen
            bottom_color: RGB tuple for bottom of screen
        """
        for y in range(SCREEN_HEIGHT):
            # Interpolate between top and bottom colors
            ratio = y / SCREEN_HEIGHT
            color = tuple(
                int(top_color[i] + (bottom_color[i] - top_color[i]) * ratio)
                for i in range(3)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def render(self, input_handler: 'InputHandler'):
        """
        Render the entire game state.

        Args:
            input_handler: Input handler (to know which cards are being dragged)
        """
        # Draw background
        self._draw_background()

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

        # Draw auto-finish button if available
        self._draw_auto_finish()

        # Draw animating card during auto-finish
        if self.game_state.auto_finishing and self.game_state.auto_finish_card:
            self._draw_auto_finish_animation()

        # Update display
        pygame.display.flip()

    def _draw_pile_outlines(self):
        """Draw rectangles and labels showing where empty piles are."""
        from pile import StockPile, WastePile, FoundationPile

        outline_color = self.pile_outline_color
        # Calculate label color as a lighter version of outline color
        label_color = tuple(min(255, c + 50) for c in outline_color)

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

        # Undo/Redo counter (top-left, to the right of waste pile to avoid overlap)
        undo_count = self.game_state.get_undo_count()
        redo_count = self.game_state.get_redo_count()
        undo_text = f"Undo (U): {undo_count}  |  Redo (Ctrl+Y): {redo_count}"
        undo_surface = self.small_font.render(undo_text, True, WHITE)
        self.screen.blit(undo_surface, (350, 10))

        # Hint counter (below undo)
        hint_count = self.game_state.hints_remaining
        hint_text = f"Hints (H): {hint_count}/3  |  Advice (A): ∞"
        hint_surface = self.small_font.render(hint_text, True, WHITE)
        self.screen.blit(hint_surface, (350, 40))

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

    def _draw_auto_finish(self):
        """Draw auto-finish button if available."""
        if not self.game_state.auto_finish_available:
            return

        # Button position (center bottom, above sage advice area)
        button_width = 200
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = SCREEN_HEIGHT - 150

        # Draw button
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (80, 120, 80), button_rect)  # Green button
        pygame.draw.rect(self.screen, (120, 200, 120), button_rect, 3)  # Bright border

        # Draw text
        text = self.small_font.render("Auto-Finish (F)", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)

    def _draw_auto_finish_animation(self):
        """Draw card flying to foundation during auto-finish."""
        import time
        import math

        card = self.game_state.auto_finish_card
        source = self.game_state.auto_finish_source
        target = self.game_state.auto_finish_target

        if not (card and source and target):
            return

        # Calculate animation progress (0.0 to 1.0)
        elapsed = time.time() - self.game_state.auto_finish_start_time
        progress = min(1.0, elapsed / 0.3)  # 0.3s animation

        # Interpolate position from source to target
        start_x, start_y = source.rect.x, source.rect.y
        end_x, end_y = target.rect.x, target.rect.y

        # Add slight arc to the animation
        arc_height = 100
        arc_progress = math.sin(progress * math.pi) * arc_height

        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress - arc_progress

        # Draw the card at animated position
        # Update card position (cards don't have rect, only position tuple)
        card.position = (int(current_x), int(current_y))
        card.draw(self.screen)

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

    def render_menu(self, menu_state: 'MenuState', stats_tracker: 'StatsTracker' = None, input_handler=None):
        """
        Render menu screens.

        Args:
            menu_state: Current menu state
            stats_tracker: Stats tracker for high scores display
            input_handler: Input handler (for pause menu to show game underneath)
        """
        from menu_state import MenuScreen

        # For pause menu, render game first then overlay
        if menu_state.current_screen == MenuScreen.PAUSE_MENU and input_handler:
            # Render the game board underneath
            self._draw_background()
            for pile in self.game_state.all_piles:
                for card in pile.cards:
                    if card not in input_handler.dragged_cards:
                        card.draw(self.screen)
            for card in input_handler.dragged_cards:
                card.draw(self.screen)
            self._draw_score_info()
            # Now render pause menu overlay on top
            self._render_pause_menu(menu_state)
        else:
            # Clear screen for other menus
            self.screen.fill((20, 20, 40))  # Dark blue background

            if menu_state.current_screen == MenuScreen.MAIN_MENU:
                self._render_main_menu(menu_state)
            elif menu_state.current_screen == MenuScreen.HIGH_SCORES:
                self._render_high_scores(stats_tracker)
            elif menu_state.current_screen == MenuScreen.SETTINGS:
                # Get scoring factors from game state
                scoring_factors = {
                    'time_enabled': getattr(self.game_state, 'time_enabled', True),
                    'moves_enabled': getattr(self.game_state, 'moves_enabled', True),
                    'values_enabled': getattr(self.game_state, 'values_enabled', True)
                }
                self._render_settings(self.background_name, scoring_factors)

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
        """Render high scores screen (filtered by current scoring mode)."""
        from constants import get_scoring_mode_name

        # Title
        title = self.font.render("High Scores", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        # Get current scoring mode name from game state
        time_enabled = getattr(self.game_state, 'time_enabled', True)
        moves_enabled = getattr(self.game_state, 'moves_enabled', True)
        values_enabled = getattr(self.game_state, 'values_enabled', True)
        mode_name = get_scoring_mode_name(time_enabled, moves_enabled, values_enabled)

        mode_text = self.small_font.render(f"Mode: {mode_name}", True, (180, 180, 180))
        mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, 110))
        self.screen.blit(mode_text, mode_rect)

        y_offset = 150

        if stats_tracker and stats_tracker.scores:
            # Get top 10 scores for current mode
            top_scores = stats_tracker.get_top_scores(10, mode_name)

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

    def _render_settings(self, current_bg: Optional[str] = None, scoring_factors: Optional[Dict[str, bool]] = None):
        """
        Render settings screen with clickable background swatches and scoring factor checkboxes.

        Args:
            current_bg: Current background color setting
            scoring_factors: Dictionary of enabled scoring factors
        """
        from constants import get_scoring_mode_name

        # Default scoring factors if not provided
        if scoring_factors is None:
            scoring_factors = {
                'time_enabled': True,
                'moves_enabled': True,
                'values_enabled': True
            }

        # Title
        title = self.font.render("Settings", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Background color section
        y_offset = 150
        subtitle = self.font.render("Background Color", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(subtitle, subtitle_rect)

        # Background options with clickable swatches
        bg_options = [
            ('green', 'Classic Green', (0, 100, 0)),
            ('blue', 'Ocean Blue', (30, 60, 110)),
            ('grey', 'Slate Grey', (60, 60, 60)),
            ('gradient_sunset', 'Sunset', (90, 50, 60)),  # Average gradient color
            ('gradient_ocean', 'Ocean', (30, 65, 90)),     # Average gradient color
            ('gradient_forest', 'Forest', (30, 60, 40)),   # Average gradient color
        ]

        y_offset = 220
        swatch_size = 80
        spacing = 150
        start_x = (SCREEN_WIDTH - (len(bg_options) * spacing - (spacing - swatch_size))) // 2

        # Store rects for click detection (stored in renderer for access by main.py)
        self.bg_swatch_rects = {}

        for i, (bg_key, bg_name, color) in enumerate(bg_options):
            x = start_x + i * spacing

            # Draw swatch
            swatch_rect = pygame.Rect(x, y_offset, swatch_size, swatch_size)

            # Draw gradient preview for gradients
            if bg_key.startswith('gradient_'):
                top_color, bottom_color = GRADIENTS[bg_key]
                for y in range(swatch_size):
                    ratio = y / swatch_size
                    line_color = tuple(
                        int(top_color[j] + (bottom_color[j] - top_color[j]) * ratio)
                        for j in range(3)
                    )
                    pygame.draw.line(self.screen, line_color,
                                   (x, y_offset + y), (x + swatch_size, y_offset + y))
            else:
                pygame.draw.rect(self.screen, color, swatch_rect)

            # Draw border (gold if selected, white otherwise)
            border_color = (255, 215, 0) if bg_key == current_bg else WHITE
            border_width = 4 if bg_key == current_bg else 2
            pygame.draw.rect(self.screen, border_color, swatch_rect, border_width)

            # Draw label
            label = self.small_font.render(bg_name, True, WHITE)
            label_rect = label.get_rect(center=(x + swatch_size // 2, y_offset + swatch_size + 20))
            self.screen.blit(label, label_rect)

            # Store rect for click detection
            self.bg_swatch_rects[bg_key] = swatch_rect

        # Pile outline color section
        y_offset = 350
        subtitle_pile = self.font.render("Empty Pile Color", True, WHITE)
        subtitle_pile_rect = subtitle_pile.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(subtitle_pile, subtitle_pile_rect)

        # Pile outline color options
        pile_options = [
            ('green', 'Green', (0, 80, 0)),
            ('white', 'White', (200, 200, 200)),
            ('gold', 'Gold', (200, 170, 0)),
            ('blue', 'Blue', (100, 150, 200)),
            ('red', 'Red', (200, 100, 100)),
        ]

        y_offset = 410
        pile_swatch_size = 60
        pile_spacing = 120
        pile_start_x = (SCREEN_WIDTH - (len(pile_options) * pile_spacing - (pile_spacing - pile_swatch_size))) // 2

        # Store rects for click detection
        self.pile_outline_rects = {}

        for i, (pile_key, pile_name, color) in enumerate(pile_options):
            x = pile_start_x + i * pile_spacing

            # Draw swatch
            pile_swatch_rect = pygame.Rect(x, y_offset, pile_swatch_size, pile_swatch_size)
            pygame.draw.rect(self.screen, color, pile_swatch_rect)

            # Draw border (gold if selected, white otherwise)
            border_color = (255, 215, 0) if pile_key == self.pile_outline_name else WHITE
            border_width = 4 if pile_key == self.pile_outline_name else 2
            pygame.draw.rect(self.screen, border_color, pile_swatch_rect, border_width)

            # Draw label
            label = self.small_font.render(pile_name, True, WHITE)
            label_rect = label.get_rect(center=(x + pile_swatch_size // 2, y_offset + pile_swatch_size + 20))
            self.screen.blit(label, label_rect)

            # Store rect for click detection
            self.pile_outline_rects[pile_key] = pile_swatch_rect

        # Scoring factors section
        y_offset = 540
        subtitle2 = self.font.render("Scoring Factors", True, WHITE)
        subtitle2_rect = subtitle2.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(subtitle2, subtitle2_rect)

        # Show current mode name
        y_offset += 50
        current_mode_name = get_scoring_mode_name(
            scoring_factors['time_enabled'],
            scoring_factors['moves_enabled'],
            scoring_factors['values_enabled']
        )
        mode_display = self.small_font.render(f"Current Mode: {current_mode_name}", True, (200, 200, 200))
        mode_rect = mode_display.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        self.screen.blit(mode_display, mode_rect)

        # Scoring factor checkboxes
        y_offset += 50
        checkbox_size = 30
        label_spacing = 200
        start_x = (SCREEN_WIDTH - (3 * label_spacing)) // 2

        self.scoring_factor_rects = {}

        factors = [
            ('time_enabled', 'Time Bonus'),
            ('moves_enabled', 'Move Penalty'),
            ('values_enabled', 'Move Values')
        ]

        for i, (factor_key, factor_label) in enumerate(factors):
            x = start_x + i * label_spacing

            # Draw checkbox
            checkbox_rect = pygame.Rect(x, y_offset, checkbox_size, checkbox_size)
            checkbox_bg = (40, 40, 40)
            pygame.draw.rect(self.screen, checkbox_bg, checkbox_rect)
            pygame.draw.rect(self.screen, WHITE, checkbox_rect, 2)

            # Draw checkmark if enabled
            if scoring_factors.get(factor_key, True):
                # Draw checkmark
                checkmark_color = (100, 255, 100)
                pygame.draw.line(self.screen, checkmark_color,
                               (x + 5, y_offset + checkbox_size // 2),
                               (x + checkbox_size // 3, y_offset + checkbox_size - 5), 3)
                pygame.draw.line(self.screen, checkmark_color,
                               (x + checkbox_size // 3, y_offset + checkbox_size - 5),
                               (x + checkbox_size - 5, y_offset + 5), 3)

            # Draw label
            label = self.small_font.render(factor_label, True, WHITE)
            label_rect = label.get_rect(midleft=(x + checkbox_size + 10, y_offset + checkbox_size // 2))
            self.screen.blit(label, label_rect)

            # Store rect for click detection (include label for easier clicking)
            extended_rect = pygame.Rect(x, y_offset, label_spacing - 20, checkbox_size)
            self.scoring_factor_rects[factor_key] = extended_rect

        # Purge scores button
        y_offset += 100
        purge_button_width = 250
        purge_button_height = 40
        purge_x = (SCREEN_WIDTH - purge_button_width) // 2

        self.purge_button_rect = pygame.Rect(purge_x, y_offset, purge_button_width, purge_button_height)
        purge_bg_color = (100, 30, 30)  # Dark red
        pygame.draw.rect(self.screen, purge_bg_color, self.purge_button_rect)
        pygame.draw.rect(self.screen, (200, 100, 100), self.purge_button_rect, 2)

        purge_text = self.small_font.render("Clear All Scores", True, WHITE)
        purge_text_rect = purge_text.get_rect(center=self.purge_button_rect.center)
        self.screen.blit(purge_text, purge_text_rect)

        # Warning text
        warning_text = self.small_font.render("(This cannot be undone!)", True, (180, 100, 100))
        warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + purge_button_height + 20))
        self.screen.blit(warning_text, warning_rect)

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
