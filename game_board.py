"""Game board management for Pygame Solitaire."""

import random
from typing import List, Optional, TYPE_CHECKING
from card import Card
from pile import Pile, StockPile, WastePile, FoundationPile, TableauPile
from move import Move
from constants import (
    STOCK_POS, WASTE_POS, FOUNDATION_START, FOUNDATION_SPACING,
    TABLEAU_START, TABLEAU_SPACING
)

if TYPE_CHECKING:
    from scoring_engine import ScoringEngine
    from undo_redo_manager import UndoRedoManager


class GameBoard:
    """Manages game board, piles, and core game logic."""

    def __init__(self, scoring_engine: 'ScoringEngine', undo_manager: 'UndoRedoManager' = None):
        """
        Initialize game board.

        Args:
            scoring_engine: Scoring engine for tracking game score
            undo_manager: Undo/redo manager for move history (can be set later via set_undo_manager)
        """
        self.stock: Optional[StockPile] = None
        self.waste: Optional[WastePile] = None
        self.foundations: List[FoundationPile] = []
        self.tableaus: List[TableauPile] = []
        self.all_piles: List[Pile] = []

        # Required subsystems (undo_manager must be set before first move)
        self.scoring_engine = scoring_engine
        self.undo_manager = undo_manager

        # Move counter
        self.move_count: int = 0

    def set_undo_manager(self, undo_manager: 'UndoRedoManager'):
        """
        Set the undo/redo manager (required before making moves).

        Args:
            undo_manager: Undo/redo manager to use
        """
        self.undo_manager = undo_manager

    def initialize_game(self):
        """Set up a new game with shuffled deck."""
        # Reset scoring
        self.scoring_engine.reset()
        self.move_count = 0

        # Create stock and waste piles
        self.stock = StockPile(*STOCK_POS)
        self.waste = WastePile(*WASTE_POS)

        # Create foundation piles (one for each suit)
        self.foundations = []
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        for i, suit in enumerate(suits):
            x = FOUNDATION_START[0] + i * FOUNDATION_SPACING
            self.foundations.append(FoundationPile(x, FOUNDATION_START[1], suit))

        # Create tableau piles
        self.tableaus = []
        for i in range(7):
            x = TABLEAU_START[0] + i * TABLEAU_SPACING
            self.tableaus.append(TableauPile(x, TABLEAU_START[1]))

        # Store all piles for easy iteration
        self.all_piles = [self.stock, self.waste] + self.foundations + self.tableaus

        # Create, shuffle, and deal deck
        deck = self._create_deck()
        random.shuffle(deck)
        self._deal_cards(deck)

    def _create_deck(self) -> List[Card]:
        """
        Create a standard 52-card deck.

        Returns:
            List of 52 Card objects
        """
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return [Card(rank, suit) for suit in suits for rank in ranks]

    def _deal_cards(self, deck: List[Card]):
        """
        Deal cards Klondike-style.

        Deals cards to tableau piles:
        - Pile 1: 1 card
        - Pile 2: 2 cards
        - ...
        - Pile 7: 7 cards
        Top card in each pile is face up, rest are face down.
        Remaining cards go to stock.

        Args:
            deck: Shuffled deck of cards
        """
        # Deal to tableau
        for i in range(7):
            for j in range(i + 1):
                card = deck.pop()
                self.tableaus[i].add_card(card)

            # Flip top card face up
            self.tableaus[i].cards[-1].face_up = True

        # Remaining cards go to stock (face down)
        for card in deck:
            self.stock.add_card(card)

    def handle_stock_click(self):
        """
        Handle clicking on the stock pile.

        If stock has cards, draw one to waste.
        If stock is empty, recycle waste back to stock.
        """
        if self.stock.cards:
            # Draw card from stock to waste
            card = self.stock.draw_card()
            if card:
                self.waste.add_card(card)
                # Create move for undo/redo (single card from stock to waste)
                move = Move(self.stock, self.waste, [card], None)
                self.undo_manager.record_move(move)
            # Note: Drawing from stock doesn't count as a scored move
        else:
            # Recycle waste back to stock
            cards_to_recycle = list(self.waste.cards)  # Copy list before clearing
            card_states = [card.face_up for card in cards_to_recycle]  # Store states before flipping

            while self.waste.cards:
                card = self.waste.cards.pop()
                card.face_up = False
                self.stock.add_card(card)

            # Create move for undo/redo (all cards from waste to stock, with original states)
            move = Move(self.waste, self.stock, cards_to_recycle, None, card_states)
            self.undo_manager.record_move(move)

            # Record the recycle action (penalty)
            self.scoring_engine.record_stock_recycle()

    def try_move(self, cards: List[Card], source: Pile, target: Pile) -> bool:
        """
        Attempt to move cards from source pile to target pile.

        Args:
            cards: List of cards to move
            source: Source pile
            target: Target pile

        Returns:
            True if move was successful, False otherwise
        """
        # Can only move single card to foundation
        if isinstance(target, FoundationPile) and len(cards) > 1:
            return False

        # Check if move is legal using target pile's rules
        if not target.can_accept(cards[0], source):
            return False

        # Execute the move
        for card in cards:
            source.remove_card(card)
            target.add_card(card)

        # Check if we flipped a card
        revealed_card = None
        if isinstance(source, TableauPile):
            if source.flip_top_card():
                # A card was flipped - track it for undo
                revealed_card = source.cards[-1] if source.cards else None

        # Calculate score change for this move
        score_delta = self.scoring_engine.record_move(source, target, cards, revealed_card is not None)

        # Create and store move for undo/redo
        move = Move(source, target, cards, revealed_card, score_delta=score_delta)
        self.undo_manager.record_move(move)

        return True

    def check_win(self) -> bool:
        """
        Check if the game is won.

        Game is won when all foundations have 13 cards (full suit).

        Returns:
            True if game is won
        """
        return all(len(foundation.cards) == 13 for foundation in self.foundations)

    def get_pile_at(self, pos: tuple) -> Optional[Pile]:
        """
        Get the pile at the given screen position.

        Args:
            pos: Screen position (x, y)

        Returns:
            Pile at that position, or None
        """
        # Check in reverse order so top piles are prioritized
        for pile in reversed(self.all_piles):
            if pile.rect.collidepoint(pos):
                return pile
        return None

