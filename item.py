"""
Base item class and item types
"""

from typing import Dict, Any, Optional
import random
from utils import Dice

class Item:
    """Base item class"""
    
    def __init__(self, name: str, item_type: str, value: int = 1, weight: float = 1.0):
        """Initialize an item"""
        self.name = name
        self.item_type = item_type
        self.value = value
        self.weight = weight
        self.description = "A mysterious item."
        self.rarity = 'common'
        self.stackable = False
        self.max_stack = 1
        self.quantity = 1
        self.icon = None
        self.color = (255, 255, 255)  # White by default
    
    def use(self, user) -> bool:
        """Use the item (to be overridden by subclasses)"""
        print(f"You can't use the {self.name} that way.")
        return False
    
    def examine(self) -> str:
        """Examine the item"""
        return f"{self.name}\n{self.description}\nValue: {self.value} gold"
    
    def get_display_name(self) -> str:
        """Get display name including quantity if stackable"""
        if self.stackable and self.quantity > 1:
            return f"{self.name} ({self.quantity})"
        return self.name
    
    def get_total_value(self) -> int:
        """Get total value considering quantity"""
        return self.value * self.quantity
    
    def get_total_weight(self) -> float:
        """Get total weight considering quantity"""
        return self.weight * self.quantity
    
    def can_stack_with(self, other: 'Item') -> bool:
        """Check if this item can stack with another"""
        return (self.stackable and other.stackable and 
                self.name == other.name and 
                type(self) == type(other))
    
    def split_stack(self, amount: int) -> Optional['Item']:
        """Split a stack into a new item"""
        if not self.stackable or amount <= 0 or amount >= self.quantity:
            return None
        
        # Create a copy with the split amount
        new_item = self.__class__.__new__(self.__class__)
        new_item.__dict__.update(self.__dict__)
        new_item.quantity = amount
        
        # Reduce this item's quantity
        self.quantity -= amount
        
        return new_item
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for saving"""
        return {
            'name': self.name,
            'item_type': self.item_type,
            'value': self.value,
            'weight': self.weight,
            'description': self.description,
            'rarity': self.rarity,
            'stackable': self.stackable,
            'max_stack': self.max_stack,
            'quantity': self.quantity,
            'color': self.color
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create item from dictionary"""
        item = cls(
            data.get('name', 'Unknown Item'),
            data.get('item_type', 'misc'),
            data.get('value', 1),
            data.get('weight', 1.0)
        )
        item.description = data.get('description', 'A mysterious item.')
        item.rarity = data.get('rarity', 'common')
        item.stackable = data.get('stackable', False)
        item.max_stack = data.get('max_stack', 1)
        item.quantity = data.get('quantity', 1)
        item.color = data.get('color', (255, 255, 255))
        return item

class HealthPotion(Item):
    """Health restoration potion"""
    
    def __init__(self, name: str = "Health Potion", healing_amount: int = 25):
        super().__init__(name, 'potion', value=15, weight=0.5)
        self.healing_amount = healing_amount
        self.description = f"Restores {healing_amount} health when consumed."
        self.color = (255, 0, 0)  # Red
        self.stackable = True
        self.max_stack = 10
    
    def use(self, user) -> bool:
        """Use the health potion"""
        if hasattr(user, 'heal'):
            healed = user.heal(self.healing_amount)
            if healed > 0:
                print(f"You drink the {self.name} and restore {healed} health!")
                return True
            else:
                print("You're already at full health!")
                return False
        return False
    
    @classmethod
    def create_minor(cls) -> 'HealthPotion':
        return cls("Minor Health Potion", 15)
    
    @classmethod
    def create_major(cls) -> 'HealthPotion':
        return cls("Major Health Potion", 50)
    
    @classmethod
    def create_superior(cls) -> 'HealthPotion':
        return cls("Superior Health Potion", 100)

class ManaPotion(Item):
    """Mana restoration potion"""
    
    def __init__(self, name: str = "Mana Potion", mana_amount: int = 20):
        super().__init__(name, 'potion', value=12, weight=0.5)
        self.mana_amount = mana_amount
        self.description = f"Restores {mana_amount} mana when consumed."
        self.color = (0, 0, 255)  # Blue
        self.stackable = True
        self.max_stack = 10
    
    def use(self, user) -> bool:
        """Use the mana potion"""
        if hasattr(user, 'restore_mana'):
            restored = user.restore_mana(self.mana_amount)
            if restored > 0:
                print(f"You drink the {self.name} and restore {restored} mana!")
                return True
            else:
                print("You're already at full mana!")
                return False
        return False
    
    @classmethod
    def create_minor(cls) -> 'ManaPotion':
        return cls("Minor Mana Potion", 10)
    
    @classmethod
    def create_major(cls) -> 'ManaPotion':
        return cls("Major Mana Potion", 40)

class Gold(Item):
    """Gold coins"""
    
    def __init__(self, amount: int = 1):
        super().__init__("Gold", 'currency', value=1, weight=0.01)
        self.quantity = amount
        self.description = f"{amount} gold coins."
        self.color = (255, 215, 0)  # Gold color
        self.stackable = True
        self.max_stack = 9999
    
    def use(self, user) -> bool:
        """Gold can't be used directly, but can be picked up"""
        print("Gold is automatically added to your purse when picked up.")
        return False
    
    def get_display_name(self) -> str:
        """Get display name with amount"""
        return f"{self.quantity} Gold"

class Food(Item):
    """Food item that restores some health"""
    
    def __init__(self, name: str, healing: int, value: int):
        super().__init__(name, 'food', value=value, weight=1.0)
        self.healing = healing
        self.description = f"A {name.lower()} that restores {healing} health."
        self.color = (139, 69, 19)  # Brown
        self.stackable = True
        self.max_stack = 5
    
    def use(self, user) -> bool:
        """Eat the food"""
        if hasattr(user, 'heal'):
            healed = user.heal(self.healing)
            if healed > 0:
                print(f"You eat the {self.name} and restore {healed} health!")
                return True
            else:
                print("You're not hungry!")
                return False
        return False
    
    @classmethod
    def create_bread(cls) -> 'Food':
        return cls("Bread", 10, 5)
    
    @classmethod
    def create_meat(cls) -> 'Food':
        return cls("Cooked Meat", 20, 8)
    
    @classmethod
    def create_fruit(cls) -> 'Food':
        return cls("Fresh Fruit", 15, 6)

class Scroll(Item):
    """Magic scroll with various effects"""
    
    def __init__(self, name: str, scroll_type: str):
        super().__init__(name, 'scroll', value=25, weight=0.1)
        self.scroll_type = scroll_type
        self.description = f"A magical scroll of {scroll_type}."
        self.color = (255, 255, 0)  # Yellow
        self.stackable = True
        self.max_stack = 5
    
    def use(self, user) -> bool:
        """Use the scroll"""
        if self.scroll_type == 'identification':
            print("You read the scroll of identification!")
            # Would identify items in inventory
            return True
        elif self.scroll_type == 'teleportation':
            print("You read the scroll of teleportation!")
            # Would teleport the player
            return True
        elif self.scroll_type == 'fire':
            print("The scroll erupts in flames!")
            # Would create fire effect
            return True
        
        return False
    
    @classmethod
    def create_identification(cls) -> 'Scroll':
        return cls("Scroll of Identification", 'identification')
    
    @classmethod
    def create_teleportation(cls) -> 'Scroll':
        return cls("Scroll of Teleportation", 'teleportation')
    
    @classmethod
    def create_fire(cls) -> 'Scroll':
        return cls("Scroll of Fire", 'fire')

class Key(Item):
    """Key item for opening doors"""
    
    def __init__(self, name: str = "Rusty Key", key_id: str = "unknown"):
        super().__init__(name, 'key', value=10, weight=0.2)
        self.key_id = key_id
        self.description = f"A {name.lower()} that might open something."
        self.color = (192, 192, 192)  # Silver
        self.stackable = False
    
    def use(self, user) -> bool:
        """Use the key"""
        print("Use this key near a locked door or chest.")
        return False

class Gem(Item):
    """Valuable gem"""
    
    def __init__(self, name: str, value: int, rarity: str = 'common'):
        super().__init__(name, 'gem', value=value, weight=0.1)
        self.rarity = rarity
        self.description = f"A precious {name.lower()}."
        self.color = self._get_color_for_gem(name)
        self.stackable = True
        self.max_stack = 10
    
    def _get_color_for_gem(self, name: str) -> tuple:
        """Get color for gem type"""
        colors = {
            'Ruby': (220, 20, 60),
            'Sapphire': (0, 0, 139),
            'Emerald': (50, 205, 50),
            'Diamond': (255, 255, 255),
            'Amethyst': (128, 0, 128),
            'Topaz': (255, 165, 0)
        }
        return colors.get(name, (200, 200, 200))
    
    def use(self, user) -> bool:
        """Gems can't be used directly"""
        print("This gem is valuable and can be sold.")
        return False
    
    @classmethod
    def create_random_gem(cls) -> 'Gem':
        """Create a random gem"""
        gems = [
            ('Ruby', 50, 'uncommon'),
            ('Sapphire', 50, 'uncommon'),
            ('Emerald', 60, 'uncommon'),
            ('Diamond', 100, 'rare'),
            ('Amethyst', 40, 'uncommon'),
            ('Topaz', 30, 'common')
        ]
        
        name, value, rarity = random.choice(gems)
        return cls(name, value, rarity)

# Item factory for creating random items
class ItemFactory:
    """Factory for creating items"""
    
    @staticmethod
    def create_random_item(item_type: str = None) -> Item:
        """Create a random item"""
        if item_type is None:
            item_type = random.choice([
                'potion', 'food', 'scroll', 'gem', 'weapon'
            ])
        
        if item_type == 'potion':
            potion_type = random.choice(['health', 'mana'])
            if potion_type == 'health':
                return HealthPotion.create_minor()
            else:
                return ManaPotion.create_minor()
        
        elif item_type == 'food':
            return random.choice([
                Food.create_bread(),
                Food.create_meat(),
                Food.create_fruit()
            ])
        
        elif item_type == 'scroll':
            return random.choice([
                Scroll.create_identification(),
                Scroll.create_teleportation(),
                Scroll.create_fire()
            ])
        
        elif item_type == 'gem':
            return Gem.create_random_gem()
        
        elif item_type == 'weapon':
            # Import here to avoid circular import
            from weapon import Weapon
            return Weapon.generate_random()
        
        # Default fallback
        return Item("Mysterious Item", 'misc', 5, 1.0)
    
    @staticmethod
    def create_gold(amount: int = None) -> Gold:
        """Create gold coins"""
        if amount is None:
            amount = random.randint(1, 50)
        return Gold(amount)