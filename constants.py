"""Game constants for Pygame Solitaire."""

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900

# Card dimensions
CARD_WIDTH = 100
CARD_HEIGHT = 140

# Pile positions
STOCK_POS = (50, 50)
WASTE_POS = (190, 50)
FOUNDATION_START = (570, 50)
FOUNDATION_SPACING = 120
TABLEAU_START = (50, 250)
TABLEAU_SPACING = 120

# Card overlap in tableau
CARD_OVERLAP_Y = 30

# Colors
GREEN_FELT = (0, 100, 0)
DARKER_GREEN = (0, 80, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Background color options
BACKGROUND_COLORS = {
    'green': (0, 100, 0),
    'blue': (30, 60, 110),
    'grey': (60, 60, 60),
    'gradient_sunset': None,  # Special gradient
    'gradient_ocean': None,   # Special gradient
    'gradient_forest': None,  # Special gradient
}

# Gradient definitions (top_color, bottom_color)
GRADIENTS = {
    'gradient_sunset': ((60, 40, 80), (120, 60, 40)),      # Purple to orange
    'gradient_ocean': ((20, 50, 80), (40, 80, 100)),       # Dark blue to teal
    'gradient_forest': ((20, 40, 30), (40, 80, 50)),       # Dark green to lighter green
}

# Pile outline colors for empty piles (theme-aware)
PILE_OUTLINE_COLORS = {
    'green': (0, 80, 0),          # Darker green (original)
    'white': (200, 200, 200),     # Light grey/white
    'gold': (200, 170, 0),        # Muted gold
    'blue': (100, 150, 200),      # Light blue
    'red': (200, 100, 100),       # Soft red
}

# Game settings
FPS = 60

# Toggle-based scoring system
# Players can enable/disable each factor independently
DEFAULT_SCORING_FACTORS = {
    'time_enabled': True,
    'moves_enabled': True,
    'values_enabled': True
}

def get_scoring_mode_name(time_enabled: bool, moves_enabled: bool, values_enabled: bool) -> str:
    """
    Generate display name for scoring mode based on enabled factors.

    Returns:
        Display name like "Time + Moves" or "Values Only" or "Complete Only"
    """
    factors = []
    if time_enabled:
        factors.append("Time")
    if moves_enabled:
        factors.append("Moves")
    if values_enabled:
        factors.append("Values")

    if not factors:
        return "Complete Only"  # No scoring, just track wins

    return " + ".join(factors)
