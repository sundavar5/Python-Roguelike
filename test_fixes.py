#!/usr/bin/env python3
"""
Test to verify the Dice.choice fixes work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dice_choice():
    """Test that Dice.choice works correctly"""
    try:
        from utils import Dice
        
        # Test choice method
        test_list = ['a', 'b', 'c', 'd']
        result = Dice.choice(test_list)
        assert result in test_list
        print(f"✓ Dice.choice works: {result}")
        
        # Test sample method
        result = Dice.sample(test_list, 2)
        assert len(result) == 2
        assert all(item in test_list for item in result)
        print(f"✓ Dice.sample works: {result}")
        
        return True
    except Exception as e:
        print(f"✗ Dice methods failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported after fixes"""
    try:
        from dungeon import Dungeon
        from weapon import Weapon
        from item import ItemFactory
        from enemy import Enemy
        
        print("✓ All modules import successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def main():
    print("=== Testing Dice Fixes ===\n")
    
    if test_dice_choice() and test_imports():
        print("\n✅ All fixes working correctly!")
        return True
    else:
        print("\n❌ Some fixes still needed")
        return False

if __name__ == "__main__":
    main()