"""
Main game class that manages the game loop and state
"""

import pygame
import sys
from enum import Enum

from config import Config
from player import Player
from dungeon import Dungeon
from ui import UI
from combat import CombatSystem
from inventory import Inventory
from utils import Vector2

class GameState(Enum):
    """Game state enumeration"""
    MENU = "menu"
    PLAYING = "playing"
    INVENTORY = "inventory"
    COMBAT = "combat"
    GAME_OVER = "game_over"
    PAUSED = "paused"

class Game:
    """Main game class that manages everything"""
    
    def __init__(self, screen):
        """Initialize the game"""
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Initialize game components
        self.player = None
        self.dungeon = None
        self.ui = None
        self.combat_system = None
        self.camera = Vector2(0, 0)
        
        # Input handling
        self.keys_pressed = set()
        self.last_input_time = 0
        self.input_delay = 100  # milliseconds
        
        # Initialize font
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Start the game
        self.start_new_game()
    
    def start_new_game(self):
        """Initialize a new game"""
        # Create player
        self.player = Player("Hero", Vector2(5, 5))
        
        # Create dungeon
        self.dungeon = Dungeon(Config.MAP_WIDTH, Config.MAP_HEIGHT)
        self.dungeon.generate()
        
        # Place player in the first room (not on stairs)
        first_room = self.dungeon.rooms[0]
        # Find a safe spawn position in the room
        spawn_x = max(first_room.left + 1, min(first_room.center.x, first_room.right - 1))
        spawn_y = max(first_room.top + 1, min(first_room.center.y, first_room.bottom - 1))
        
        # Ensure not spawning on stairs
        while self.dungeon.is_stairs(spawn_x, spawn_y):
            spawn_x = Dice.roll_range(first_room.left + 1, first_room.right - 1)
            spawn_y = Dice.roll_range(first_room.top + 1, first_room.bottom - 1)
        
        self.player.position = Vector2(spawn_x, spawn_y)
        
        # Initialize other systems
        self.combat_system = CombatSystem()
        self.ui = UI(self.screen, self.player, self.dungeon)
        
        # Set game state to playing
        self.state = GameState.PLAYING
        
        print("New game started!")
        print(f"Welcome to Dungeon Level {self.dungeon.current_level}!")
        print(f"You are in a room at ({self.player.position.x}, {self.player.position.y})")
        print("Use ARROW KEYS to move, 'I' for inventory, '>' to descend stairs when on them")
        print("Press SPACE to wait a turn, ESC to pause")
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            self.handle_events()
            
            # Update game state
            if self.state == GameState.PLAYING:
                self.update()
            elif self.state == GameState.COMBAT:
                self.update_combat()
            
            # Render everything
            self.render()
            
            # Cap the frame rate
            self.clock.tick(Config.FPS)
    
    def handle_events(self):
        """Handle input events"""
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                # Handle different game states
                if self.state == GameState.MENU:
                    self.handle_menu_input(event)
                elif self.state == GameState.PLAYING:
                    self.handle_game_input(event)
                elif self.state == GameState.INVENTORY:
                    self.handle_inventory_input(event)
                elif self.state == GameState.COMBAT:
                    self.handle_combat_input(event)
                elif self.state == GameState.GAME_OVER:
                    self.handle_game_over_input(event)
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
        
        # Handle continuous movement
        if self.state == GameState.PLAYING and current_time - self.last_input_time > self.input_delay:
            self.handle_continuous_movement()
            self.last_input_time = current_time
    
    def handle_menu_input(self, event):
        """Handle input in menu state"""
        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self.state = GameState.PLAYING
        elif event.key == pygame.K_ESCAPE:
            self.running = False
    
    def handle_game_input(self, event):
        """Handle input during gameplay"""
        if event.key == pygame.K_i:
            self.state = GameState.INVENTORY
        elif event.key == pygame.K_ESCAPE:
            self.state = GameState.PAUSED
        elif event.key == pygame.K_SPACE:
            # Wait a turn - enemies get to move
            print("You wait a turn...")
            self.update_enemies()
        elif event.key == pygame.K_PERIOD:  # '.' key for wait
            print("You wait a turn...")
            self.update_enemies()
        elif event.key == pygame.K_GREATER:  # '>' key for descend
            if self.dungeon.is_stairs(self.player.position.x, self.player.position.y):
                print("Press '>' again to descend the stairs...")
        elif event.key == pygame.K_LESS:  # '<' key for ascend  
            if self.dungeon.is_stairs(self.player.position.x, self.player.position.y) and self.dungeon.current_level > 1:
                print("Press '<' again to ascend the stairs...")
    
    def handle_inventory_input(self, event):
        """Handle input in inventory state"""
        if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
            self.state = GameState.PLAYING
    
    def handle_combat_input(self, event):
        """Handle input during combat"""
        if event.key == pygame.K_SPACE:
            # End combat turn
            pass
    
    def handle_game_over_input(self, event):
        """Handle input in game over state"""
        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self.start_new_game()
        elif event.key == pygame.K_ESCAPE:
            self.running = False
    
    def handle_continuous_movement(self):
        """Handle smooth movement when keys are held down"""
        direction = None
        
        if pygame.K_UP in self.keys_pressed:
            if pygame.K_LEFT in self.keys_pressed:
                direction = Config.DIRECTIONS['UP_LEFT']
            elif pygame.K_RIGHT in self.keys_pressed:
                direction = Config.DIRECTIONS['UP_RIGHT']
            else:
                direction = Config.DIRECTIONS['UP']
        elif pygame.K_DOWN in self.keys_pressed:
            if pygame.K_LEFT in self.keys_pressed:
                direction = Config.DIRECTIONS['DOWN_LEFT']
            elif pygame.K_RIGHT in self.keys_pressed:
                direction = Config.DIRECTIONS['DOWN_RIGHT']
            else:
                direction = Config.DIRECTIONS['DOWN']
        elif pygame.K_LEFT in self.keys_pressed:
            direction = Config.DIRECTIONS['LEFT']
        elif pygame.K_RIGHT in self.keys_pressed:
            direction = Config.DIRECTIONS['RIGHT']
        
        if direction:
            self.move_player(direction)
    
    def move_player(self, direction):
        """Move the player in the given direction"""
        new_x = self.player.position.x + direction[0]
        new_y = self.player.position.y + direction[1]
        
        # Check if the move is valid
        if self.dungeon.is_walkable(new_x, new_y):
            # Check for enemies at the destination
            enemy = self.dungeon.get_enemy_at(new_x, new_y)
            if enemy:
                # Start combat
                self.start_combat(enemy)
            else:
                # Move the player
                self.player.position = Vector2(new_x, new_y)
                self.update_camera()
                
                # Check for items
                item = self.dungeon.get_item_at(new_x, new_y)
                if item:
                    self.player.inventory.add_item(item)
                    self.dungeon.remove_item(new_x, new_y)
                    print(f"Picked up {item.name}")
                
                # Move enemies (simple AI)
                self.update_enemies()
    
    def update_camera(self):
        """Update camera position to follow player"""
        self.camera.x = self.player.position.x - Config.VIEWPORT_WIDTH // 2
        self.camera.y = self.player.position.y - Config.VIEWPORT_HEIGHT // 2
        
        # Clamp camera to map bounds
        self.camera.x = max(0, min(self.camera.x, Config.MAP_WIDTH - Config.VIEWPORT_WIDTH))
        self.camera.y = max(0, min(self.camera.y, Config.MAP_HEIGHT - Config.VIEWPORT_HEIGHT))
    
    def start_combat(self, enemy):
        """Start combat with an enemy"""
        self.state = GameState.COMBAT
        self.combat_system.start_combat(self.player, enemy)
        print(f"Combat started with {enemy.name}!")
    
    def update_combat(self):
        """Update combat state"""
        result = self.combat_system.update()
        
        if result == "player_won":
            self.state = GameState.PLAYING
            # Remove the defeated enemy
            self.dungeon.remove_enemy(self.combat_system.enemy)
            # Award experience and loot
            self.player.gain_experience(self.combat_system.enemy.xp_reward)
            print(f"Defeated {self.combat_system.enemy.name}!")
        elif result == "enemy_won":
            self.state = GameState.GAME_OVER
            print("You have been defeated!")
        elif result == "escaped":
            self.state = GameState.PLAYING
            print("Escaped from combat!")
    
    def update_enemies(self):
        """Update enemy positions and AI"""
        for enemy in self.dungeon.enemies:
            if enemy.is_active and not enemy.is_in_combat:
                # Simple AI: move randomly or towards player if close
                if enemy.distance_to(self.player.position) < 5:
                    enemy.move_towards(self.player.position, self.dungeon)
                else:
                    enemy.move_randomly(self.dungeon)
    
    def update(self):
        """Update game state when playing"""
        # Check if player wants to descend stairs (press '>' key)
        if (self.dungeon.is_stairs(self.player.position.x, self.player.position.y) and 
            pygame.K_GREATER in self.keys_pressed):  # '>' key
            print("Descending to the next level...")
            self.dungeon.generate_next_level()
            # Place player at the start of the new level (not on stairs)
            self.player.position = Vector2(10, 10)
            self.update_camera()
            print(f"Welcome to dungeon level {self.dungeon.current_level}!")
            
        # Check if player wants to ascend stairs (press '<' key)
        elif (self.dungeon.is_stairs(self.player.position.x, self.player.position.y) and 
              pygame.K_LESS in self.keys_pressed and  # '<' key
              self.dungeon.current_level > 1):  # Can't go up from level 1
            print("Ascending to the previous level...")
            self.dungeon.current_level -= 1
            # Place player at the start of the previous level
            self.player.position = Vector2(10, 10)
            self.update_camera()
            print(f"Welcome to dungeon level {self.dungeon.current_level}!")
    
    def render(self):
        """Render everything to the screen"""
        # Clear screen
        self.screen.fill(Config.BLACK)
        
        if self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.PLAYING:
            self.render_game()
        elif self.state == GameState.INVENTORY:
            self.render_inventory()
        elif self.state == GameState.COMBAT:
            self.render_combat()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.state == GameState.PAUSED:
            self.render_pause()
        
        # Update display
        pygame.display.flip()
    
    def render_menu(self):
        """Render the main menu"""
        title_text = self.font.render("Dungeon Delver", True, Config.YELLOW)
        subtitle_text = self.small_font.render("Press SPACE to begin your adventure", True, Config.WHITE)
        
        title_rect = title_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
    
    def render_game(self):
        """Render the main game view"""
        # Render dungeon
        self.ui.render_dungeon()
        
        # Render UI panels
        self.ui.render_player_stats()
        self.ui.render_minimap()
        self.ui.render_message_log()
    
    def render_inventory(self):
        """Render the inventory screen"""
        self.ui.render_inventory()
    
    def render_combat(self):
        """Render combat screen"""
        self.ui.render_combat(self.combat_system)
    
    def render_game_over(self):
        """Render game over screen"""
        game_over_text = self.font.render("GAME OVER", True, Config.RED)
        restart_text = self.small_font.render("Press SPACE to try again", True, Config.WHITE)
        
        game_over_rect = game_over_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def render_pause(self):
        """Render pause screen"""
        pause_text = self.font.render("PAUSED", True, Config.YELLOW)
        resume_text = self.small_font.render("Press ESC to resume", True, Config.WHITE)
        
        pause_rect = pause_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 50))
        resume_rect = resume_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(resume_text, resume_rect)