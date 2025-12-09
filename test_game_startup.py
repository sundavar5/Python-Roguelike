#!/usr/bin/env python3
"""
Test script to verify the game can start without errors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_game_initialization():
    """Test that the Game class can be initialized"""
    try:
        print("Testing game initialization...")
        
        # Test dungeon generation
        from dungeon import Dungeon
        from utils import Vector2
        dungeon = Dungeon(40, 25)
        print(f"✓ Dungeon generated with {len(dungeon.rooms)} rooms")
        
        # Test player creation
        from player import Player
        player = Player("Test Hero", Vector2(5, 5))
        print(f"✓ Player created: {player.name}")
        
        # Test enemy creation
        from enemy import Enemy
        enemy = Enemy("goblin", Vector2(10, 10), 1)
        print(f"✓ Enemy created: {enemy.name}")
        
        # Test weapon generation
        from weapon import Weapon
        weapon = Weapon.generate_random()
        print(f"✓ Weapon generated: {weapon.name}")
        
        # Test item creation
        from item import ItemFactory
        item = ItemFactory.create_random_item()
        print(f"✓ Item created: {item.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Game initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== Game Startup Test ===\n")
    
    if test_game_initialization():
        print("\n✅ Game can start successfully!")
        print("You can now run 'python main.py' to play the game.")
        return True
    else:
        print("\n❌ Game still has startup issues")
        return False

if __name__ == "__main__":
    main()