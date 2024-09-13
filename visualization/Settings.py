class Settings:
    """A class for handling configuration constants"""
    SCALING_FACTOR = 7
    PLAYER_SIZE_RATIO = 12 / SCALING_FACTOR
    REFRESH_RATE = 10
    OFFSET = 6
    MIN_X = 0
    MAX_X = 100
    MIN_Y = 0
    MAX_Y = 50
    COLUMN_WIDTH = 0.3
    COURT_SCALE = 1.65
    FONT_SIZE = 6
    CENTER_X = MAX_X / 2 - OFFSET / 1.5 + 0.10
    CENTER_Y = MAX_Y - OFFSET / 1.5 - 0.35
    NOTIFICATION = 'Re-execute the script and select an event from 0 to '
