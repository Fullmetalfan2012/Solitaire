"""Card class for Pygame Solitaire."""

import pygame
import copy
from typing import Optional
from constants import CARD_WIDTH, CARD_HEIGHT


class Card:
    """Represents a single playing card with support for future special abilities."""

    # Class-level image cache (loaded once, shared across all cards)
    _image_cache = {}

    def __init__(self, rank: str, suit: str):
        """
        Initialize a card.

        Args:
            rank: Card rank ('A', '2'-'10', 'J', 'Q', 'K')
            suit: Card suit ('hearts', 'diamonds', 'clubs', 'spades')
        """
        self.rank = rank
        self.suit = suit
        self.face_up = False
        self.position = (0, 0)

        # Extension points for future special abilities
        self.special_suit_ability: Optional[str] = None
        self.special_rank_ability: Optional[str] = None

        # Get images from cache
        self.image = self._image_cache.get(f"{suit}_{rank}")
        self.back_image = self._image_cache.get('back')

    def __deepcopy__(self, memo):
        """
        Custom deep copy that skips pygame Surface objects.

        Images are cached at class level and don't need to be copied.
        Only copy card state (rank, suit, position, face_up, abilities).
        """
        # Create new card instance
        new_card = Card(self.rank, self.suit)

        # Copy mutable state
        new_card.face_up = self.face_up
        new_card.position = copy.deepcopy(self.position, memo)
        new_card.special_suit_ability = self.special_suit_ability
        new_card.special_rank_ability = self.special_rank_ability

        # Images are already set in __init__ from cache - no need to copy

        return new_card

    def flip(self):
        """Toggle card face up/down."""
        self.face_up = not self.face_up

    def get_color(self) -> str:
        """
        Get card color based on suit.

        Returns:
            'red' for hearts/diamonds, 'black' for clubs/spades
        """
        return 'red' if self.suit in ['hearts', 'diamonds'] else 'black'

    def get_rank_value(self) -> int:
        """
        Get numeric value of rank for comparison.

        Returns:
            1-13 (Ace=1, 2-10=face value, J=11, Q=12, K=13)
        """
        rank_values = {
            'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
            '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
        }
        return rank_values[self.rank]

    def activate_suit_ability(self):
        """Activate special suit ability (stub for future implementation)."""
        if self.special_suit_ability:
            # TODO: Implement suit-based abilities
            pass

    def activate_rank_ability(self):
        """Activate special rank ability (stub for future implementation)."""
        if self.special_rank_ability:
            # TODO: Implement rank-based abilities
            pass

    def draw(self, surface: pygame.Surface):
        """
        Draw card to surface.

        Args:
            surface: Pygame surface to draw on
        """
        x, y = self.position

        if self.face_up and self.image:
            surface.blit(self.image, (x, y))
        elif self.back_image:
            surface.blit(self.back_image, (x, y))
        else:
            # Fallback: draw placeholder if images not loaded
            self._draw_placeholder(surface)

    def _draw_placeholder(self, surface: pygame.Surface):
        """Draw placeholder card when images aren't loaded."""
        x, y = self.position

        # Draw card background
        card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surface, (255, 255, 255), card_rect)
        pygame.draw.rect(surface, (0, 0, 0), card_rect, 2)

        if self.face_up:
            # Draw rank and suit
            font = pygame.font.Font(None, 36)
            color = (255, 0, 0) if self.get_color() == 'red' else (0, 0, 0)

            # Suit symbols
            suit_symbols = {
                'hearts': '♥', 'diamonds': '♦',
                'clubs': '♣', 'spades': '♠'
            }

            text = f"{self.rank} {suit_symbols.get(self.suit, self.suit[0].upper())}"
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
            surface.blit(text_surface, text_rect)
        else:
            # Draw card back pattern
            font = pygame.font.Font(None, 24)
            text = font.render("CARD", True, (100, 100, 100))
            text_rect = text.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
            surface.blit(text, text_rect)

    @classmethod
    def load_images(cls):
        """Load all card images into class-level cache."""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

        # Try to load PNG images
        for suit in suits:
            for rank in ranks:
                key = f"{suit}_{rank}"
                try:
                    path = f"assets/cards/{key}.png"
                    image = pygame.image.load(path)
                    cls._image_cache[key] = pygame.transform.scale(
                        image, (CARD_WIDTH, CARD_HEIGHT)
                    )
                except (pygame.error, FileNotFoundError):
                    # Image not found - will use placeholder
                    cls._image_cache[key] = None

        # Load card back
        try:
            back_image = pygame.image.load("assets/backs/back_light.png")
            cls._image_cache['back'] = pygame.transform.scale(
                back_image, (CARD_WIDTH, CARD_HEIGHT)
            )
        except (pygame.error, FileNotFoundError):
            # Back image not found - will use placeholder
            cls._image_cache['back'] = None

    def __repr__(self):
        """String representation for debugging."""
        return f"Card({self.rank} of {self.suit})"
