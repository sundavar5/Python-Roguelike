"""
Game configuration and constants
"""

import os
from pathlib import Path

class Config:
    """Game configuration constants"""

    # Screen settings
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 800
    FPS = 60

    # Game settings
    GAME_TITLE = "Dungeon Delver"
    VERSION = "2.0.0"

    # Tile and map settings
    TILE_SIZE = 32
    MAP_WIDTH = 50
    MAP_HEIGHT = 35
    VIEWPORT_WIDTH = 25
    VIEWPORT_HEIGHT = 20

    # Animation settings
    ANIMATION_SPEED = 0.15  # Seconds per movement
    IDLE_ANIMATION_SPEED = 8  # Frames between idle animation updates
    ENABLE_SMOOTH_MOVEMENT = True
    ENABLE_ANIMATIONS = True

    # Rendering settings
    USE_SPRITES = True  # Use graphical sprites instead of text
    RENDER_SHADOWS = True
    AMBIENT_LIGHT = 0.3  # Darkness level for unexplored areas
    
    # Colors (R, G, B)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    BROWN = (139, 69, 19)
    DARK_BROWN = (101, 67, 33)
    
    # UI Colors
    UI_BG = (30, 30, 40)
    UI_BORDER = (60, 60, 80)
    UI_TEXT = (220, 220, 220)
    UI_HIGHLIGHT = (100, 150, 255)
    
    # Game colors
    FLOOR_COLOR = (50, 50, 50)
    WALL_COLOR = (100, 100, 100)
    PLAYER_COLOR = (0, 255, 255)
    ENEMY_COLOR = (255, 0, 0)
    ITEM_COLOR = (255, 255, 0)
    STAIRS_COLOR = (128, 128, 255)
    
    # Combat settings
    BASE_CRITICAL_CHANCE = 0.05
    CRITICAL_DAMAGE_MULTIPLIER = 2.0
    DODGE_CHANCE_CAP = 0.75
    
    # Experience and leveling
    BASE_XP_REQUIREMENT = 100
    XP_GROWTH_RATE = 1.5
    MAX_LEVEL = 50
    
    # Player starting stats
    PLAYER_STARTING_HP = 100
    PLAYER_STARTING_MP = 50
    PLAYER_STARTING_STR = 10
    PLAYER_STARTING_DEX = 10
    PLAYER_STARTING_INT = 10
    PLAYER_STARTING_DEF = 5
    
    # File paths
    ASSETS_DIR = Path("assets")
    SPRITES_DIR = ASSETS_DIR / "sprites"
    SOUNDS_DIR = ASSETS_DIR / "sounds"
    DATA_DIR = ASSETS_DIR / "data"
    
    # Game states
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_INVENTORY = "inventory"
    STATE_COMBAT = "combat"
    STATE_GAME_OVER = "game_over"
    STATE_PAUSED = "paused"
    
    # Directions
    DIRECTIONS = {
        'UP': (0, -1),
        'DOWN': (0, 1),
        'LEFT': (-1, 0),
        'RIGHT': (1, 0),
        'UP_LEFT': (-1, -1),
        'UP_RIGHT': (1, -1),
        'DOWN_LEFT': (-1, 1),
        'DOWN_RIGHT': (1, 1)
    }
    
    # Weapon types and their properties
    WEAPON_TYPES = {
        'sword': {
            'damage_range': (8, 15),
            'critical_chance': 0.15,
            'range': 1,
            'type': 'physical'
        },
        'axe': {
            'damage_range': (10, 18),
            'critical_chance': 0.10,
            'range': 1,
            'type': 'physical'
        },
        'bow': {
            'damage_range': (6, 12),
            'critical_chance': 0.20,
            'range': 5,
            'type': 'physical'
        },
        'staff': {
            'damage_range': (4, 8),
            'critical_chance': 0.05,
            'range': 3,
            'type': 'magical'
        },
        'dagger': {
            'damage_range': (4, 10),
            'critical_chance': 0.25,
            'range': 1,
            'type': 'physical'
        }
    }
    
    # Enemy types
    ENEMY_TYPES = {
        'goblin': {
            'hp': 20,
            'damage': (3, 6),
            'defense': 2,
            'xp_reward': 10,
            'gold_reward': (1, 5)
        },
        'orc': {
            'hp': 35,
            'damage': (5, 10),
            'defense': 4,
            'xp_reward': 20,
            'gold_reward': (3, 8)
        },
        'skeleton': {
            'hp': 25,
            'damage': (4, 8),
            'defense': 3,
            'xp_reward': 15,
            'gold_reward': (2, 6)
        },
        'dragon': {
            'hp': 200,
            'damage': (20, 40),
            'defense': 15,
            'xp_reward': 500,
            'gold_reward': (100, 200)
        }
    }
    
    # Item rarity colors
    RARITY_COLORS = {
        'common': (255, 255, 255),
        'uncommon': (0, 255, 0),
        'rare': (0, 100, 255),
        'epic': (128, 0, 128),
        'legendary': (255, 165, 0)
    }