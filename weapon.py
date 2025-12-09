"""
Weapon system with different weapon types and properties
"""

from typing import Tuple, Optional
import random
from utils import Dice
from config import Config

class Weapon:
    """Weapon class with damage, critical chance, and special properties"""
    
    def __init__(self, name: str, weapon_type: str, rarity: str = "common"):
        """Initialize a weapon"""
        self.name = name
        self.weapon_type = weapon_type
        self.rarity = rarity
        
        # Get base properties from config
        weapon_config = Config.WEAPON_TYPES.get(weapon_type, Config.WEAPON_TYPES['sword'])
        
        # Base damage range
        base_min, base_max = weapon_config['damage_range']
        
        # Apply rarity modifications
        self.damage_range = self._apply_rarity_bonus(base_min, base_max, rarity)
        self.critical_chance = weapon_config['critical_chance']
        self.range = weapon_config['range']
        self.damage_type = weapon_config['type']
        
        # Special properties based on rarity
        self.special_effects = []
        self.enchantments = []
        
        # Apply rarity-based bonuses
        self._apply_rarity_effects(rarity)
        
        # Value for selling/buying
        self.value = self._calculate_value()
        
        # Durability (weapons can break)
        self.max_durability = 100
        self.current_durability = self.max_durability
    
    def _apply_rarity_bonus(self, base_min: int, base_max: int, rarity: str) -> Tuple[int, int]:
        """Apply damage bonus based on rarity"""
        rarity_multipliers = {
            'common': 1.0,
            'uncommon': 1.2,
            'rare': 1.5,
            'epic': 2.0,
            'legendary': 2.5
        }
        
        multiplier = rarity_multipliers.get(rarity, 1.0)
        
        new_min = int(base_min * multiplier)
        new_max = int(base_max * multiplier)
        
        return (new_min, new_max)
    
    def _apply_rarity_effects(self, rarity: str):
        """Apply special effects based on rarity"""
        if rarity == 'uncommon':
            # Small chance for a minor effect
            if Dice.roll(100) <= 30:
                self.special_effects.append('keen')  # +5% crit chance
                self.critical_chance += 0.05
        
        elif rarity == 'rare':
            # Guaranteed minor effect, chance for medium effect
            self.special_effects.append('balanced')  # +1 min damage
            self.damage_range = (self.damage_range[0] + 1, self.damage_range[1])
            
            if Dice.roll(100) <= 40:
                effect = Dice.choice(['elemental', 'vampiric', 'precise'])
                self.special_effects.append(effect)
                if effect == 'elemental':
                    self.damage_type = 'elemental'
                elif effect == 'vampiric':
                    self.enchantments.append('life_steal_5%')
                elif effect == 'precise':
                    self.critical_chance += 0.10
        
        elif rarity == 'epic':
            # Guaranteed effects
            self.special_effects.extend(['masterwork', 'enhanced'])
            self.damage_range = (self.damage_range[0] + 2, self.damage_range[1] + 2)
            self.critical_chance += 0.10
            
            # Additional random effect
            effect = Dice.choice(['flaming', 'frost', 'shocking', 'vampiric'])
            self.special_effects.append(effect)
            if effect in ['flaming', 'frost', 'shocking']:
                self.damage_type = effect
                self.enchantments.append(f'{effect}_proc_20%')
            elif effect == 'vampiric':
                self.enchantments.append('life_steal_15%')
        
        elif rarity == 'legendary':
            # Multiple guaranteed powerful effects
            self.special_effects.extend(['legendary', 'perfect', 'enhanced'])
            self.damage_range = (self.damage_range[0] + 3, self.damage_range[1] + 5)
            self.critical_chance += 0.15
            
            # Multiple special effects
            effects = Dice.sample(['flaming', 'frost', 'shocking', 'vampiric', 'holy', 'unholy'], 2)
            self.special_effects.extend(effects)
            
            for effect in effects:
                if effect in ['flaming', 'frost', 'shocking', 'holy', 'unholy']:
                    self.damage_type = effect
                    self.enchantments.append(f'{effect}_proc_30%')
                elif effect == 'vampiric':
                    self.enchantments.append('life_steal_25%')
    
    def _calculate_value(self) -> int:
        """Calculate the gold value of the weapon"""
        base_value = 50
        
        # Value based on damage
        damage_value = (self.damage_range[0] + self.damage_range[1]) * 5
        
        # Value based on critical chance
        crit_value = int(self.critical_chance * 100) * 2
        
        # Rarity multiplier
        rarity_multipliers = {
            'common': 1,
            'uncommon': 2,
            'rare': 5,
            'epic': 15,
            'legendary': 50
        }
        
        rarity_value = rarity_multipliers.get(self.rarity, 1)
        
        # Special effects value
        effect_value = len(self.special_effects) * 25
        
        total_value = (base_value + damage_value + crit_value + effect_value) * rarity_value
        return max(1, total_value)
    
    def roll_damage(self) -> int:
        """Roll damage within the weapon's damage range"""
        damage = Dice.roll_range(self.damage_range[0], self.damage_range[1])
        
        # Apply durability penalty if weapon is damaged
        if self.current_durability < self.max_durability:
            penalty = (self.max_durability - self.current_durability) / self.max_durability
            damage = int(damage * (1 - penalty * 0.5))  # Up to 50% damage penalty
        
        return max(1, damage)
    
    def use(self) -> bool:
        """Use the weapon (decreases durability)"""
        if self.current_durability > 0:
            self.current_durability -= 1
            return True
        return False  # Weapon is broken
    
    def repair(self, amount: int = 10) -> int:
        """Repair the weapon"""
        old_durability = self.current_durability
        self.current_durability = min(self.max_durability, self.current_durability + amount)
        return self.current_durability - old_durability
    
    def is_broken(self) -> bool:
        """Check if the weapon is broken"""
        return self.current_durability <= 0
    
    def get_description(self) -> str:
        """Get a detailed description of the weapon"""
        lines = [
            f"{self.name} ({self.rarity.title()})",
            f"Type: {self.weapon_type.title()}",
            f"Damage: {self.damage_range[0]}-{self.damage_range[1]}",
            f"Critical Chance: {self.critical_chance:.1%}",
            f"Range: {self.range}",
            f"Damage Type: {self.damage_type.title()}",
            f"Durability: {self.current_durability}/{self.max_durability}",
            f"Value: {self.value} gold"
        ]
        
        if self.special_effects:
            lines.append(f"Special: {', '.join(self.special_effects)}")
        
        if self.enchantments:
            lines.append(f"Enchantments: {', '.join(self.enchantments)}")
        
        return "\n".join(lines)
    
    def get_short_description(self) -> str:
        """Get a short description for inventory display"""
        return f"{self.name} ({self.damage_range[0]}-{self.damage_range[1]} dmg)"
    
    def get_display_color(self) -> tuple:
        """Get the display color based on rarity"""
        return Config.RARITY_COLORS.get(self.rarity, Config.WHITE)
    
    @classmethod
    def generate_random(cls, weapon_type: str = None, rarity: str = None, min_level: int = 1) -> 'Weapon':
        """Generate a random weapon"""
        # Choose weapon type if not specified
        if weapon_type is None:
            weapon_type = Dice.choice(list(Config.WEAPON_TYPES.keys()))
        
        # Choose rarity if not specified (weighted towards common)
        if rarity is None:
            rarity_choices = [
                ('common', 60),
                ('uncommon', 25),
                ('rare', 10),
                ('epic', 4),
                ('legendary', 1)
            ]
            rarity = cls._weighted_choice(rarity_choices)
        
        # Generate name based on type and rarity
        name = cls._generate_name(weapon_type, rarity)
        
        return cls(name, weapon_type, rarity)
    
    @staticmethod
    def _weighted_choice(choices):
        """Make a weighted random choice"""
        total_weight = sum(weight for _, weight in choices)
        r = random.uniform(0, total_weight)
        
        current_weight = 0
        for item, weight in choices:
            current_weight += weight
            if r <= current_weight:
                return item
        
        return choices[-1][0]
    
    @staticmethod
    def _generate_name(weapon_type: str, rarity: str) -> str:
        """Generate a weapon name based on type and rarity"""
        prefixes = {
            'common': ['Rusty', 'Crude', 'Simple', 'Basic'],
            'uncommon': ['Fine', 'Sharp', 'Balanced', 'Quality'],
            'rare': ['Superior', 'Exceptional', 'Masterwork', 'Gleaming'],
            'epic': ['Flaming', 'Frost', 'Lightning', 'Vampiric'],
            'legendary': ['Legendary', 'Mythic', 'Eternal', 'Divine']
        }
        
        weapon_names = {
            'sword': ['Sword', 'Blade', 'Longsword', 'Broadsword'],
            'axe': ['Axe', 'Battle Axe', 'War Axe', 'Cleaver'],
            'bow': ['Bow', 'Longbow', 'Shortbow', 'Recurve Bow'],
            'staff': ['Staff', 'Magic Staff', 'Arcane Staff', 'Wizard Staff'],
            'dagger': ['Dagger', 'Knife', 'Blade', 'Stiletto']
        }
        
        prefix = random.choice(prefixes.get(rarity, ['']))
        weapon_name = random.choice(weapon_names.get(weapon_type, [weapon_type.title()]))
        
        if prefix:
            return f"{prefix} {weapon_name}"
        return weapon_name