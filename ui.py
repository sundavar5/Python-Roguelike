"""
User interface system for rendering game elements
"""

import pygame
from typing import Optional, List, Tuple
from config import Config
from utils import Vector2, TextUtils

class UI:
    """User interface class for rendering game elements"""
    
    def __init__(self, screen, player, dungeon):
        """Initialize UI"""
        self.screen = screen
        self.player = player
        self.dungeon = dungeon
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.tiny_font = pygame.font.Font(None, 14)
        
        # UI dimensions
        self.viewport_width = Config.VIEWPORT_WIDTH
        self.viewport_height = Config.VIEWPORT_HEIGHT
        self.tile_size = Config.TILE_SIZE
        
        # Panel positions
        self.map_panel_x = 10
        self.map_panel_y = 10
        self.map_panel_width = self.viewport_width * self.tile_size
        self.map_panel_height = self.viewport_height * self.tile_size
        
        # Stats panel
        self.stats_panel_x = self.map_panel_x + self.map_panel_width + 10
        self.stats_panel_y = 10
        self.stats_panel_width = 250
        self.stats_panel_height = 200
        
        # Minimap panel
        self.minimap_panel_x = self.stats_panel_x
        self.minimap_panel_y = self.stats_panel_y + self.stats_panel_height + 10
        self.minimap_panel_width = 250
        self.minimap_panel_height = 150
        
        # Message log panel
        self.message_panel_x = self.map_panel_x
        self.message_panel_y = self.map_panel_y + self.map_panel_height + 10
        self.message_panel_width = self.map_panel_width
        self.message_panel_height = 100
        
        # Inventory panel (when active)
        self.inventory_active = False
        self.inventory_panel_x = 50
        self.inventory_panel_y = 50
        self.inventory_panel_width = Config.SCREEN_WIDTH - 100
        self.inventory_panel_height = Config.SCREEN_HEIGHT - 100
        
        # Message log
        self.messages: List[Tuple[str, tuple]] = []
        self.max_messages = 5
    
    def add_message(self, message: str, color: tuple = Config.WHITE):
        """Add a message to the message log"""
        self.messages.append((message, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def render_dungeon(self):
        """Render the dungeon view"""
        # Draw map panel background
        pygame.draw.rect(self.screen, Config.UI_BG, 
                        (self.map_panel_x - 2, self.map_panel_y - 2, 
                         self.map_panel_width + 4, self.map_panel_height + 4))
        pygame.draw.rect(self.screen, Config.UI_BORDER, 
                        (self.map_panel_x - 2, self.map_panel_y - 2, 
                         self.map_panel_width + 4, self.map_panel_height + 4), 2)
        
        # Calculate camera offset
        camera_x = max(0, min(self.player.position.x - self.viewport_width // 2, 
                             self.dungeon.width - self.viewport_width))
        camera_y = max(0, min(self.player.position.y - self.viewport_height // 2, 
                             self.dungeon.height - self.viewport_height))
        
        # Render visible tiles
        for viewport_x in range(self.viewport_width):
            for viewport_y in range(self.viewport_height):
                map_x = camera_x + viewport_x
                map_y = camera_y + viewport_y
                
                if 0 <= map_x < self.dungeon.width and 0 <= map_y < self.dungeon.height:
                    tile = self.dungeon.tiles[map_x][map_y]
                    
                    # Only render explored tiles
                    if tile.explored:
                        # Determine color based on visibility
                        if tile.visible:
                            color = self.dungeon.get_color_at(map_x, map_y)
                            char = self.dungeon.get_char_at(map_x, map_y)
                        else:
                            # Darker color for unexplored areas
                            color = tuple(c // 2 for c in self.dungeon.get_color_at(map_x, map_y))
                            char = self.dungeon.get_char_at(map_x, map_y)
                        
                        # Draw tile
                        pixel_x = self.map_panel_x + viewport_x * self.tile_size
                        pixel_y = self.map_panel_y + viewport_y * self.tile_size
                        
                        # Draw tile background
                        if tile.type == 'floor':
                            pygame.draw.rect(self.screen, color, 
                                           (pixel_x, pixel_y, self.tile_size, self.tile_size))
                        elif tile.type == 'wall':
                            pygame.draw.rect(self.screen, color, 
                                           (pixel_x, pixel_y, self.tile_size, self.tile_size))
                        
                        # Draw character
                        if char != '.':  # Don't draw floor dots
                            text = self.small_font.render(char, True, color)
                            text_rect = text.get_rect(center=(
                                pixel_x + self.tile_size // 2,
                                pixel_y + self.tile_size // 2
                            ))
                            self.screen.blit(text, text_rect)
        
        # Draw player
        player_viewport_x = self.player.position.x - camera_x
        player_viewport_y = self.player.position.y - camera_y
        
        if 0 <= player_viewport_x < self.viewport_width and 0 <= player_viewport_y < self.viewport_height:
            pixel_x = self.map_panel_x + player_viewport_x * self.tile_size
            pixel_y = self.map_panel_y + player_viewport_y * self.tile_size
            
            # Player character
            text = self.small_font.render('@', True, Config.PLAYER_COLOR)
            text_rect = text.get_rect(center=(
                pixel_x + self.tile_size // 2,
                pixel_y + self.tile_size // 2
            ))
            self.screen.blit(text, text_rect)
    
    def render_player_stats(self):
        """Render player statistics panel"""
        # Draw panel background
        pygame.draw.rect(self.screen, Config.UI_BG, 
                        (self.stats_panel_x, self.stats_panel_y, 
                         self.stats_panel_width, self.stats_panel_height))
        pygame.draw.rect(self.screen, Config.UI_BORDER, 
                        (self.stats_panel_x, self.stats_panel_y, 
                         self.stats_panel_width, self.stats_panel_height), 2)
        
        # Player info
        y_offset = self.stats_panel_y + 10
        
        # Name and level
        name_text = self.font.render(f"{self.player.name} (Level {self.player.level})", 
                                   True, Config.UI_TEXT)
        self.screen.blit(name_text, (self.stats_panel_x + 10, y_offset))
        y_offset += 25
        
        # Health bar
        hp_ratio = self.player.get_health_percentage()
        hp_text = self.small_font.render(f"HP: {self.player.current_hp}/{self.player.max_hp}", 
                                        True, Config.UI_TEXT)
        self.screen.blit(hp_text, (self.stats_panel_x + 10, y_offset))
        y_offset += 20
        
        # Health bar background
        pygame.draw.rect(self.screen, Config.DARK_GRAY, 
                        (self.stats_panel_x + 10, y_offset, 100, 10))
        # Health bar fill
        hp_color = Config.GREEN if hp_ratio > 0.5 else Config.YELLOW if hp_ratio > 0.25 else Config.RED
        pygame.draw.rect(self.screen, hp_color, 
                        (self.stats_panel_x + 10, y_offset, int(100 * hp_ratio), 10))
        y_offset += 15
        
        # Mana bar (if player has mana)
        if self.player.max_mp > 0:
            mp_ratio = self.player.get_mana_percentage()
            mp_text = self.small_font.render(f"MP: {self.player.current_mp}/{self.player.max_mp}", 
                                            True, Config.UI_TEXT)
            self.screen.blit(mp_text, (self.stats_panel_x + 10, y_offset))
            y_offset += 20
            
            # Mana bar background
            pygame.draw.rect(self.screen, Config.DARK_GRAY, 
                            (self.stats_panel_x + 10, y_offset, 100, 10))
            # Mana bar fill
            pygame.draw.rect(self.screen, Config.BLUE, 
                            (self.stats_panel_x + 10, y_offset, int(100 * mp_ratio), 10))
            y_offset += 15
        
        # Experience bar
        exp_ratio = self.player.get_experience_percentage()
        exp_text = self.small_font.render(f"XP: {self.player.experience}/{self.player.experience_to_next}", 
                                         True, Config.UI_TEXT)
        self.screen.blit(exp_text, (self.stats_panel_x + 10, y_offset))
        y_offset += 20
        
        # Experience bar background
        pygame.draw.rect(self.screen, Config.DARK_GRAY, 
                        (self.stats_panel_x + 10, y_offset, 100, 10))
        # Experience bar fill
        pygame.draw.rect(self.screen, Config.PURPLE, 
                        (self.stats_panel_x + 10, y_offset, int(100 * exp_ratio), 10))
        y_offset += 20
        
        # Attributes
        y_offset += 10
        attr_text = self.small_font.render("Attributes:", True, Config.UI_TEXT)
        self.screen.blit(attr_text, (self.stats_panel_x + 10, y_offset))
        y_offset += 20
        
        attributes = [
            f"STR: {self.player.strength}",
            f"DEX: {self.player.dexterity}",
            f"INT: {self.player.intelligence}",
            f"DEF: {self.player.total_defense}"
        ]
        
        for attr in attributes:
            attr_surface = self.small_font.render(attr, True, Config.UI_TEXT)
            self.screen.blit(attr_surface, (self.stats_panel_x + 10, y_offset))
            y_offset += 18
        
        # Equipment
        y_offset += 10
        equip_text = self.small_font.render("Equipment:", True, Config.UI_TEXT)
        self.screen.blit(equip_text, (self.stats_panel_x + 10, y_offset))
        y_offset += 20
        
        weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "None"
        weapon_text = self.small_font.render(f"Weapon: {weapon_name}", True, Config.UI_TEXT)
        self.screen.blit(weapon_text, (self.stats_panel_x + 10, y_offset))
        y_offset += 18
        
        damage_text = self.small_font.render(f"Damage: {self.player.damage[0]}-{self.player.damage[1]}", 
                                           True, Config.UI_TEXT)
        self.screen.blit(damage_text, (self.stats_panel_x + 10, y_offset))
        y_offset += 18
        
        crit_text = self.small_font.render(f"Crit: {self.player.total_critical_chance:.1%}", 
                                          True, Config.UI_TEXT)
        self.screen.blit(crit_text, (self.stats_panel_x + 10, y_offset))
    
    def render_minimap(self):
        """Render minimap panel"""
        # Draw panel background
        pygame.draw.rect(self.screen, Config.UI_BG, 
                        (self.minimap_panel_x, self.minimap_panel_y, 
                         self.minimap_panel_width, self.minimap_panel_height))
        pygame.draw.rect(self.screen, Config.UI_BORDER, 
                        (self.minimap_panel_x, self.minimap_panel_y, 
                         self.minimap_panel_width, self.minimap_panel_height), 2)
        
        # Title
        title_text = self.small_font.render("Minimap", True, Config.UI_TEXT)
        self.screen.blit(title_text, (self.minimap_panel_x + 10, self.minimap_panel_y + 5))
        
        # Calculate scale for minimap
        scale_x = (self.minimap_panel_width - 20) / self.dungeon.width
        scale_y = (self.minimap_panel_height - 30) / self.dungeon.height
        scale = min(scale_x, scale_y)
        
        offset_x = self.minimap_panel_x + 10 + (self.minimap_panel_width - 20 - self.dungeon.width * scale) // 2
        offset_y = self.minimap_panel_y + 25 + (self.minimap_panel_height - 30 - self.dungeon.height * scale) // 2
        
        # Draw explored tiles
        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                tile = self.dungeon.tiles[x][y]
                if tile.explored:
                    pixel_x = offset_x + x * scale
                    pixel_y = offset_y + y * scale
                    
                    if tile.type == 'wall':
                        color = Config.WALL_COLOR
                    elif tile.type == 'floor':
                        color = Config.FLOOR_COLOR
                    elif tile.type == 'stairs':
                        color = Config.STAIRS_COLOR
                    else:
                        color = Config.FLOOR_COLOR
                    
                    # Make unexplored areas darker
                    if not tile.visible:
                        color = tuple(c // 2 for c in color)
                    
                    pygame.draw.rect(self.screen, color, 
                                   (pixel_x, pixel_y, max(1, scale), max(1, scale)))
        
        # Draw player position
        player_x = offset_x + self.player.position.x * scale
        player_y = offset_y + self.player.position.y * scale
        pygame.draw.rect(self.screen, Config.PLAYER_COLOR, 
                        (player_x, player_y, max(2, scale), max(2, scale)))
        
        # Draw level info
        level_text = self.small_font.render(f"Level: {self.dungeon.current_level}", 
                                           True, Config.UI_TEXT)
        self.screen.blit(level_text, (self.minimap_panel_x + 10, 
                                     self.minimap_panel_y + self.minimap_panel_height - 20))
    
    def render_message_log(self):
        """Render message log panel"""
        # Draw panel background
        pygame.draw.rect(self.screen, Config.UI_BG, 
                        (self.message_panel_x, self.message_panel_y, 
                         self.message_panel_width, self.message_panel_height))
        pygame.draw.rect(self.screen, Config.UI_BORDER, 
                        (self.message_panel_x, self.message_panel_y, 
                         self.message_panel_width, self.message_panel_height), 2)
        
        # Render messages
        y_offset = self.message_panel_y + 5
        for message, color in self.messages[-5:]:  # Show last 5 messages
            message_surface = self.small_font.render(message, True, color)
            self.screen.blit(message_surface, (self.message_panel_x + 10, y_offset))
            y_offset += 18
    
    def render_inventory(self):
        """Render inventory screen"""
        # Draw background overlay
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw inventory panel
        pygame.draw.rect(self.screen, Config.UI_BG, 
                        (self.inventory_panel_x, self.inventory_panel_y, 
                         self.inventory_panel_width, self.inventory_panel_height))
        pygame.draw.rect(self.screen, Config.UI_BORDER, 
                        (self.inventory_panel_x, self.inventory_panel_y, 
                         self.inventory_panel_width, self.inventory_panel_height), 2)
        
        # Title
        title_text = self.font.render("Inventory", True, Config.UI_TEXT)
        title_rect = title_text.get_rect(center=(
            self.inventory_panel_x + self.inventory_panel_width // 2,
            self.inventory_panel_y + 20
        ))
        self.screen.blit(title_text, title_rect)
        
        # Gold
        gold_text = self.small_font.render(f"Gold: {self.player.inventory.gold}", 
                                          True, Config.UI_TEXT)
        self.screen.blit(gold_text, (self.inventory_panel_x + 20, self.inventory_panel_y + 50))
        
        # Items grid
        slots_per_row = 10
        slot_size = 60
        start_x = self.inventory_panel_x + 20
        start_y = self.inventory_panel_y + 80
        
        for i, item in enumerate(self.player.inventory.items):
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_x = start_x + col * slot_size
            slot_y = start_y + row * slot_size
            
            # Draw slot background
            pygame.draw.rect(self.screen, Config.DARK_GRAY, 
                           (slot_x, slot_y, slot_size - 2, slot_size - 2))
            
            if item:
                # Draw item
                item_text = self.tiny_font.render(item.name[:8], True, item.color)
                item_rect = item_text.get_rect(center=(
                    slot_x + slot_size // 2,
                    slot_y + slot_size // 2
                ))
                self.screen.blit(item_text, item_rect)
                
                # Stack quantity
                if hasattr(item, 'quantity') and item.quantity > 1:
                    qty_text = self.tiny_font.render(str(item.quantity), True, Config.WHITE)
                    self.screen.blit(qty_text, (slot_x + 2, slot_y + 2))
        
        # Instructions
        instructions = [
            "Click an item to select",
            "Press ESC or I to close",
            "Drag items to move them"
        ]
        
        y_offset = start_y + 5 * slot_size + 20
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, Config.UI_TEXT)
            self.screen.blit(inst_text, (self.inventory_panel_x + 20, y_offset))
            y_offset += 20
    
    def render_combat(self, combat_system):
        """Render combat screen"""
        # Draw background overlay
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Combat panel
        panel_width = 600
        panel_height = 400
        panel_x = (Config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (Config.SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(self.screen, Config.UI_BG, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, Config.UI_BORDER, 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title_text = self.font.render("COMBAT", True, Config.RED)
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 20))
        self.screen.blit(title_text, title_rect)
        
        # Combat status
        status = combat_system.get_combat_status()
        
        # Player info
        player_info = f"{self.player.name} - HP: {status['player_hp']}"
        player_text = self.small_font.render(player_info, True, Config.PLAYER_COLOR)
        self.screen.blit(player_text, (panel_x + 20, panel_y + 60))
        
        # Enemy info
        enemy_info = f"{status['enemy_name']} - HP: {status['enemy_hp']}"
        enemy_text = self.small_font.render(enemy_info, True, Config.ENEMY_COLOR)
        self.screen.blit(enemy_text, (panel_x + panel_width - 200, panel_y + 60))
        
        # Combat log
        log_y = panel_y + 100
        for i, message in enumerate(status['log'][-5:]):
            log_text = self.small_font.render(message, True, Config.UI_TEXT)
            self.screen.blit(log_text, (panel_x + 20, log_y + i * 20))
        
        # Action buttons (if player turn)
        if status['player_turn']:
            actions = combat_system.get_combat_options()
            button_width = 120
            button_height = 30
            button_y = panel_y + panel_height - 80
            
            for i, action in enumerate(actions):
                button_x = panel_x + 20 + i * (button_width + 10)
                
                # Draw button
                pygame.draw.rect(self.screen, Config.UI_BORDER, 
                               (button_x, button_y, button_width, button_height))
                pygame.draw.rect(self.screen, Config.UI_HIGHLIGHT, 
                               (button_x + 2, button_y + 2, button_width - 4, button_height - 4))
                
                # Button text
                action_text = self.small_font.render(action, True, Config.BLACK)
                text_rect = action_text.get_rect(center=(
                    button_x + button_width // 2,
                    button_y + button_height // 2
                ))
                self.screen.blit(action_text, text_rect)
        else:
            # Enemy turn message
            enemy_turn_text = self.small_font.render("Enemy's turn...", True, Config.UI_TEXT)
            self.screen.blit(enemy_turn_text, (panel_x + 20, panel_y + panel_height - 50))
    
    def render_game_over(self):
        """Render game over screen"""
        # Draw background overlay
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, Config.RED)
        text_rect = game_over_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Instructions
        restart_text = self.small_font.render("Press SPACE to restart or ESC to quit", 
                                            True, Config.WHITE)
        restart_rect = restart_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, restart_rect)
    
    def handle_inventory_click(self, mouse_pos: tuple) -> Optional[int]:
        """Handle inventory click and return item index if clicked"""
        if not self.inventory_active:
            return None
        
        # Calculate slot from mouse position
        slots_per_row = 10
        slot_size = 60
        start_x = self.inventory_panel_x + 20
        start_y = self.inventory_panel_y + 80
        
        # Check if click is within inventory grid
        if (start_x <= mouse_pos[0] < start_x + slots_per_row * slot_size and
            start_y <= mouse_pos[1] < start_y + 5 * slot_size):
            
            col = (mouse_pos[0] - start_x) // slot_size
            row = (mouse_pos[1] - start_y) // slot_size
            index = row * slots_per_row + col
            
            if 0 <= index < len(self.player.inventory.items):
                return index
        
        return None
    
    def set_inventory_active(self, active: bool):
        """Set inventory panel active state"""
        self.inventory_active = active