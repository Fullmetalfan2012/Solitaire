#!/usr/bin/env python3
"""Detailed test for undo/redo scoring bug fix."""

import pygame
pygame.init()

from game_state import GameState
from card import Card
from pile import TableauPile, FoundationPile

def test_undo_redo_scoring_detailed():
    """Test undo/redo scoring with manually created scenario."""
    print("\n=== Detailed Undo/Redo Scoring Test ===")

    gs = GameState()
    gs.initialize_game()

    # Enable value scoring
    gs.values_enabled = True
    gs.scoring_config['value_enabled'] = True
    gs.scoring_config['to_foundation'] = 10
    gs.scoring_config['flip_card'] = 5

    # Manually set up a test scenario
    # Create an ace and put it in a tableau
    ace_hearts = Card('A', 'hearts')
    ace_hearts.face_up = True

    # Find first tableau
    tableau = gs.tableaus[0]
    tableau.cards.clear()
    tableau.add_card(ace_hearts)

    # Find hearts foundation
    foundation = gs.foundations[0]  # Any empty foundation will do
    foundation.cards.clear()

    print(f"\nInitial state:")
    print(f"  Tableau cards: {[str(c) for c in tableau.cards]}")
    print(f"  Foundation cards: {[str(c) for c in foundation.cards]}")
    print(f"  Score: {gs.move_value_score}")

    assert gs.move_value_score == 0, "Initial score should be 0"

    # Test 1: Move ace to foundation (should add 10 points)
    print(f"\n--- Test 1: Move to Foundation (+10 pts) ---")
    success = gs.try_move([ace_hearts], tableau, foundation)
    assert success, "Move should succeed"

    score_after_move = gs.move_value_score
    print(f"  Score after move: {score_after_move}")
    assert score_after_move == 10, f"Score should be 10, got {score_after_move}"

    # Check the move was recorded with correct score_delta
    assert len(gs.move_history) > 0, "Move should be in history"
    last_move = gs.move_history[-1]
    print(f"  Move score_delta: {last_move.score_delta}")
    assert last_move.score_delta == 10, f"Move score_delta should be 10, got {last_move.score_delta}"

    # Test 2: Undo (should restore score to 0)
    print(f"\n--- Test 2: Undo (restore to 0) ---")
    undo_success = gs.undo()
    assert undo_success, "Undo should succeed"

    score_after_undo = gs.move_value_score
    print(f"  Score after undo: {score_after_undo}")
    assert score_after_undo == 0, f"❌ BUG: Score should be 0 after undo, got {score_after_undo}"

    print(f"  Tableau cards: {[str(c) for c in tableau.cards]}")
    print(f"  Foundation cards: {[str(c) for c in foundation.cards]}")
    assert ace_hearts in tableau.cards, "Card should be back in tableau"
    assert ace_hearts not in foundation.cards, "Card should not be in foundation"

    # Test 3: Redo (should restore score to 10)
    print(f"\n--- Test 3: Redo (restore to 10) ---")
    redo_success = gs.redo()
    assert redo_success, "Redo should succeed"

    score_after_redo = gs.move_value_score
    print(f"  Score after redo: {score_after_redo}")
    assert score_after_redo == 10, f"Score should be 10 after redo, got {score_after_redo}"

    print(f"  Tableau cards: {[str(c) for c in tableau.cards]}")
    print(f"  Foundation cards: {[str(c) for c in foundation.cards]}")
    assert ace_hearts not in tableau.cards, "Card should not be in tableau"
    assert ace_hearts in foundation.cards, "Card should be in foundation"

    # Test 4: Multiple moves with different scores
    print(f"\n--- Test 4: Multiple Moves with Different Scores ---")

    # Add another card to foundation (+10)
    two_hearts = Card('2', 'hearts')
    two_hearts.face_up = True
    tableau.cards.clear()
    tableau.add_card(two_hearts)

    gs.try_move([two_hearts], tableau, foundation)
    score_after_2nd = gs.move_value_score
    print(f"  Score after 2nd move: {score_after_2nd}")
    assert score_after_2nd == 20, f"Score should be 20, got {score_after_2nd}"

    # Undo twice
    gs.undo()
    score_after_1_undo = gs.move_value_score
    print(f"  Score after 1st undo: {score_after_1_undo}")
    assert score_after_1_undo == 10, f"Score should be 10, got {score_after_1_undo}"

    gs.undo()
    score_after_2_undo = gs.move_value_score
    print(f"  Score after 2nd undo: {score_after_2_undo}")
    assert score_after_2_undo == 0, f"Score should be 0, got {score_after_2_undo}"

    # Redo twice
    gs.redo()
    score_after_1_redo = gs.move_value_score
    print(f"  Score after 1st redo: {score_after_1_redo}")
    assert score_after_1_redo == 10, f"Score should be 10, got {score_after_1_redo}"

    gs.redo()
    score_after_2_redo = gs.move_value_score
    print(f"  Score after 2nd redo: {score_after_2_redo}")
    assert score_after_2_redo == 20, f"Score should be 20, got {score_after_2_redo}"

    print(f"\n✅ All undo/redo scoring tests passed!")
    print(f"✅ The critical bug is FIXED!")
    return True

if __name__ == '__main__':
    try:
        success = test_undo_redo_scoring_detailed()
        if success:
            print("\n" + "="*60)
            print("🎉 SUCCESS - Undo/Redo scoring bug is FIXED!")
            print("="*60)
    except AssertionError as e:
        print(f"\n❌ FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
