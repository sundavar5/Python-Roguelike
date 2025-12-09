#!/usr/bin/env python3
"""
Direct test of the Dice.choice method
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dice_choice_direct():
    """Test Dice.choice directly"""
    try:
        from utils import Dice
        
        # Test basic functionality
        test_list = ['a', 'b', 'c', 'd']
        result = Dice.choice(test_list)
        print(f"Dice.choice worked: {result}")
        
        # Test with dungeon rooms simulation
        class MockRoom:
            def __init__(self, name):
                self.name = name
        
        rooms = [MockRoom(f"Room {i}") for i in range(5)]
        chosen_room = Dice.choice(rooms)
        print(f"Dice.choice with rooms worked: {chosen_room.name}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Dice.choice directly...")
    if test_dice_choice_direct():
        print("✅ Dice.choice is working!")
    else:
        print("❌ Dice.choice is still broken")