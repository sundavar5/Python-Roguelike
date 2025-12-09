"""
Enemy class with AI and combat behaviors
"""

from typing import List, Optional, Tuple
from utils import Vector2, Dice, RandomUtils
from config import Config

class Enemy:
    """Enemy character class with AI"""
    
    def __init__(self, enemy_type: str, position: Vector2, level: int = 1):
        """Initialize an enemy"""
        self.enemy_type = enemy_type
        self.position = position
        self.level = level
        
        # Get base stats from config
        enemy_config = Config.ENEMY_TYPES.get(enemy_type, Config.ENEMY_TYPES['goblin'])
        
        # Scale stats based on level
        self.max_hp = int(enemy_config['hp'] * (1 + (level - 1) * 0.2))
        self.current_hp = self.max_hp
        
        base_damage = enemy_config['damage']
        damage_multiplier = 1 + (level - 1) * 0.1
        self.damage_range = (
            int(base_damage[0] * damage_multiplier),
            int(base_damage[1] * damage_multiplier)
        )
        
        self.defense = int(enemy_config['defense'] * (1 + (level - 1) * 0.1))
        self.xp_reward = int(enemy_config['xp_reward'] * (1 + (level - 1) * 0.15))
        
        gold_range = enemy_config['gold_reward']
        self.gold_reward = (
            int(gold_range[0] * (1 + (level - 1) * 0.1)),
            int(gold_range[1] * (1 + (level - 1) * 0.1))
        )
        
        # AI properties
        self.is_active = True
        self.is_in_combat = False
        self.last_known_player_pos = None
        self.ai_state = 'idle'  # idle, hunting, attacking, fleeing
        
        # Combat properties
        self.critical_chance = 0.05
        self.dodge_chance = 0.05
        self.block_chance = 0.0
        
        # Special abilities based on type
        self.special_abilities = self._get_special_abilities(enemy_type)
        
        # Status effects
        self.status_effects = {}
        
        # Visual properties
        self.color = self._get_color_for_type(enemy_type)
        self.char = self._get_char_for_type(enemy_type)
    
    @property
    def name(self) -> str:
        """Get the display name of the enemy"""
        if self.level > 1:
            return f"Level {self.level} {self.enemy_type.title()}"
        return self.enemy_type.title()
    
    @property
    def is_alive(self) -> bool:
        """Check if the enemy is alive"""
        return self.current_hp > 0
    
    def _get_special_abilities(self, enemy_type: str) -> List[str]:
        """Get special abilities for enemy type"""
        abilities = {
            'goblin': ['sneak_attack'],
            'orc': ['berserker_rage'],
            'skeleton': ['undying'],
            'dragon': ['fire_breath', 'wing_buffet', 'terrifying_presence']
        }
        return abilities.get(enemy_type, [])
    
    def _get_color_for_type(self, enemy_type: str) -> tuple:
        """Get color for enemy type"""
        colors = {
            'goblin': (0, 128, 0),      # Green
            'orc': (128, 64, 0),        # Brown
            'skeleton': (200, 200, 200), # Light gray
            'dragon': (128, 0, 128)     # Purple
        }
        return colors.get(enemy_type, Config.RED)
    
    def _get_char_for_type(self, enemy_type: str) -> str:
        """Get character representation for enemy type"""
        chars = {
            'goblin': 'g',
            'orc': 'O',
            'skeleton': 'S',
            'dragon': 'D'
        }
        return chars.get(enemy_type, '?')
    
    def update_ai(self, player_pos: Vector2, dungeon):
        """Update enemy AI state and behavior"""
        distance_to_player = self.distance_to(player_pos)
        
        # State transitions
        if self.ai_state == 'idle':
            if distance_to_player <= 8:
                self.ai_state = 'hunting'
                self.last_known_player_pos = player_pos.copy()
        
        elif self.ai_state == 'hunting':
            if distance_to_player <= 1:
                self.ai_state = 'attacking'
            elif distance_to_player > 10:
                self.ai_state = 'idle'
            else:
                self.last_known_player_pos = player_pos.copy()
        
        elif self.ai_state == 'attacking':
            if distance_to_player > 1:
                self.ai_state = 'hunting'
            elif self.current_hp < self.max_hp * 0.3:
                self.ai_state = 'fleeing'
        
        elif self.ai_state == 'fleeing':
            if distance_to_player > 5:
                self.ai_state = 'hunting'
            elif self.current_hp >= self.max_hp * 0.6:
                self.ai_state = 'hunting'
        
        # Execute AI behavior based on current state
        if self.ai_state == 'hunting':
            self.move_towards(player_pos, dungeon)
        elif self.ai_state == 'fleeing':
            self.move_away_from(player_pos, dungeon)
        elif self.ai_state == 'idle':
            self.move_randomly(dungeon)
    
    def move_towards(self, target_pos: Vector2, dungeon):
        """Move towards a target position"""
        if not self.is_active:
            return
        
        # Simple pathfinding: move one step closer
        dx = 0
        dy = 0
        
        if target_pos.x > self.position.x:
            dx = 1
        elif target_pos.x < self.position.x:
            dx = -1
        
        if target_pos.y > self.position.y:
            dy = 1
        elif target_pos.y < self.position.y:
            dy = -1
        
        # Try to move diagonally first
        if dx != 0 and dy != 0:
            new_x = self.position.x + dx
            new_y = self.position.y + dy
            if dungeon.is_walkable(new_x, new_y):
                self.position = Vector2(new_x, new_y)
                return
        
        # Try horizontal movement
        if dx != 0:
            new_x = self.position.x + dx
            if dungeon.is_walkable(new_x, self.position.y):
                self.position = Vector2(new_x, self.position.y)
                return
        
        # Try vertical movement
        if dy != 0:
            new_y = self.position.y + dy
            if dungeon.is_walkable(self.position.x, new_y):
                self.position = Vector2(self.position.x, new_y)
                return
    
    def move_away_from(self, target_pos: Vector2, dungeon):
        """Move away from a target position"""
        if not self.is_active:
            return
        
        # Move in the opposite direction
        dx = 0
        dy = 0
        
        if target_pos.x > self.position.x:
            dx = -1
        elif target_pos.x < self.position.x:
            dx = 1
        
        if target_pos.y > self.position.y:
            dy = -1
        elif target_pos.y < self.position.y:
            dy = 1
        
        # Try to move
        new_x = self.position.x + dx
        new_y = self.position.y + dy
        
        if dungeon.is_walkable(new_x, new_y):
            self.position = Vector2(new_x, new_y)
        else:
            # If blocked, try a random direction
            self.move_randomly(dungeon)
    
    def move_randomly(self, dungeon):
        """Move in a random direction"""
        if not self.is_active:
            return
        
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),
            (-1, -1), (1, -1), (-1, 1), (1, 1)
        ]
        
        # Shuffle directions for random movement
        import random
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x = self.position.x + dx
            new_y = self.position.y + dy
            
            if dungeon.is_walkable(new_x, new_y):
                self.position = Vector2(new_x, new_y)
                return
    
    def attack(self, target) -> dict:
        """Perform an attack on a target"""
        result = {
            'hit': False,
            'critical': False,
            'damage': 0,
            'effect_applied': None
        }
        
        # Calculate hit chance
        hit_chance = 0.75  # Base 75% hit chance
        
        # Roll to hit
        if Dice.roll(100) <= hit_chance * 100:
            result['hit'] = True
            
            # Check for critical hit
            if Dice.roll(100) <= self.critical_chance * 100:
                result['critical'] = True
            
            # Calculate damage
            damage = Dice.roll_range(self.damage_range[0], self.damage_range[1])
            
            # Apply critical multiplier
            if result['critical']:
                damage = int(damage * 1.5)
            
            result['damage'] = max(1, damage)
            
            # Apply special abilities
            if self.special_abilities:
                for ability in self.special_abilities:
                    if self._use_special_ability(ability, target):
                        result['effect_applied'] = ability
                        break
        
        return result
    
    def _use_special_ability(self, ability: str, target) -> bool:
        """Use a special ability during combat"""
        if ability == 'sneak_attack':
            if Dice.roll(100) <= 30:  # 30% chance
                # Extra damage when flanking
                return True
        
        elif ability == 'berserker_rage':
            if self.current_hp < self.max_hp * 0.5:  # When wounded
                # Increased damage
                return True
        
        elif ability == 'undying':
            if self.current_hp <= 0 and Dice.roll(100) <= 20:  # 20% chance to avoid death
                self.current_hp = 1
                return True
        
        elif ability == 'fire_breath':
            if Dice.roll(100) <= 25:  # 25% chance
                # Dragon fire breath attack
                return True
        
        return False
    
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage taken"""
        # Calculate damage reduction from defense
        damage_reduction = self.defense // 3  # 1 damage reduction per 3 defense
        actual_damage = max(1, damage - damage_reduction)
        
        # Apply dodge chance
        if Dice.roll(100) <= self.dodge_chance * 100:
            actual_damage = 0  # Dodged the attack
        
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        if self.current_hp <= 0:
            self.is_active = False
            self.is_in_combat = False
        
        return actual_damage
    
    def distance_to(self, position: Vector2) -> float:
        """Calculate distance to a position"""
        return self.position.distance_to(position)
    
    def can_see_player(self, player_pos: Vector2, dungeon) -> bool:
        """Check if enemy can see the player"""
        distance = self.distance_to(player_pos)
        
        if distance > 10:  # Max sight range
            return False
        
        # Simple line of sight check (could be improved with raycasting)
        # For now, just check if there are walls blocking
        # This is a simplified version
        return True
    
    def get_display_info(self) -> dict:
        """Get display information for the UI"""
        return {
            'name': self.name,
            'hp': f"{self.current_hp}/{self.max_hp}",
            'damage': f"{self.damage_range[0]}-{self.damage_range[1]}",
            'defense': self.defense,
            'level': self.level,
            'type': self.enemy_type,
            'ai_state': self.ai_state,
            'special_abilities': self.special_abilities
        }