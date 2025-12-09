#!/usr/bin/env python3
"""
Simple test script to verify the game can start without errors
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        import pygame
        print("✓ Pygame imported successfully")
        
        from config import Config
        print("✓ Config imported successfully")
        
        from utils import Vector2, Dice, Rect
        print("✓ Utils imported successfully")
        
        from player import Player
        print("✓ Player imported successfully")
        
        from enemy import Enemy
        print("✓ Enemy imported successfully")
        
        from weapon import Weapon
        print("✓ Weapon imported successfully")
        
        from item import Item, HealthPotion, Gold
        print("✓ Item imported successfully")
        
        from inventory import Inventory
        print("✓ Inventory imported successfully")
        
        from dungeon import Dungeon, Tile
        print("✓ Dungeon imported successfully")
        
        from combat import CombatSystem
        print("✓ Combat imported successfully")
        
        from ui import UI
        print("✓ UI imported successfully")
        
        from game import Game, GameState
        print("✓ Game imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic game functionality"""
    try:
        print("\nTesting basic functionality...")
        
        # Test vector operations
        from utils import Vector2
        v1 = Vector2(5, 10)
        v2 = Vector2(3, 4)
        v3 = v1 + v2
        assert v3.x == 8 and v3.y == 14
        print("✓ Vector operations work")
        
        # Test dice rolling
        from utils import Dice
        roll = Dice.roll(6)
        assert 1 <= roll <= 6
        print("✓ Dice rolling works")
        
        # Test player creation
        from player import Player
        from utils import Vector2
        player = Player("Test Hero", Vector2(5, 5))
        assert player.name == "Test Hero"
        assert player.is_alive()
        print("✓ Player creation works")
        
        # Test weapon creation
        from weapon import Weapon
        weapon = Weapon("Test Sword", "sword", "common")
        assert weapon.name == "Test Sword"
        assert weapon.weapon_type == "sword"
        print("✓ Weapon creation works")
        
        # Test enemy creation
        from enemy import Enemy
        enemy = Enemy("goblin", Vector2(10, 10), 1)
        assert enemy.enemy_type == "goblin"
        assert enemy.is_alive()
        print("✓ Enemy creation works")
        
        # Test dungeon generation
        from dungeon import Dungeon
        dungeon = Dungeon(40, 25)
        assert len(dungeon.rooms) > 0
        assert dungeon.is_walkable(dungeon.rooms[0].center.x, dungeon.rooms[0].center.y)
        print("✓ Dungeon generation works")
        
        # Test inventory
        from inventory import Inventory
        from item import HealthPotion
        inventory = Inventory(10)
        potion = HealthPotion()
        assert inventory.add_item(potion)
        assert inventory.get_used_slots() == 1
        print("✓ Inventory works")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== Dungeon Delver Test Suite ===\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed!")
        return False
    
    print("\n✅ All tests passed! The game should work correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)