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
from inventory import Inventory
from utils import Vector2, Dice


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
        self.camera = Vector2(0, 0)

        # Input handling
        self.keys_pressed = set()
        self.last_input_time = 0
        self.input_delay = 120  # milliseconds between moves

        # Real-time combat and movement tuning
        self.player_speed = 6.0  # tiles per second
        self.attack_cooldown = 400  # milliseconds between player attacks
        self.last_attack_time = 0
        self.enemy_move_delay = 300  # milliseconds between enemy steps
        self.enemy_attack_delay = 800  # milliseconds between enemy attacks
        self.last_enemy_update = 0

        # Delta time tracking
        self.last_frame_time = pygame.time.get_ticks()
        self.dt = 0

        # Initialize font
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Movement animation state
        self.is_moving = False
        self.movement_cooldown = 0

        # Start the game
        self.start_new_game()

    def start_new_game(self):
        """Initialize a new game"""
        # Create player
        self.player = Player("Hero", Vector2(5, 5))

        # Create dungeon
        self.dungeon = Dungeon(Config.MAP_WIDTH, Config.MAP_HEIGHT)

        # Place player in the first room (not on stairs)
        if self.dungeon.rooms:
            first_room = self.dungeon.rooms[0]
            # Find a safe spawn position in the room
            spawn_x = max(first_room.left + 1, min(int(first_room.center.x), first_room.right - 1))
            spawn_y = max(first_room.top + 1, min(int(first_room.center.y), first_room.bottom - 1))

            # Ensure not spawning on stairs
            attempts = 0
            while self.dungeon.is_stairs(spawn_x, spawn_y) and attempts < 20:
                spawn_x = Dice.roll_range(first_room.left + 1, first_room.right - 1)
                spawn_y = Dice.roll_range(first_room.top + 1, first_room.bottom - 1)
                attempts += 1

            self.player.position = Vector2(spawn_x, spawn_y)

        # Initialize other systems
        self.ui = UI(self.screen, self.player, self.dungeon)

        # Update visibility around player
        self.dungeon.update_visibility(self.player.position)

        # Set initial camera position
        self.ui.update_camera(self.player.position.x, self.player.position.y)
        self.ui.camera_x = self.ui.target_camera_x
        self.ui.camera_y = self.ui.target_camera_y

        # Add welcome message
        self.ui.add_message(f"Welcome to Dungeon Level {self.dungeon.current_level}!", Config.YELLOW)
        self.ui.add_message("Move freely with WASD/ARROWS, press SPACE or click to attack nearby foes.", Config.UI_TEXT)

        # Set game state to menu (or playing if you want to skip menu)
        self.state = GameState.MENU

    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            self.dt = (current_time - self.last_frame_time) / 1000.0
            self.last_frame_time = current_time

            # Handle events
            self.handle_events()

            # Update game state
            self.update()

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
                elif self.state == GameState.PAUSED:
                    self.handle_pause_input(event)

            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_mouse_click(event.pos)

        # Continuous movement handled in update loop

    def handle_menu_input(self, event):
        """Handle input in menu state"""
        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self.state = GameState.PLAYING
            self.ui.add_message("Your adventure begins!", Config.GREEN)
        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def handle_game_input(self, event):
        """Handle input during gameplay"""
        if event.key == pygame.K_i:
            self.state = GameState.INVENTORY
            self.ui.set_inventory_active(True)
        elif event.key == pygame.K_ESCAPE:
            self.state = GameState.PAUSED
        elif event.key == pygame.K_SPACE or event.key == pygame.K_PERIOD:
            # Melee attack
            self.perform_player_attack()
        elif event.key == pygame.K_GREATER or (event.key == pygame.K_PERIOD and pygame.K_LSHIFT in self.keys_pressed):
            # Descend stairs
            self.try_use_stairs(down=True)
        elif event.key == pygame.K_LESS or (event.key == pygame.K_COMMA and pygame.K_LSHIFT in self.keys_pressed):
            # Ascend stairs
            self.try_use_stairs(down=False)

    def handle_inventory_input(self, event):
        """Handle input in inventory state"""
        if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
            self.state = GameState.PLAYING
            self.ui.set_inventory_active(False)
        elif event.key == pygame.K_e:
            # Equip selected item
            self.try_equip_selected_item()
        elif event.key == pygame.K_u:
            # Use selected item
            self.try_use_selected_item()
        elif event.key == pygame.K_d:
            # Drop selected item
            self.try_drop_selected_item()

    def handle_combat_input(self, event):
        """Handle input during combat"""
        # Legacy stub - combat is handled in real time now
        return

    def handle_game_over_input(self, event):
        """Handle input in game over state"""
        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self.start_new_game()
            self.state = GameState.PLAYING
        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def handle_pause_input(self, event):
        """Handle input in pause state"""
        if event.key == pygame.K_ESCAPE:
            self.state = GameState.PLAYING

    def handle_mouse_click(self, pos):
        """Handle mouse clicks"""
        if self.state == GameState.INVENTORY:
            clicked_slot = self.ui.handle_inventory_click(pos)
            if clicked_slot is not None:
                # Item was selected
                pass
        elif self.state == GameState.PLAYING:
            self.perform_player_attack()

    def handle_continuous_movement(self):
        """Handle smooth movement when keys are held down"""
        direction = None

        if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
            if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
                direction = Config.DIRECTIONS['UP_LEFT']
            elif pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
                direction = Config.DIRECTIONS['UP_RIGHT']
            else:
                direction = Config.DIRECTIONS['UP']
        elif pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed:
            if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
                direction = Config.DIRECTIONS['DOWN_LEFT']
            elif pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
                direction = Config.DIRECTIONS['DOWN_RIGHT']
            else:
                direction = Config.DIRECTIONS['DOWN']
        elif pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
            direction = Config.DIRECTIONS['LEFT']
        elif pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
            direction = Config.DIRECTIONS['RIGHT']

        if direction:
            move_step = Vector2(direction[0], direction[1]).normalized * (self.player_speed * self.dt)
            new_pos = Vector2(self.player.position.x + move_step.x, self.player.position.y + move_step.y)

            # Prevent moving through walls by checking intended tile
            if self.dungeon.is_walkable(int(new_pos.x), int(new_pos.y)):
                self.player.position = new_pos
                self.ui.update_camera(self.player.position.x, self.player.position.y)
                self.dungeon.update_visibility(self.player.position)

            self.last_input_time = pygame.time.get_ticks()

    def move_player(self, direction):
        """Move the player in the given direction"""
        old_pos = self.player.position.copy()
        new_x = int(self.player.position.x + direction[0])
        new_y = int(self.player.position.y + direction[1])

        # Check if the move is valid
        if self.dungeon.is_walkable(new_x, new_y):
            # Check for enemies at the destination
            enemy = self.dungeon.get_enemy_at(new_x, new_y)
            if enemy:
                # Attack instead of switching to a combat state
                self.perform_player_attack(enemy)
                return

            # Move the player with animation
            new_pos = Vector2(new_x, new_y)
            self.ui.start_player_move_animation(old_pos, new_pos)
            self.player.position = new_pos

            # Update camera
            self.ui.update_camera(self.player.position.x, self.player.position.y)

            # Update visibility
            self.dungeon.update_visibility(self.player.position)

            # Check for items
            item = self.dungeon.get_item_at(new_x, new_y)
            if item:
                if self.player.inventory.add_item(item):
                    self.dungeon.remove_item(new_x, new_y)
                    self.ui.add_message(f"Picked up {item.name}", Config.YELLOW)
                else:
                    self.ui.add_message("Inventory full!", Config.RED)

            # Check for stairs
            if self.dungeon.is_stairs(new_x, new_y):
                self.ui.add_message("You see stairs here. Press > to descend or < to ascend.", Config.UI_HIGHLIGHT)
        else:
            # Can't move there
            pass

    def try_use_stairs(self, down=True):
        """Try to use stairs"""
        x, y = int(self.player.position.x), int(self.player.position.y)

        if not self.dungeon.is_stairs(x, y):
            self.ui.add_message("There are no stairs here.", Config.GRAY)
            return

        if down:
            # Descend
            self.ui.add_message(f"Descending to level {self.dungeon.current_level + 1}...", Config.UI_HIGHLIGHT)
            self.dungeon.generate_next_level()

            # Place player in first room
            if self.dungeon.rooms:
                first_room = self.dungeon.rooms[0]
                spawn_x = max(first_room.left + 1, min(int(first_room.center.x), first_room.right - 1))
                spawn_y = max(first_room.top + 1, min(int(first_room.center.y), first_room.bottom - 1))
                self.player.position = Vector2(spawn_x, spawn_y)

            self.ui.add_message(f"Welcome to Dungeon Level {self.dungeon.current_level}!", Config.YELLOW)
        else:
            # Ascend
            if self.dungeon.current_level <= 1:
                self.ui.add_message("You cannot ascend from level 1.", Config.GRAY)
                return

            self.ui.add_message(f"Ascending to level {self.dungeon.current_level - 1}...", Config.UI_HIGHLIGHT)
            self.dungeon.current_level -= 1
            self.dungeon.generate()

            # Place player near stairs
            if self.dungeon.rooms:
                last_room = self.dungeon.rooms[-1]
                spawn_x = max(last_room.left + 1, min(int(last_room.center.x), last_room.right - 1))
                spawn_y = max(last_room.top + 1, min(int(last_room.center.y), last_room.bottom - 1))
                self.player.position = Vector2(spawn_x, spawn_y)

            self.ui.add_message(f"Back on Dungeon Level {self.dungeon.current_level}.", Config.YELLOW)

        # Update camera and visibility
        self.ui.update_camera(self.player.position.x, self.player.position.y)
        self.ui.camera_x = self.ui.target_camera_x
        self.ui.camera_y = self.ui.target_camera_y
        self.dungeon.update_visibility(self.player.position)

    def try_equip_selected_item(self):
        """Try to equip the selected inventory item"""
        slot = self.ui.selected_inventory_slot
        if 0 <= slot < len(self.player.inventory.items):
            item = self.player.inventory.items[slot]
            if item and hasattr(item, 'damage_range'):  # It's a weapon
                self.player.equip_weapon(item)
                self.ui.add_message(f"Equipped {item.name}", Config.GREEN)

    def try_use_selected_item(self):
        """Try to use the selected inventory item"""
        slot = self.ui.selected_inventory_slot
        if 0 <= slot < len(self.player.inventory.items):
            item = self.player.inventory.items[slot]
            if item:
                # Try to use the item
                if hasattr(item, 'use'):
                    result = item.use(self.player)
                    if result:
                        self.player.inventory.remove_item(item)
                        self.ui.add_message(f"Used {item.name}", Config.GREEN)
                elif hasattr(item, 'healing'):
                    heal_amount = self.player.heal(item.healing)
                    if heal_amount > 0:
                        self.player.inventory.remove_item(item)
                        self.ui.add_message(f"Healed for {heal_amount} HP!", Config.GREEN)
                    else:
                        self.ui.add_message("Already at full health.", Config.GRAY)

    def try_drop_selected_item(self):
        """Try to drop the selected inventory item"""
        slot = self.ui.selected_inventory_slot
        if 0 <= slot < len(self.player.inventory.items):
            item = self.player.inventory.items[slot]
            if item:
                self.player.inventory.remove_item(item)
                # Add item to dungeon at player's position
                self.dungeon.items.append((self.player.position.copy(), item))
                self.ui.add_message(f"Dropped {item.name}", Config.GRAY)

    def perform_player_attack(self, target=None):
        """Perform a free-form melee attack against nearby enemies"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return

        self.last_attack_time = current_time

        if target is None:
            # Find closest enemy in melee range
            enemies_in_range = [
                enemy for enemy in self.dungeon.enemies
                if enemy.is_alive and enemy.distance_to(self.player.position) <= 1.5
            ]
            target = enemies_in_range[0] if enemies_in_range else None

        if not target:
            self.ui.add_message("You swing at nothing.", Config.GRAY)
            return

        result = self.player.attack(target)
        if result['hit']:
            damage = target.take_damage(result['damage'])
            hit_text = f"You hit {target.name} for {damage} damage!"
            if result['critical']:
                hit_text = f"CRITICAL! {hit_text}"
            self.ui.add_message(hit_text, Config.GREEN)
            if not target.is_alive:
                self.finish_enemy_defeat(target)
        else:
            self.ui.add_message("Your attack misses!", Config.GRAY)

    def finish_enemy_defeat(self, enemy):
        """Handle rewards and cleanup after an enemy falls"""
        xp_gained = enemy.xp_reward
        self.player.gain_experience(xp_gained)
        self.player.total_kills += 1

        self.ui.add_message(f"Defeated {enemy.name}! Gained {xp_gained} XP.", Config.YELLOW)

        # Remove enemy from dungeon
        self.dungeon.remove_enemy(enemy)

        # Drop loot
        gold_drop = Dice.roll_range(enemy.gold_reward[0], enemy.gold_reward[1])
        self.player.inventory.gold += gold_drop
        self.ui.add_message(f"Found {gold_drop} gold!", Config.YELLOW)

    def process_enemy_attack(self, enemy):
        """Enemies strike the player in real time when close enough"""
        attack_result = enemy.attack(self.player)
        if attack_result['hit']:
            damage = self.player.take_damage(attack_result['damage'])
            msg = f"{enemy.name} hits you for {damage} damage!"
            if attack_result.get('critical'):
                msg = f"CRITICAL! {msg}"
            self.ui.add_message(msg, Config.RED)
        else:
            self.ui.add_message(f"{enemy.name} misses you!", Config.GRAY)

        if not self.player.is_alive():
            self.state = GameState.GAME_OVER
            self.ui.add_message("You have been defeated!", Config.RED)

    def update_enemies(self):
        """Update enemy positions and AI with real-time behavior"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_enemy_update < self.enemy_move_delay:
            return

        self.last_enemy_update = current_time

        for enemy in list(self.dungeon.enemies):
            if not enemy.is_alive:
                continue

            # Update AI state
            enemy.update_ai(self.player.position, self.dungeon)

            # Enemy attack check
            if enemy.distance_to(self.player.position) <= 1.5:
                last_attack = getattr(enemy, "last_attack_time", 0)
                cooldown = getattr(enemy, "attack_cooldown", self.enemy_attack_delay)
                if current_time - last_attack >= cooldown:
                    self.process_enemy_attack(enemy)
                    enemy.last_attack_time = current_time

    def update(self):
        """Update game state"""
        # Update UI animations
        self.ui.update(self.dt)

        if self.state == GameState.PLAYING:
            self.handle_continuous_movement()
            self.update_enemies()
        elif self.state == GameState.COMBAT:
            # Combat updates handled by combat system
            pass

    def render(self):
        """Render everything to the screen"""
        # Clear screen
        self.screen.fill(Config.BLACK)

        if self.state == GameState.MENU:
            self.ui.render_menu()
        elif self.state == GameState.PLAYING:
            self.render_game()
        elif self.state == GameState.INVENTORY:
            self.render_game()  # Render game in background
            self.ui.render_inventory()
        elif self.state == GameState.COMBAT:
            self.render_game()  # Render game in background
            self.ui.render_combat(self.combat_system)
        elif self.state == GameState.GAME_OVER:
            self.render_game()  # Render game in background
            self.ui.render_game_over()
        elif self.state == GameState.PAUSED:
            self.render_game()  # Render game in background
            self.ui.render_pause()

        # Update display
        pygame.display.flip()

    def render_game(self):
        """Render the main game view"""
        # Render dungeon with sprites
        self.ui.render_dungeon()

        # Render UI panels
        self.ui.render_player_stats()
        self.ui.render_minimap()
        self.ui.render_equipment_panel()
        self.ui.render_message_log()
