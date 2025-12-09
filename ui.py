"""
User interface system for rendering game elements using sprites
"""

import pygame
import math
from typing import Optional, List, Tuple
from config import Config
from utils import Vector2, TextUtils
from sprites import SpriteManager, EffectManager, Animation


class UI:
    """User interface class for rendering game elements with sprites"""

    def __init__(self, screen, player, dungeon):
        """Initialize UI"""
        self.screen = screen
        self.player = player
        self.dungeon = dungeon

        # Initialize sprite manager
        self.sprite_manager = SpriteManager(Config.TILE_SIZE)
        self.effect_manager = EffectManager(self.sprite_manager)

        # Animation state
        self.animation_frame = 0
        self.frame_counter = 0

        # Player animation
        self.player_animation = Animation(Config.ANIMATION_SPEED)
        self.player_render_pos = (player.position.x, player.position.y)

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.tiny_font = pygame.font.Font(None, 14)
        self.title_font = pygame.font.Font(None, 48)

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
        self.stats_panel_height = 300

        # Minimap panel
        self.minimap_panel_x = self.stats_panel_x
        self.minimap_panel_y = self.stats_panel_y + self.stats_panel_height + 10
        self.minimap_panel_width = 250
        self.minimap_panel_height = 180

        # Equipment panel
        self.equip_panel_x = self.stats_panel_x
        self.equip_panel_y = self.minimap_panel_y + self.minimap_panel_height + 10
        self.equip_panel_width = 250
        self.equip_panel_height = 120

        # Message log panel
        self.message_panel_x = self.map_panel_x
        self.message_panel_y = self.map_panel_y + self.map_panel_height + 10
        self.message_panel_width = self.map_panel_width
        self.message_panel_height = 120

        # Inventory panel (when active)
        self.inventory_active = False
        self.inventory_panel_x = 50
        self.inventory_panel_y = 50
        self.inventory_panel_width = Config.SCREEN_WIDTH - 100
        self.inventory_panel_height = Config.SCREEN_HEIGHT - 100
        self.selected_inventory_slot = -1

        # Message log
        self.messages: List[Tuple[str, tuple]] = []
        self.max_messages = 6

        # Camera smoothing
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.target_camera_x = 0.0
        self.target_camera_y = 0.0

        # Pre-render some surfaces
        self._create_ui_surfaces()

    def _create_ui_surfaces(self):
        """Create pre-rendered UI surfaces for performance"""
        # Create a darkening overlay for fog of war
        self.fog_overlay = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self.fog_overlay.fill((0, 0, 0, 180))

        # Create a shadow/unseen overlay
        self.shadow_overlay = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self.shadow_overlay.fill((0, 0, 0, 220))

    def update(self, dt: float):
        """Update UI animations"""
        # Update animation frame
        self.frame_counter += 1
        if self.frame_counter >= Config.IDLE_ANIMATION_SPEED:
            self.frame_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 8

        # Update player movement animation
        if self.player_animation.active:
            self.player_render_pos = self.player_animation.update(dt)
        else:
            self.player_render_pos = (self.player.position.x, self.player.position.y)

        # Update effects
        self.effect_manager.update(dt)

        # Smooth camera movement
        camera_speed = 10.0 * dt
        self.camera_x += (self.target_camera_x - self.camera_x) * camera_speed
        self.camera_y += (self.target_camera_y - self.camera_y) * camera_speed

    def start_player_move_animation(self, start_pos: Vector2, end_pos: Vector2):
        """Start a player movement animation"""
        if Config.ENABLE_SMOOTH_MOVEMENT:
            self.player_animation.start(
                (start_pos.x, start_pos.y),
                (end_pos.x, end_pos.y)
            )

    def add_effect(self, effect_type: str, position: Tuple[int, int]):
        """Add a visual effect"""
        self.effect_manager.add_effect(effect_type, position)

    def add_message(self, message: str, color: tuple = Config.WHITE):
        """Add a message to the message log"""
        self.messages.append((message, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def update_camera(self, target_x: float, target_y: float):
        """Update camera target position"""
        self.target_camera_x = max(0, min(target_x - self.viewport_width / 2,
                                          self.dungeon.width - self.viewport_width))
        self.target_camera_y = max(0, min(target_y - self.viewport_height / 2,
                                          self.dungeon.height - self.viewport_height))

    def render_dungeon(self):
        """Render the dungeon view with sprites"""
        # Draw map panel background
        pygame.draw.rect(self.screen, Config.UI_BG,
                        (self.map_panel_x - 2, self.map_panel_y - 2,
                         self.map_panel_width + 4, self.map_panel_height + 4))
        pygame.draw.rect(self.screen, Config.UI_BORDER,
                        (self.map_panel_x - 2, self.map_panel_y - 2,
                         self.map_panel_width + 4, self.map_panel_height + 4), 2)

        # Use smooth camera position
        camera_x = int(self.camera_x)
        camera_y = int(self.camera_y)
        camera_offset_x = (self.camera_x - camera_x) * self.tile_size
        camera_offset_y = (self.camera_y - camera_y) * self.tile_size

        # Render tiles
        for viewport_x in range(-1, self.viewport_width + 1):
            for viewport_y in range(-1, self.viewport_height + 1):
                map_x = camera_x + viewport_x
                map_y = camera_y + viewport_y

                if 0 <= map_x < self.dungeon.width and 0 <= map_y < self.dungeon.height:
                    tile = self.dungeon.tiles[map_x][map_y]

                    pixel_x = self.map_panel_x + viewport_x * self.tile_size - int(camera_offset_x)
                    pixel_y = self.map_panel_y + viewport_y * self.tile_size - int(camera_offset_y)

                    # Clip to viewport
                    if (pixel_x < self.map_panel_x - self.tile_size or
                        pixel_x > self.map_panel_x + self.map_panel_width or
                        pixel_y < self.map_panel_y - self.tile_size or
                        pixel_y > self.map_panel_y + self.map_panel_height):
                        continue

                    # Only render explored tiles
                    if tile.explored:
                        # Get appropriate sprite
                        if tile.type == 'wall':
                            sprite = self.sprite_manager.get_sprite('wall')
                        elif tile.type == 'stairs':
                            # Determine if up or down stairs
                            if self.dungeon.stairs_down and \
                               int(self.dungeon.stairs_down.x) == map_x and \
                               int(self.dungeon.stairs_down.y) == map_y:
                                sprite = self.sprite_manager.get_sprite('stairs_down')
                            else:
                                sprite = self.sprite_manager.get_sprite('stairs_up')
                        else:
                            sprite = self.sprite_manager.get_floor_tile(map_x, map_y)

                        if sprite:
                            self.screen.blit(sprite, (pixel_x, pixel_y))

                        # Apply fog of war for non-visible tiles
                        if not tile.visible:
                            self.screen.blit(self.fog_overlay, (pixel_x, pixel_y))
                    else:
                        # Unexplored - draw black
                        pygame.draw.rect(self.screen, Config.BLACK,
                                       (pixel_x, pixel_y, self.tile_size, self.tile_size))

        # Render items
        for pos, item in self.dungeon.items:
            map_x, map_y = int(pos.x), int(pos.y)
            tile = self.dungeon.get_tile_at(map_x, map_y)

            if tile and tile.visible:
                pixel_x = self.map_panel_x + (map_x - camera_x) * self.tile_size - int(camera_offset_x)
                pixel_y = self.map_panel_y + (map_y - camera_y) * self.tile_size - int(camera_offset_y)

                # Check if in viewport
                if (self.map_panel_x <= pixel_x < self.map_panel_x + self.map_panel_width and
                    self.map_panel_y <= pixel_y < self.map_panel_y + self.map_panel_height):
                    item_sprite = self.sprite_manager.get_item_sprite(item)
                    self.screen.blit(item_sprite, (pixel_x, pixel_y))

        # Render enemies
        for enemy in self.dungeon.enemies:
            if enemy.is_alive:
                map_x, map_y = int(enemy.position.x), int(enemy.position.y)
                tile = self.dungeon.get_tile_at(map_x, map_y)

                if tile and tile.visible:
                    pixel_x = self.map_panel_x + (map_x - camera_x) * self.tile_size - int(camera_offset_x)
                    pixel_y = self.map_panel_y + (map_y - camera_y) * self.tile_size - int(camera_offset_y)

                    # Check if in viewport
                    if (self.map_panel_x <= pixel_x < self.map_panel_x + self.map_panel_width and
                        self.map_panel_y <= pixel_y < self.map_panel_y + self.map_panel_height):
                        enemy_sprite = self.sprite_manager.get_animated_sprite(
                            enemy.enemy_type, self.animation_frame)
                        if enemy_sprite:
                            self.screen.blit(enemy_sprite, (pixel_x, pixel_y))

                        # Draw health bar above enemy
                        self._draw_health_bar(pixel_x, pixel_y - 6,
                                            enemy.current_hp, enemy.max_hp,
                                            self.tile_size, 4)

        # Render player
        player_x, player_y = self.player_render_pos
        pixel_x = self.map_panel_x + (player_x - self.camera_x) * self.tile_size
        pixel_y = self.map_panel_y + (player_y - self.camera_y) * self.tile_size

        player_sprite = self.sprite_manager.get_animated_sprite('player', self.animation_frame)
        if player_sprite:
            self.screen.blit(player_sprite, (int(pixel_x), int(pixel_y)))

        # Render effects
        self.effect_manager.render(self.screen,
                                  (int(self.camera_x * self.tile_size) - self.map_panel_x,
                                   int(self.camera_y * self.tile_size) - self.map_panel_y),
                                  self.tile_size)

        # Draw viewport clipping border
        pygame.draw.rect(self.screen, Config.UI_BORDER,
                        (self.map_panel_x - 2, self.map_panel_y - 2,
                         self.map_panel_width + 4, self.map_panel_height + 4), 3)

    def _draw_health_bar(self, x: int, y: int, current: int, maximum: int,
                        width: int, height: int):
        """Draw a health bar"""
        if maximum <= 0:
            return

        ratio = current / maximum

        # Background
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, width, height))

        # Health fill
        if ratio > 0:
            if ratio > 0.6:
                color = Config.GREEN
            elif ratio > 0.3:
                color = Config.YELLOW
            else:
                color = Config.RED

            fill_width = int(width * ratio)
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))

        # Border
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, width, height), 1)

    def render_player_stats(self):
        """Render player statistics panel"""
        # Draw panel background with gradient effect
        panel_rect = (self.stats_panel_x, self.stats_panel_y,
                     self.stats_panel_width, self.stats_panel_height)
        pygame.draw.rect(self.screen, Config.UI_BG, panel_rect)
        pygame.draw.rect(self.screen, Config.UI_BORDER, panel_rect, 2)

        # Title bar
        title_rect = (self.stats_panel_x, self.stats_panel_y,
                     self.stats_panel_width, 25)
        pygame.draw.rect(self.screen, (40, 40, 60), title_rect)
        title_text = self.font.render("CHARACTER", True, Config.UI_HIGHLIGHT)
        self.screen.blit(title_text, (self.stats_panel_x + 10, self.stats_panel_y + 4))

        y_offset = self.stats_panel_y + 35

        # Name and level with icon
        name_text = self.font.render(f"{self.player.name}", True, Config.WHITE)
        self.screen.blit(name_text, (self.stats_panel_x + 10, y_offset))
        level_text = self.small_font.render(f"Level {self.player.level}", True, Config.UI_HIGHLIGHT)
        self.screen.blit(level_text, (self.stats_panel_x + 150, y_offset + 3))
        y_offset += 30

        # Health bar
        hp_label = self.small_font.render("HP", True, Config.RED)
        self.screen.blit(hp_label, (self.stats_panel_x + 10, y_offset))
        hp_text = self.small_font.render(f"{self.player.current_hp}/{self.player.max_hp}",
                                        True, Config.UI_TEXT)
        self.screen.blit(hp_text, (self.stats_panel_x + 160, y_offset))
        y_offset += 18

        # Health bar visual
        bar_width = 200
        bar_height = 12
        hp_ratio = self.player.get_health_percentage()
        pygame.draw.rect(self.screen, Config.DARK_GRAY,
                        (self.stats_panel_x + 10, y_offset, bar_width, bar_height))
        hp_color = Config.GREEN if hp_ratio > 0.5 else Config.YELLOW if hp_ratio > 0.25 else Config.RED
        pygame.draw.rect(self.screen, hp_color,
                        (self.stats_panel_x + 10, y_offset, int(bar_width * hp_ratio), bar_height))
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (self.stats_panel_x + 10, y_offset, bar_width, bar_height), 1)
        y_offset += 20

        # Mana bar
        if self.player.max_mp > 0:
            mp_label = self.small_font.render("MP", True, Config.BLUE)
            self.screen.blit(mp_label, (self.stats_panel_x + 10, y_offset))
            mp_text = self.small_font.render(f"{self.player.current_mp}/{self.player.max_mp}",
                                            True, Config.UI_TEXT)
            self.screen.blit(mp_text, (self.stats_panel_x + 160, y_offset))
            y_offset += 18

            mp_ratio = self.player.get_mana_percentage()
            pygame.draw.rect(self.screen, Config.DARK_GRAY,
                            (self.stats_panel_x + 10, y_offset, bar_width, bar_height))
            pygame.draw.rect(self.screen, (70, 130, 180),
                            (self.stats_panel_x + 10, y_offset, int(bar_width * mp_ratio), bar_height))
            pygame.draw.rect(self.screen, (100, 100, 100),
                            (self.stats_panel_x + 10, y_offset, bar_width, bar_height), 1)
            y_offset += 20

        # Experience bar
        exp_label = self.small_font.render("EXP", True, Config.PURPLE)
        self.screen.blit(exp_label, (self.stats_panel_x + 10, y_offset))
        exp_text = self.small_font.render(f"{self.player.experience}/{self.player.experience_to_next}",
                                         True, Config.UI_TEXT)
        self.screen.blit(exp_text, (self.stats_panel_x + 140, y_offset))
        y_offset += 18

        exp_ratio = self.player.get_experience_percentage()
        pygame.draw.rect(self.screen, Config.DARK_GRAY,
                        (self.stats_panel_x + 10, y_offset, bar_width, bar_height))
        pygame.draw.rect(self.screen, (180, 100, 200),
                        (self.stats_panel_x + 10, y_offset, int(bar_width * exp_ratio), bar_height))
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (self.stats_panel_x + 10, y_offset, bar_width, bar_height), 1)
        y_offset += 25

        # Separator line
        pygame.draw.line(self.screen, Config.UI_BORDER,
                        (self.stats_panel_x + 10, y_offset),
                        (self.stats_panel_x + self.stats_panel_width - 10, y_offset), 1)
        y_offset += 10

        # Attributes in a grid
        attr_label = self.small_font.render("ATTRIBUTES", True, Config.UI_HIGHLIGHT)
        self.screen.blit(attr_label, (self.stats_panel_x + 10, y_offset))
        y_offset += 22

        attributes = [
            ("STR", self.player.strength, Config.RED),
            ("DEX", self.player.dexterity, Config.GREEN),
            ("INT", self.player.intelligence, Config.BLUE),
            ("DEF", self.player.total_defense, Config.GRAY)
        ]

        col_width = 60
        for i, (name, value, color) in enumerate(attributes):
            col = i % 4
            x_pos = self.stats_panel_x + 10 + col * col_width
            # Attribute name
            attr_name = self.tiny_font.render(name, True, color)
            self.screen.blit(attr_name, (x_pos, y_offset))
            # Attribute value
            attr_val = self.small_font.render(str(value), True, Config.WHITE)
            self.screen.blit(attr_val, (x_pos, y_offset + 12))

        y_offset += 35

        # Combat stats
        combat_label = self.small_font.render("COMBAT", True, Config.UI_HIGHLIGHT)
        self.screen.blit(combat_label, (self.stats_panel_x + 10, y_offset))
        y_offset += 20

        damage_text = self.tiny_font.render(f"Damage: {self.player.damage[0]}-{self.player.damage[1]}",
                                           True, Config.UI_TEXT)
        self.screen.blit(damage_text, (self.stats_panel_x + 10, y_offset))

        crit_text = self.tiny_font.render(f"Crit: {self.player.total_critical_chance:.0%}",
                                         True, Config.UI_TEXT)
        self.screen.blit(crit_text, (self.stats_panel_x + 120, y_offset))

    def render_minimap(self):
        """Render minimap panel"""
        # Draw panel background
        panel_rect = (self.minimap_panel_x, self.minimap_panel_y,
                     self.minimap_panel_width, self.minimap_panel_height)
        pygame.draw.rect(self.screen, Config.UI_BG, panel_rect)
        pygame.draw.rect(self.screen, Config.UI_BORDER, panel_rect, 2)

        # Title bar
        title_rect = (self.minimap_panel_x, self.minimap_panel_y,
                     self.minimap_panel_width, 20)
        pygame.draw.rect(self.screen, (40, 40, 60), title_rect)
        title_text = self.small_font.render(f"DUNGEON LEVEL {self.dungeon.current_level}",
                                           True, Config.UI_HIGHLIGHT)
        self.screen.blit(title_text, (self.minimap_panel_x + 10, self.minimap_panel_y + 3))

        # Calculate scale for minimap
        map_area_width = self.minimap_panel_width - 20
        map_area_height = self.minimap_panel_height - 30
        scale_x = map_area_width / self.dungeon.width
        scale_y = map_area_height / self.dungeon.height
        scale = min(scale_x, scale_y)

        offset_x = self.minimap_panel_x + 10 + (map_area_width - self.dungeon.width * scale) / 2
        offset_y = self.minimap_panel_y + 25 + (map_area_height - self.dungeon.height * scale) / 2

        # Draw explored tiles
        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                tile = self.dungeon.tiles[x][y]
                if tile.explored:
                    pixel_x = offset_x + x * scale
                    pixel_y = offset_y + y * scale

                    if tile.type == 'wall':
                        color = (80, 80, 90)
                    elif tile.type == 'floor':
                        color = (50, 50, 55)
                    elif tile.type == 'stairs':
                        color = (100, 100, 200)
                    else:
                        color = (50, 50, 55)

                    # Make non-visible areas darker
                    if not tile.visible:
                        color = tuple(c // 2 for c in color)

                    pygame.draw.rect(self.screen, color,
                                   (pixel_x, pixel_y, max(1, scale), max(1, scale)))

        # Draw enemies on minimap
        for enemy in self.dungeon.enemies:
            if enemy.is_alive:
                tile = self.dungeon.get_tile_at(int(enemy.position.x), int(enemy.position.y))
                if tile and tile.visible:
                    enemy_x = offset_x + enemy.position.x * scale
                    enemy_y = offset_y + enemy.position.y * scale
                    pygame.draw.rect(self.screen, Config.RED,
                                   (enemy_x, enemy_y, max(2, scale), max(2, scale)))

        # Draw player position (blinking)
        if self.animation_frame % 4 < 2:  # Blink effect
            player_x = offset_x + self.player.position.x * scale
            player_y = offset_y + self.player.position.y * scale
            pygame.draw.rect(self.screen, Config.PLAYER_COLOR,
                            (player_x - 1, player_y - 1, max(3, scale + 2), max(3, scale + 2)))

        # Draw viewport rectangle
        viewport_x = offset_x + self.camera_x * scale
        viewport_y = offset_y + self.camera_y * scale
        viewport_w = self.viewport_width * scale
        viewport_h = self.viewport_height * scale
        pygame.draw.rect(self.screen, Config.WHITE,
                        (viewport_x, viewport_y, viewport_w, viewport_h), 1)

    def render_equipment_panel(self):
        """Render equipment panel"""
        panel_rect = (self.equip_panel_x, self.equip_panel_y,
                     self.equip_panel_width, self.equip_panel_height)
        pygame.draw.rect(self.screen, Config.UI_BG, panel_rect)
        pygame.draw.rect(self.screen, Config.UI_BORDER, panel_rect, 2)

        # Title
        title_rect = (self.equip_panel_x, self.equip_panel_y,
                     self.equip_panel_width, 20)
        pygame.draw.rect(self.screen, (40, 40, 60), title_rect)
        title_text = self.small_font.render("EQUIPMENT", True, Config.UI_HIGHLIGHT)
        self.screen.blit(title_text, (self.equip_panel_x + 10, self.equip_panel_y + 3))

        y_offset = self.equip_panel_y + 30

        # Weapon
        weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "None"
        weapon_label = self.tiny_font.render("Weapon:", True, Config.UI_TEXT)
        self.screen.blit(weapon_label, (self.equip_panel_x + 10, y_offset))

        # Get rarity color if weapon equipped
        if self.player.equipped_weapon:
            rarity = getattr(self.player.equipped_weapon, 'rarity', 'common')
            weapon_color = Config.RARITY_COLORS.get(rarity, Config.WHITE)
        else:
            weapon_color = Config.GRAY

        weapon_text = self.small_font.render(weapon_name, True, weapon_color)
        self.screen.blit(weapon_text, (self.equip_panel_x + 70, y_offset - 2))
        y_offset += 22

        # Weapon sprite preview
        if self.player.equipped_weapon:
            weapon_sprite = self.sprite_manager.get_sprite('weapon')
            if weapon_sprite:
                self.screen.blit(weapon_sprite, (self.equip_panel_x + 10, y_offset))

            # Weapon stats
            damage_text = self.tiny_font.render(
                f"DMG: {self.player.equipped_weapon.damage_range[0]}-{self.player.equipped_weapon.damage_range[1]}",
                True, Config.UI_TEXT)
            self.screen.blit(damage_text, (self.equip_panel_x + 50, y_offset + 5))

            crit_text = self.tiny_font.render(
                f"CRIT: {self.player.equipped_weapon.critical_chance:.0%}",
                True, Config.UI_TEXT)
            self.screen.blit(crit_text, (self.equip_panel_x + 130, y_offset + 5))

        y_offset += 35

        # Gold
        gold_text = self.small_font.render(f"Gold: {self.player.inventory.gold}", True, Config.YELLOW)
        self.screen.blit(gold_text, (self.equip_panel_x + 10, y_offset))

    def render_message_log(self):
        """Render message log panel"""
        # Draw panel background
        panel_rect = (self.message_panel_x, self.message_panel_y,
                     self.message_panel_width, self.message_panel_height)
        pygame.draw.rect(self.screen, Config.UI_BG, panel_rect)
        pygame.draw.rect(self.screen, Config.UI_BORDER, panel_rect, 2)

        # Title bar
        title_rect = (self.message_panel_x, self.message_panel_y,
                     self.message_panel_width, 20)
        pygame.draw.rect(self.screen, (40, 40, 60), title_rect)
        title_text = self.small_font.render("MESSAGE LOG", True, Config.UI_HIGHLIGHT)
        self.screen.blit(title_text, (self.message_panel_x + 10, self.message_panel_y + 3))

        # Render messages
        y_offset = self.message_panel_y + 25
        for message, color in self.messages[-self.max_messages:]:
            # Truncate long messages
            if len(message) > 80:
                message = message[:77] + "..."
            message_surface = self.small_font.render(message, True, color)
            self.screen.blit(message_surface, (self.message_panel_x + 10, y_offset))
            y_offset += 16

    def render_inventory(self):
        """Render inventory screen"""
        # Draw background overlay
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Draw inventory panel
        panel_rect = (self.inventory_panel_x, self.inventory_panel_y,
                     self.inventory_panel_width, self.inventory_panel_height)
        pygame.draw.rect(self.screen, Config.UI_BG, panel_rect)
        pygame.draw.rect(self.screen, Config.UI_BORDER, panel_rect, 3)

        # Title
        title_text = self.title_font.render("INVENTORY", True, Config.UI_HIGHLIGHT)
        title_rect = title_text.get_rect(center=(
            self.inventory_panel_x + self.inventory_panel_width // 2,
            self.inventory_panel_y + 30
        ))
        self.screen.blit(title_text, title_rect)

        # Gold display
        gold_text = self.font.render(f"Gold: {self.player.inventory.gold}", True, Config.YELLOW)
        self.screen.blit(gold_text, (self.inventory_panel_x + 20, self.inventory_panel_y + 60))

        # Capacity display
        capacity = f"Capacity: {len([i for i in self.player.inventory.items if i])}/{len(self.player.inventory.items)}"
        capacity_text = self.small_font.render(capacity, True, Config.UI_TEXT)
        self.screen.blit(capacity_text, (self.inventory_panel_x + 200, self.inventory_panel_y + 65))

        # Items grid
        slots_per_row = 10
        slot_size = 64
        slot_padding = 4
        start_x = self.inventory_panel_x + 20
        start_y = self.inventory_panel_y + 100

        for i, item in enumerate(self.player.inventory.items):
            row = i // slots_per_row
            col = i % slots_per_row

            slot_x = start_x + col * (slot_size + slot_padding)
            slot_y = start_y + row * (slot_size + slot_padding)

            # Draw slot background
            slot_color = Config.UI_HIGHLIGHT if i == self.selected_inventory_slot else (50, 50, 60)
            pygame.draw.rect(self.screen, slot_color,
                           (slot_x, slot_y, slot_size, slot_size))
            pygame.draw.rect(self.screen, Config.UI_BORDER,
                           (slot_x, slot_y, slot_size, slot_size), 2)

            if item:
                # Draw item sprite
                item_sprite = self.sprite_manager.get_item_sprite(item)
                if item_sprite:
                    # Scale sprite to fit slot
                    scaled_sprite = pygame.transform.scale(item_sprite, (slot_size - 8, slot_size - 8))
                    self.screen.blit(scaled_sprite, (slot_x + 4, slot_y + 4))

                # Draw item name (truncated)
                item_name = item.name[:8] if len(item.name) > 8 else item.name

                # Get rarity color
                rarity = getattr(item, 'rarity', 'common')
                item_color = Config.RARITY_COLORS.get(rarity, Config.WHITE)

                name_text = self.tiny_font.render(item_name, True, item_color)
                name_rect = name_text.get_rect(center=(slot_x + slot_size // 2, slot_y + slot_size - 8))
                self.screen.blit(name_text, name_rect)

                # Stack quantity
                if hasattr(item, 'quantity') and item.quantity > 1:
                    qty_text = self.small_font.render(str(item.quantity), True, Config.WHITE)
                    self.screen.blit(qty_text, (slot_x + 4, slot_y + 4))

        # Selected item details
        if 0 <= self.selected_inventory_slot < len(self.player.inventory.items):
            selected_item = self.player.inventory.items[self.selected_inventory_slot]
            if selected_item:
                detail_y = start_y + 3 * (slot_size + slot_padding) + 20

                # Item name
                rarity = getattr(selected_item, 'rarity', 'common')
                name_color = Config.RARITY_COLORS.get(rarity, Config.WHITE)
                name_text = self.font.render(selected_item.name, True, name_color)
                self.screen.blit(name_text, (self.inventory_panel_x + 20, detail_y))

                # Item description
                desc = getattr(selected_item, 'description', 'A mysterious item.')
                desc_text = self.small_font.render(desc, True, Config.UI_TEXT)
                self.screen.blit(desc_text, (self.inventory_panel_x + 20, detail_y + 25))

                # Item stats if weapon
                if hasattr(selected_item, 'damage_range'):
                    stats = f"Damage: {selected_item.damage_range[0]}-{selected_item.damage_range[1]}  Crit: {selected_item.critical_chance:.0%}"
                    stats_text = self.small_font.render(stats, True, Config.UI_TEXT)
                    self.screen.blit(stats_text, (self.inventory_panel_x + 20, detail_y + 45))

        # Instructions
        instructions = [
            "Click to select  |  [E] Equip  |  [U] Use  |  [D] Drop  |  [I/ESC] Close"
        ]
        inst_y = self.inventory_panel_y + self.inventory_panel_height - 40
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, Config.UI_TEXT)
            inst_rect = inst_text.get_rect(center=(
                self.inventory_panel_x + self.inventory_panel_width // 2, inst_y))
            self.screen.blit(inst_text, inst_rect)
            inst_y += 20

    def render_combat(self, combat_system):
        """Render combat screen"""
        # Draw background overlay
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Combat panel
        panel_width = 700
        panel_height = 500
        panel_x = (Config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (Config.SCREEN_HEIGHT - panel_height) // 2

        # Panel background
        pygame.draw.rect(self.screen, (30, 20, 20),
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (150, 50, 50),
                        (panel_x, panel_y, panel_width, panel_height), 3)

        # Title
        title_text = self.title_font.render("COMBAT!", True, Config.RED)
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 35))
        self.screen.blit(title_text, title_rect)

        # Combat status
        status = combat_system.get_combat_status()

        # Player side
        player_area_x = panel_x + 50
        player_area_y = panel_y + 80

        # Player sprite (larger)
        player_sprite = self.sprite_manager.get_animated_sprite('player', self.animation_frame)
        if player_sprite:
            scaled_player = pygame.transform.scale(player_sprite, (96, 96))
            self.screen.blit(scaled_player, (player_area_x, player_area_y))

        # Player name and health
        player_name = self.font.render(self.player.name, True, Config.PLAYER_COLOR)
        self.screen.blit(player_name, (player_area_x, player_area_y + 100))

        # Player health bar
        self._draw_large_health_bar(player_area_x, player_area_y + 125,
                                   self.player.current_hp, self.player.max_hp,
                                   150, 20, "HP")

        # Enemy side
        enemy_area_x = panel_x + panel_width - 200
        enemy_area_y = panel_y + 80

        # Enemy sprite (larger)
        enemy = combat_system.enemy
        enemy_sprite = self.sprite_manager.get_animated_sprite(enemy.enemy_type, self.animation_frame)
        if enemy_sprite:
            scaled_enemy = pygame.transform.scale(enemy_sprite, (96, 96))
            self.screen.blit(scaled_enemy, (enemy_area_x, enemy_area_y))

        # Enemy name and health
        enemy_name = self.font.render(status['enemy_name'], True, Config.RED)
        self.screen.blit(enemy_name, (enemy_area_x, enemy_area_y + 100))

        # Enemy health bar
        self._draw_large_health_bar(enemy_area_x, enemy_area_y + 125,
                                   enemy.current_hp, enemy.max_hp,
                                   150, 20, "HP")

        # VS text
        vs_text = self.title_font.render("VS", True, Config.YELLOW)
        vs_rect = vs_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 130))
        self.screen.blit(vs_text, vs_rect)

        # Combat log
        log_y = panel_y + 220
        pygame.draw.rect(self.screen, (20, 20, 30),
                        (panel_x + 20, log_y, panel_width - 40, 150))
        pygame.draw.rect(self.screen, Config.UI_BORDER,
                        (panel_x + 20, log_y, panel_width - 40, 150), 1)

        log_y_offset = log_y + 5
        for i, message in enumerate(status['log'][-7:]):
            log_text = self.small_font.render(message, True, Config.UI_TEXT)
            self.screen.blit(log_text, (panel_x + 30, log_y_offset + i * 20))

        # Action buttons (if player turn)
        if status['player_turn']:
            actions = combat_system.get_combat_options()
            button_width = 140
            button_height = 40
            button_y = panel_y + panel_height - 70
            total_width = len(actions) * button_width + (len(actions) - 1) * 20
            start_x = panel_x + (panel_width - total_width) // 2

            for i, action in enumerate(actions):
                button_x = start_x + i * (button_width + 20)

                # Button background
                pygame.draw.rect(self.screen, (60, 60, 80),
                               (button_x, button_y, button_width, button_height))
                pygame.draw.rect(self.screen, Config.UI_HIGHLIGHT,
                               (button_x, button_y, button_width, button_height), 2)

                # Button text
                action_text = self.font.render(action, True, Config.WHITE)
                text_rect = action_text.get_rect(center=(
                    button_x + button_width // 2,
                    button_y + button_height // 2
                ))
                self.screen.blit(action_text, text_rect)

                # Key hint
                key_hint = self.tiny_font.render(f"[{i + 1}]", True, Config.UI_TEXT)
                self.screen.blit(key_hint, (button_x + 5, button_y + 5))
        else:
            # Enemy turn message
            turn_text = self.font.render("Enemy's turn...", True, Config.RED)
            turn_rect = turn_text.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 50))
            self.screen.blit(turn_text, turn_rect)

    def _draw_large_health_bar(self, x: int, y: int, current: int, maximum: int,
                              width: int, height: int, label: str):
        """Draw a large health bar with label"""
        if maximum <= 0:
            return

        ratio = current / maximum

        # Background
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, width, height))

        # Health fill
        if ratio > 0:
            if ratio > 0.6:
                color = Config.GREEN
            elif ratio > 0.3:
                color = Config.YELLOW
            else:
                color = Config.RED

            fill_width = int(width * ratio)
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))

        # Border
        pygame.draw.rect(self.screen, (150, 150, 150), (x, y, width, height), 2)

        # Text
        hp_text = self.small_font.render(f"{current}/{maximum}", True, Config.WHITE)
        hp_rect = hp_text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(hp_text, hp_rect)

    def render_game_over(self):
        """Render game over screen"""
        # Draw background overlay
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((40, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.title_font.render("GAME OVER", True, Config.RED)
        text_rect = game_over_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, text_rect)

        # Death message
        death_msg = self.font.render("You have fallen in the dungeon...", True, Config.UI_TEXT)
        death_rect = death_msg.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(death_msg, death_rect)

        # Stats
        stats_text = self.small_font.render(
            f"Reached Level {self.player.level} | Dungeon Level {self.dungeon.current_level} | Kills: {self.player.total_kills}",
            True, Config.UI_TEXT)
        stats_rect = stats_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(stats_text, stats_rect)

        # Instructions
        restart_text = self.font.render("Press SPACE to try again or ESC to quit", True, Config.WHITE)
        restart_rect = restart_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def render_menu(self):
        """Render main menu"""
        # Background
        self.screen.fill((20, 15, 30))

        # Draw some decorative dungeon elements
        for i in range(20):
            x = (i * 67 + self.animation_frame * 2) % Config.SCREEN_WIDTH
            y = 100 + math.sin(i + self.animation_frame * 0.1) * 30
            wall_sprite = self.sprite_manager.get_sprite('wall')
            if wall_sprite:
                darkened = wall_sprite.copy()
                darkened.set_alpha(50)
                self.screen.blit(darkened, (x, y))

        # Title
        title_text = self.title_font.render("DUNGEON DELVER", True, Config.YELLOW)
        title_rect = title_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 3))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_text = self.font.render("A Roguelike Adventure", True, Config.UI_TEXT)
        subtitle_rect = subtitle_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 3 + 40))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Animated player sprite
        player_sprite = self.sprite_manager.get_animated_sprite('player', self.animation_frame)
        if player_sprite:
            scaled_player = pygame.transform.scale(player_sprite, (64, 64))
            self.screen.blit(scaled_player, (Config.SCREEN_WIDTH // 2 - 32, Config.SCREEN_HEIGHT // 2 - 20))

        # Start instruction
        blink = (self.animation_frame // 2) % 2 == 0
        if blink:
            start_text = self.font.render("Press SPACE or ENTER to begin", True, Config.WHITE)
            start_rect = start_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 80))
            self.screen.blit(start_text, start_rect)

        # Controls hint
        controls = [
            "Arrow Keys - Move",
            "I - Inventory",
            "> - Descend Stairs",
            "SPACE - Wait Turn"
        ]
        y_offset = Config.SCREEN_HEIGHT - 120
        for control in controls:
            control_text = self.small_font.render(control, True, Config.GRAY)
            control_rect = control_text.get_rect(center=(Config.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(control_text, control_rect)
            y_offset += 20

        # Version
        version_text = self.tiny_font.render(f"v{Config.VERSION}", True, Config.DARK_GRAY)
        self.screen.blit(version_text, (10, Config.SCREEN_HEIGHT - 20))

    def render_pause(self):
        """Render pause screen"""
        # Draw background overlay
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Pause text
        pause_text = self.title_font.render("PAUSED", True, Config.YELLOW)
        pause_rect = pause_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(pause_text, pause_rect)

        # Resume instruction
        resume_text = self.font.render("Press ESC to resume", True, Config.WHITE)
        resume_rect = resume_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(resume_text, resume_rect)

    def handle_inventory_click(self, mouse_pos: tuple) -> Optional[int]:
        """Handle inventory click and return item index if clicked"""
        if not self.inventory_active:
            return None

        # Calculate slot from mouse position
        slots_per_row = 10
        slot_size = 64
        slot_padding = 4
        start_x = self.inventory_panel_x + 20
        start_y = self.inventory_panel_y + 100

        # Check if click is within inventory grid
        grid_width = slots_per_row * (slot_size + slot_padding)
        grid_height = 2 * (slot_size + slot_padding)

        if (start_x <= mouse_pos[0] < start_x + grid_width and
            start_y <= mouse_pos[1] < start_y + grid_height):

            col = (mouse_pos[0] - start_x) // (slot_size + slot_padding)
            row = (mouse_pos[1] - start_y) // (slot_size + slot_padding)
            index = row * slots_per_row + col

            if 0 <= index < len(self.player.inventory.items):
                self.selected_inventory_slot = index
                return index

        return None

    def set_inventory_active(self, active: bool):
        """Set inventory panel active state"""
        self.inventory_active = active
        if not active:
            self.selected_inventory_slot = -1
