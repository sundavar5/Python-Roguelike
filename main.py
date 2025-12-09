#!/usr/bin/env python3
"""
Dungeon Delver - A Python Roguelike Game
Main entry point and game initialization
"""

import pygame
import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import Game
from config import Config

def main():
    """Main entry point for the game"""
    try:
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Set up the display
        screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Delver - Roguelike Adventure")
        
        # Create and run the game
        game = Game(screen)
        game.run()
        
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()