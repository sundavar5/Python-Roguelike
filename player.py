"""
Player character class with stats, inventory, and abilities
"""

from typing import List, Optional, Dict
from utils import Vector2, Dice
from config import Config
from inventory import Inventory
from weapon import Weapon

class Player:
    """Player character class"""
    
    def __init__(self, name: str, position: Vector2):
        """Initialize the player"""
        self.name = name
        self.position = position
        
        # Basic stats
        self.level = 1
        self.experience = 0
        self.experience_to_next = Config.BASE_XP_REQUIREMENT
        
        # Core attributes
        self.max_hp = Config.PLAYER_STARTING_HP
        self.current_hp = self.max_hp
        self.max_mp = Config.PLAYER_STARTING_MP
        self.current_mp = self.max_mp
        
        self.strength = Config.PLAYER_STARTING_STR
        self.dexterity = Config.PLAYER_STARTING_DEX
        self.intelligence = Config.PLAYER_STARTING_INT
        self.defense = Config.PLAYER_STARTING_DEF
        
        # Combat stats
        self.base_damage = (1, 4)  # Min, max damage
        self.critical_chance = Config.BASE_CRITICAL_CHANCE
        self.dodge_chance = 0.1
        self.block_chance = 0.05
        
        # Equipment
        self.equipped_weapon: Optional[Weapon] = None
        self.equipped_armor = None
        self.equipped_shield = None
        
        # Inventory
        self.inventory = Inventory(20)  # 20 slot inventory
        
        # Give player a starting weapon
        starter_weapon = Weapon("Rusty Sword", "sword", "common")
        self.inventory.add_item(starter_weapon)
        self.equip_weapon(starter_weapon)
        
        # Status effects
        self.status_effects: Dict[str, int] = {}  # effect_name: duration
        
        # Skills and abilities
        self.skill_points = 0
        self.abilities: List[str] = []
        
        # Meta progress
        self.total_kills = 0
        self.dungeons_cleared = 0
        self.gold_earned = 0
    
    @property
    def damage(self) -> tuple:
        """Get current damage range including weapon bonuses"""
        base_min, base_max = self.base_damage
        
        if self.equipped_weapon:
            weapon_min, weapon_max = self.equipped_weapon.damage_range
            return (base_min + weapon_min, base_max + weapon_max)
        
        return self.base_damage
    
    @property
    def total_defense(self) -> int:
        """Get total defense including armor bonuses"""
        defense = self.defense
        
        if self.equipped_armor:
            defense += self.equipped_armor.defense_bonus
        if self.equipped_shield:
            defense += self.equipped_shield.defense_bonus
        
        return defense
    
    @property
    def total_critical_chance(self) -> float:
        """Get total critical chance including weapon bonuses"""
        crit_chance = self.critical_chance
        
        if self.equipped_weapon:
            crit_chance += self.equipped_weapon.critical_chance
        
        return min(crit_chance, 0.8)  # Cap at 80%
    
    def equip_weapon(self, weapon: Weapon) -> bool:
        """Equip a weapon"""
        if weapon in self.inventory.items:
            self.equipped_weapon = weapon
            return True
        return False
    
    def unequip_weapon(self):
        """Unequip current weapon"""
        self.equipped_weapon = None
    
    def attack(self, target) -> dict:
        """Perform an attack on a target"""
        result = {
            'hit': False,
            'critical': False,
            'damage': 0,
            'blocked': False
        }
        
        # Calculate hit chance
        hit_chance = 0.8 + (self.dexterity * 0.02)  # Base 80% + dex bonus
        hit_chance = min(hit_chance, 0.95)  # Cap at 95%
        
        # Roll to hit
        if Dice.roll(100) <= hit_chance * 100:
            result['hit'] = True
            
            # Check for critical hit
            if Dice.roll(100) <= self.total_critical_chance * 100:
                result['critical'] = True
            
            # Calculate damage
            damage_min, damage_max = self.damage
            base_damage = Dice.roll_range(damage_min, damage_max)
            
            # Apply critical multiplier
            if result['critical']:
                base_damage = int(base_damage * Config.CRITICAL_DAMAGE_MULTIPLIER)
            
            # Apply strength bonus
            strength_bonus = self.strength // 5  # 1 damage per 5 strength
            total_damage = base_damage + strength_bonus
            
            result['damage'] = max(1, total_damage)  # Minimum 1 damage
        
        return result
    
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage taken"""
        # Calculate damage reduction from defense
        damage_reduction = self.total_defense // 2  # 1 damage reduction per 2 defense
        actual_damage = max(1, damage - damage_reduction)
        
        # Apply dodge chance
        if Dice.roll(100) <= self.dodge_chance * 100:
            actual_damage = 0  # Dodged the attack
        
        # Apply block chance if shield is equipped
        if self.equipped_shield and Dice.roll(100) <= self.block_chance * 100:
            actual_damage = max(1, actual_damage // 2)  # Block reduces damage by half
        
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal the player"""
        actual_heal = min(amount, self.max_hp - self.current_hp)
        self.current_hp += actual_heal
        return actual_heal
    
    def restore_mana(self, amount: int) -> int:
        """Restore mana"""
        actual_restore = min(amount, self.max_mp - self.current_mp)
        self.current_mp += actual_restore
        return actual_restore
    
    def gain_experience(self, amount: int) -> bool:
        """Gain experience and check for level up"""
        self.experience += amount
        
        if self.experience >= self.experience_to_next:
            self.level_up()
            return True
        
        return False
    
    def level_up(self):
        """Level up the player"""
        self.level += 1
        self.skill_points += 3  # 3 skill points per level
        
        # Increase experience requirement for next level
        self.experience_to_next = int(
            Config.BASE_XP_REQUIREMENT * (Config.XP_GROWTH_RATE ** (self.level - 1))
        )
        
        # Increase stats
        self.max_hp += 10
        self.current_hp = self.max_hp  # Full heal on level up
        self.max_mp += 5
        self.current_mp = self.max_mp  # Full mana on level up
        
        # Increase attributes (small random increases)
        self.strength += Dice.roll_range(1, 3)
        self.dexterity += Dice.roll_range(1, 3)
        self.intelligence += Dice.roll_range(1, 3)
        self.defense += Dice.roll_range(1, 2)
        
        print(f"Level up! You are now level {self.level}")
        print(f"Gained 3 skill points!")
    
    def add_status_effect(self, effect_name: str, duration: int):
        """Add a status effect"""
        self.status_effects[effect_name] = duration
    
    def remove_status_effect(self, effect_name: str):
        """Remove a status effect"""
        self.status_effects.pop(effect_name, None)
    
    def update_status_effects(self):
        """Update status effect durations"""
        effects_to_remove = []
        
        for effect, duration in self.status_effects.items():
            self.status_effects[effect] = duration - 1
            if duration <= 1:
                effects_to_remove.append(effect)
        
        for effect in effects_to_remove:
            self.remove_status_effect(effect)
    
    def get_stat(self, stat_name: str) -> int:
        """Get a stat value by name"""
        return getattr(self, stat_name, 0)
    
    def set_stat(self, stat_name: str, value: int):
        """Set a stat value by name"""
        if hasattr(self, stat_name):
            setattr(self, stat_name, value)
    
    def get_health_percentage(self) -> float:
        """Get health as a percentage (0.0 to 1.0)"""
        return self.current_hp / self.max_hp if self.max_hp > 0 else 0
    
    def get_mana_percentage(self) -> float:
        """Get mana as a percentage (0.0 to 1.0)"""
        return self.current_mp / self.max_mp if self.max_mp > 0 else 0
    
    def get_experience_percentage(self) -> float:
        """Get experience progress as a percentage (0.0 to 1.0)"""
        return self.experience / self.experience_to_next if self.experience_to_next > 0 else 0
    
    def is_alive(self) -> bool:
        """Check if the player is alive"""
        return self.current_hp > 0
    
    def get_display_info(self) -> dict:
        """Get display information for the UI"""
        return {
            'name': self.name,
            'level': self.level,
            'hp': f"{self.current_hp}/{self.max_hp}",
            'mp': f"{self.current_mp}/{self.max_mp}",
            'experience': f"{self.experience}/{self.experience_to_next}",
            'strength': self.strength,
            'dexterity': self.dexterity,
            'intelligence': self.intelligence,
            'defense': self.total_defense,
            'damage': f"{self.damage[0]}-{self.damage[1]}",
            'critical_chance': f"{self.total_critical_chance:.1%}",
            'equipped_weapon': self.equipped_weapon.name if self.equipped_weapon else "None",
            'status_effects': list(self.status_effects.keys())
        }