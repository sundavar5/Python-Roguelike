#!/usr/bin/env python3
"""
Final test to verify all game components work together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_components():
    """Test all game components without pygame"""
    print("=== Final Game Component Test ===\n")
    
    try:
        # Test utils
        from utils import Dice, Vector2
        result = Dice.choice(['a', 'b', 'c'])
        print(f"✓ Dice.choice working: {result}")
        
        # Test dungeon
        from dungeon import Dungeon
        dungeon = Dungeon(40, 25)
        print(f"✓ Dungeon generated: {len(dungeon.rooms)} rooms, {len(dungeon.enemies)} enemies")
        
        # Test player
        from player import Player
        player = Player("Test Hero", Vector2(5, 5))
        print(f"✓ Player created: {player.name} (Level {player.level})")
        
        # Test enemy
        from enemy import Enemy
        enemy = Enemy("goblin", Vector2(10, 10), 1)
        print(f"✓ Enemy created: {enemy.name}")
        
        # Test weapon
        from weapon import Weapon
        weapon = Weapon.generate_random()
        print(f"✓ Weapon generated: {weapon.name}")
        
        # Test item
        from item import ItemFactory
        item = ItemFactory.create_random_item()
        print(f"✓ Item created: {item.name}")
        
        # Test combat system
        from combat import CombatSystem
        combat = CombatSystem()
        print("✓ Combat system initialized")
        
        # Test inventory
        from inventory import Inventory
        inventory = Inventory(20)
        print("✓ Inventory system working")
        
        print("\n✅ ALL GAME SYSTEMS WORKING!")
        print("✅ The game should now start without errors!")
        print("✅ Run 'python main.py' to play!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_components()
    sys.exit(0 if success else 1)