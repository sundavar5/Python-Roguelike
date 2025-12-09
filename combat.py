"""
Combat system for handling battles between entities
"""

from typing import Optional, Dict, Any, List
from utils import Dice
from config import Config

class CombatSystem:
    """Combat system for managing battles"""
    
    def __init__(self):
        """Initialize combat system"""
        self.player = None
        self.enemy = None
        self.is_active = False
        self.player_turn = True
        self.round = 1
        self.log = []
    
    def start_combat(self, player, enemy):
        """Start combat between player and enemy"""
        self.player = player
        self.enemy = enemy
        self.is_active = True
        self.player_turn = True
        self.round = 1
        self.log.clear()
        
        enemy.is_in_combat = True
        self.add_to_log(f"Combat started! You face a {enemy.name}.")
    
    def end_combat(self):
        """End the current combat"""
        if self.enemy:
            self.enemy.is_in_combat = False
        
        self.is_active = False
        self.player = None
        self.enemy = None
        self.log.clear()
    
    def add_to_log(self, message: str):
        """Add a message to the combat log"""
        self.log.append(message)
        # Keep only last 10 messages
        if len(self.log) > 10:
            self.log.pop(0)
    
    def player_attack(self) -> Dict[str, Any]:
        """Player attacks the enemy"""
        if not self.is_active or not self.player_turn:
            return {'success': False, 'message': 'Not your turn!'}
        
        # Player attacks
        attack_result = self.player.attack(self.enemy)
        
        if attack_result['hit']:
            damage = self.enemy.take_damage(attack_result['damage'])
            
            if attack_result['critical']:
                self.add_to_log(f"Critical hit! You deal {damage} damage to {self.enemy.name}!")
            else:
                self.add_to_log(f"You hit {self.enemy.name} for {damage} damage!")
            
            # Check if enemy is defeated
            if not self.enemy.is_alive:
                self.add_to_log(f"You defeated {self.enemy.name}!")
                return {'success': True, 'result': 'victory'}
        else:
            self.add_to_log(f"You miss {self.enemy.name}!")
        
        # Enemy's turn
        self.player_turn = False
        return {'success': True, 'result': 'continue'}
    
    def enemy_attack(self) -> Dict[str, Any]:
        """Enemy attacks the player"""
        if not self.is_active or self.player_turn:
            return {'success': False, 'message': 'Not enemy turn!'}
        
        # Enemy attacks
        attack_result = self.enemy.attack(self.player)
        
        if attack_result['hit']:
            damage = self.player.take_damage(attack_result['damage'])
            
            if attack_result['critical']:
                self.add_to_log(f"{self.enemy.name} critically hits you for {damage} damage!")
            else:
                self.add_to_log(f"{self.enemy.name} hits you for {damage} damage!")
            
            # Check if player is defeated
            if not self.player.is_alive:
                self.add_to_log("You have been defeated!")
                return {'success': True, 'result': 'defeat'}
        else:
            self.add_to_log(f"{self.enemy.name} misses you!")
        
        # Player's turn
        self.player_turn = True
        self.round += 1
        return {'success': True, 'result': 'continue'}
    
    def player_use_item(self, item_index: int) -> Dict[str, Any]:
        """Player uses an item from inventory"""
        if not self.is_active or not self.player_turn:
            return {'success': False, 'message': 'Not your turn!'}
        
        # Get item from inventory
        if item_index < 0 or item_index >= len(self.player.inventory.items):
            return {'success': False, 'message': 'Invalid item index!'}
        
        item = self.player.inventory.get_item_at(item_index)
        if not item:
            return {'success': False, 'message': 'No item at that slot!'}
        
        # Try to use the item
        try:
            success = item.use(self.player)
            if success:
                # Remove item if it's consumable
                if hasattr(item, 'consumable') and item.consumable:
                    self.player.inventory.remove_item_at(item_index)
                
                self.add_to_log(f"You used {item.name}.")
                
                # Enemy's turn
                self.player_turn = False
                return {'success': True, 'result': 'continue'}
            else:
                return {'success': False, 'message': "You can't use that item now!"}
        except Exception as e:
            return {'success': False, 'message': f'Error using item: {e}'}
    
    def player_flee(self) -> Dict[str, Any]:
        """Player attempts to flee from combat"""
        if not self.is_active or not self.player_turn:
            return {'success': False, 'message': 'Not your turn!'}
        
        # Flee chance based on dexterity and enemy level
        flee_chance = 0.6 + (self.player.dexterity * 0.02) - (self.enemy.level * 0.05)
        flee_chance = max(0.2, min(0.9, flee_chance))  # Clamp between 20% and 90%
        
        if Dice.roll(100) <= flee_chance * 100:
            self.add_to_log("You successfully fled from combat!")
            return {'success': True, 'result': 'flee'}
        else:
            self.add_to_log("You failed to flee!")
            self.player_turn = False  # Enemy gets to attack
            return {'success': True, 'result': 'continue'}
    
    def update(self) -> Optional[str]:
        """Update combat state"""
        if not self.is_active:
            return None
        
        # Check if combat should end
        if not self.enemy.is_alive:
            result = 'player_won'
            self.end_combat()
            return result
        
        if not self.player.is_alive:
            result = 'enemy_won'
            self.end_combat()
            return result
        
        # If it's enemy's turn, let them attack
        if not self.player_turn:
            result = self.enemy_attack()
            if result['result'] in ['victory', 'defeat']:
                self.end_combat()
                return 'player_won' if result['result'] == 'victory' else 'enemy_won'
            elif result['result'] == 'flee':
                self.end_combat()
                return 'escaped'
        
        return None  # Combat continues
    
    def get_combat_status(self) -> Dict[str, Any]:
        """Get current combat status"""
        if not self.is_active:
            return {'active': False}
        
        return {
            'active': True,
            'round': self.round,
            'player_turn': self.player_turn,
            'player_hp': f"{self.player.current_hp}/{self.player.max_hp}",
            'enemy_hp': f"{self.enemy.current_hp}/{self.enemy.max_hp}",
            'enemy_name': self.enemy.name,
            'log': self.log.copy()
        }
    
    def get_combat_options(self) -> List[str]:
        """Get available combat options for the player"""
        options = ['Attack', 'Flee']
        
        # Add item usage if player has usable items
        if self.player.inventory.get_non_none_items():
            options.append('Use Item')
        
        return options