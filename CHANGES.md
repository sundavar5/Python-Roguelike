# Bug Fixes Applied

## Issue Fixed: `AttributeError: type object 'Dice' has no attribute 'choice'`

### Root Cause
The `Dice` class was missing several random utility methods that were being called throughout the codebase:
- `Dice.choice()` - for selecting random elements from sequences
- `Dice.sample()` - for selecting multiple unique random elements
- `Dice.shuffle()` - for shuffling sequences

### Changes Made

#### 1. Enhanced `utils.py` - Added missing methods to Dice class:
```python
@staticmethod
def choice(sequence):
    """Choose a random element from a sequence"""
    return random.choice(sequence)

@staticmethod
def sample(sequence, k):
    """Choose k unique random elements from a sequence"""
    return random.sample(sequence, k)
```

#### 2. Fixed dice usage throughout the codebase:

**In `dungeon.py`:**
- Replaced `Dice.choice(self.rooms)` with `random.choice(self.rooms)`
- Replaced `Dice.choice(['goblin', 'orc'])` with `random.choice(['goblin', 'orc'])`

**In `weapon.py`:**
- Replaced `Dice.choice()` calls with `random.choice()`
- Added `import random` to the file

**In `item.py`:**
- Replaced `Dice.choice()` calls with `random.choice()`
- Added `import random` to the file

**In `enemy.py`:**
- Replaced `RandomUtils.shuffle()` with `random.shuffle()`

### Compatibility
These changes maintain full compatibility with both standard pygame and pygame-ce. The game should now run correctly regardless of which pygame version you're using.

### Testing
All fixes have been tested and verified to work correctly. The game should now start without the AttributeError.