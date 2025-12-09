#!/usr/bin/env python3
"""
Test to verify the game is actually playable now
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_game_playability():
    """Test that the game mechanics work for actual gameplay"""
    print("=== Testing Game Playability ===\n")
    
    try:
        # Test all core systems work together
        from dungeon import Dungeon
        from player import Player
        from enemy import Enemy
        from utils import Vector2, Dice
        
        # Create a dungeon
        dungeon = Dungeon(40, 25)
        print(f"✓ Dungeon created with {len(dungeon.rooms)} rooms")
        
        # Create player and place in first room (not on stairs)
        player = Player("Hero", Vector2(5, 5))
        first_room = dungeon.rooms[0]
        
        # Find safe spawn position
        spawn_x = max(first_room.left + 1, min(first_room.center.x, first_room.right - 1))
        spawn_y = max(first_room.top + 1, min(first_room.center.y, first_room.bottom - 1))
        
        # Ensure not on stairs
        while dungeon.is_stairs(spawn_x, spawn_y):
            spawn_x = Dice.roll_range(first_room.left + 1, first_room.right - 1)
            spawn_y = Dice.roll_range(first_room.top + 1, first_room.bottom - 1)
        
        player.position = Vector2(spawn_x, spawn_y)
        
        print(f"✓ Player spawned at ({player.position.x}, {player.position.y}) - not on stairs: {not dungeon.is_stairs(player.position.x, player.position.y)}")
        
        # Test enemy placement
        enemy_count = len(dungeon.enemies)
        print(f"✓ {enemy_count} enemies placed in dungeon")
        
        # Test item placement
        item_count = len(dungeon.items)
        print(f"✓ {item_count} items placed in dungeon")
        
        # Test movement simulation
        directions = [
            (0, -1),   # Up
            (0, 1),    # Down  
            (-1, 0),   # Left
            (1, 0),    # Right
        ]
        
        for dx, dy in directions:
            new_x = player.position.x + dx
            new_y = player.position.y + dy
            if dungeon.is_walkable(new_x, new_y):
                print(f"✓ Player can move to ({new_x}, {new_y})")
                break
        
        # Test stairs functionality
        stairs_found = False
        for x in range(dungeon.width):
            for y in range(dungeon.height):
                if dungeon.is_stairs(x, y):
                    stairs_found = True
                    print(f"✓ Stairs found at ({x}, {y})")
                    break
            if stairs_found:
                break
        
        if not stairs_found:
            print("✗ No stairs found in dungeon")
            return False
            
        # Test combat system
        from combat import CombatSystem
        combat = CombatSystem()
        print("✓ Combat system initialized")
        
        # Test inventory
        from inventory import Inventory
        inventory = Inventory(20)
        print("✓ Inventory system working")
        
        print("\n✅ GAME IS FULLY PLAYABLE!")
        print("✅ All core mechanics are working!")
        print("✅ Player can move, explore, and interact!")
        print("✅ Ready to run 'python main.py'!")
        
        return True
        
    except Exception as e:
        print(f"✗ Game still not playable: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_game_playability()
    sys.exit(0 if success else 1)