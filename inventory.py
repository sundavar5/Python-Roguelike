"""
Inventory system for managing items
"""

from typing import List, Optional, Dict, Any, Tuple
from item import Item
from weapon import Weapon
from config import Config

class Inventory:
    """Inventory class for managing items"""
    
    def __init__(self, capacity: int = 20):
        """Initialize inventory with given capacity"""
        self.capacity = capacity
        self.items: List[Optional[Item]] = [None] * capacity
        self.gold = 0
    
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory"""
        # Find first empty slot
        for i in range(self.capacity):
            if self.items[i] is None:
                self.items[i] = item
                return True
        
        return False  # Inventory full
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from inventory"""
        for i in range(self.capacity):
            if self.items[i] == item:
                self.items[i] = None
                return True
        
        return False  # Item not found
    
    def remove_item_at(self, index: int) -> Optional[Item]:
        """Remove and return item at given index"""
        if 0 <= index < self.capacity:
            item = self.items[index]
            self.items[index] = None
            return item
        
        return None
    
    def get_item_at(self, index: int) -> Optional[Item]:
        """Get item at given index without removing it"""
        if 0 <= index < self.capacity:
            return self.items[index]
        return None
    
    def move_item(self, from_index: int, to_index: int) -> bool:
        """Move an item from one slot to another"""
        if (0 <= from_index < self.capacity and 
            0 <= to_index < self.capacity and 
            from_index != to_index):
            
            item = self.items[from_index]
            target_item = self.items[to_index]
            
            # Swap items
            self.items[from_index] = target_item
            self.items[to_index] = item
            
            return True
        
        return False
    
    def is_full(self) -> bool:
        """Check if inventory is full"""
        return all(item is not None for item in self.items)
    
    def is_empty(self) -> bool:
        """Check if inventory is empty"""
        return all(item is None for item in self.items)
    
    def get_used_slots(self) -> int:
        """Get number of used slots"""
        return sum(1 for item in self.items if item is not None)
    
    def get_empty_slots(self) -> int:
        """Get number of empty slots"""
        return self.capacity - self.get_used_slots()
    
    def add_gold(self, amount: int) -> int:
        """Add gold to inventory"""
        if amount > 0:
            self.gold += amount
            return amount
        return 0
    
    def remove_gold(self, amount: int) -> int:
        """Remove gold from inventory"""
        if amount > 0:
            actual_amount = min(amount, self.gold)
            self.gold -= actual_amount
            return actual_amount
        return 0
    
    def has_gold(self, amount: int) -> bool:
        """Check if inventory has enough gold"""
        return self.gold >= amount
    
    def find_items_by_type(self, item_type: str) -> List[Tuple[int, Item]]:
        """Find all items of a specific type"""
        found_items = []
        for i, item in enumerate(self.items):
            if item is not None and item.item_type == item_type:
                found_items.append((i, item))
        return found_items
    
    def find_items_by_name(self, name: str) -> List[Tuple[int, Item]]:
        """Find all items with a specific name"""
        found_items = []
        for i, item in enumerate(self.items):
            if item is not None and name.lower() in item.name.lower():
                found_items.append((i, item))
        return found_items
    
    def get_total_weight(self) -> float:
        """Get total weight of all items"""
        return sum(item.weight for item in self.items if item is not None)
    
    def get_total_value(self) -> int:
        """Get total value of all items"""
        return sum(item.value for item in self.items if item is not None)
    
    def sort_items(self, key: str = 'name'):
        """Sort items in inventory"""
        # Get all non-None items
        non_none_items = [item for item in self.items if item is not None]
        
        # Sort based on key
        if key == 'name':
            non_none_items.sort(key=lambda x: x.name)
        elif key == 'value':
            non_none_items.sort(key=lambda x: x.value, reverse=True)
        elif key == 'weight':
            non_none_items.sort(key=lambda x: x.weight)
        elif key == 'type':
            non_none_items.sort(key=lambda x: x.item_type)
        
        # Clear inventory and add sorted items
        self.clear()
        for i, item in enumerate(non_none_items):
            if i < self.capacity:
                self.items[i] = item
    
    def clear(self):
        """Clear all items from inventory"""
        self.items = [None] * self.capacity
    
    def get_items(self) -> List[Optional[Item]]:
        """Get a copy of all items"""
        return self.items.copy()
    
    def get_non_none_items(self) -> List[Item]:
        """Get all non-None items"""
        return [item for item in self.items if item is not None]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary for saving"""
        return {
            'capacity': self.capacity,
            'items': [item.to_dict() if item else None for item in self.items],
            'gold': self.gold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Inventory':
        """Create inventory from dictionary"""
        inventory = cls(data.get('capacity', 20))
        inventory.gold = data.get('gold', 0)
        
        # Restore items
        items_data = data.get('items', [])
        for i, item_data in enumerate(items_data):
            if i < inventory.capacity and item_data:
                # This would need to be expanded to handle different item types
                if item_data.get('item_type') == 'weapon':
                    inventory.items[i] = Weapon.from_dict(item_data)
                else:
                    inventory.items[i] = Item.from_dict(item_data)
        
        return inventory