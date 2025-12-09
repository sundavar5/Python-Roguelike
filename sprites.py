"""
Sprite generation and management system for the 2D roguelike
Generates pixel art sprites programmatically using pygame
"""

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional
from config import Config


class SpriteGenerator:
    """Generates pixel art sprites programmatically"""

    @staticmethod
    def create_surface(width: int, height: int, alpha: bool = True) -> pygame.Surface:
        """Create a new surface with optional alpha"""
        if alpha:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
        else:
            surface = pygame.Surface((width, height))
        return surface

    @staticmethod
    def draw_pixel(surface: pygame.Surface, x: int, y: int, color: tuple, scale: int = 1):
        """Draw a scaled pixel"""
        pygame.draw.rect(surface, color, (x * scale, y * scale, scale, scale))

    @staticmethod
    def generate_wall_tile(size: int = 32) -> pygame.Surface:
        """Generate a stone wall tile"""
        surface = SpriteGenerator.create_surface(size, size, False)

        # Base color
        base_color = (70, 70, 80)
        surface.fill(base_color)

        # Add stone texture
        random.seed(42)  # Consistent texture
        for _ in range(50):
            x = random.randint(0, size - 4)
            y = random.randint(0, size - 4)
            w = random.randint(3, 8)
            h = random.randint(3, 6)
            shade = random.randint(-20, 20)
            color = tuple(max(0, min(255, c + shade)) for c in base_color)
            pygame.draw.rect(surface, color, (x, y, w, h))

        # Add mortar lines
        mortar_color = (50, 50, 55)
        # Horizontal lines
        for y in [0, size // 3, 2 * size // 3]:
            pygame.draw.line(surface, mortar_color, (0, y), (size, y), 2)
        # Vertical lines (offset per row)
        for row in range(3):
            y_start = row * (size // 3)
            offset = (size // 4) if row % 2 else 0
            for x in [offset, offset + size // 2]:
                if 0 <= x < size:
                    pygame.draw.line(surface, mortar_color, (x, y_start), (x, y_start + size // 3), 2)

        # Add edge shading
        pygame.draw.line(surface, (90, 90, 100), (0, 0), (size - 1, 0), 1)
        pygame.draw.line(surface, (90, 90, 100), (0, 0), (0, size - 1), 1)
        pygame.draw.line(surface, (40, 40, 50), (size - 1, 0), (size - 1, size - 1), 1)
        pygame.draw.line(surface, (40, 40, 50), (0, size - 1), (size - 1, size - 1), 1)

        return surface

    @staticmethod
    def generate_floor_tile(size: int = 32, variant: int = 0) -> pygame.Surface:
        """Generate a floor tile"""
        surface = SpriteGenerator.create_surface(size, size, False)

        # Base color - darker dungeon floor
        base_color = (45, 42, 40)
        surface.fill(base_color)

        # Add subtle texture variation
        random.seed(variant)
        for _ in range(30):
            x = random.randint(0, size - 3)
            y = random.randint(0, size - 3)
            shade = random.randint(-10, 10)
            color = tuple(max(0, min(255, c + shade)) for c in base_color)
            pygame.draw.rect(surface, color, (x, y, 2, 2))

        # Add occasional cracks
        if variant % 5 == 0:
            crack_color = (35, 32, 30)
            start_x = random.randint(5, size - 10)
            for i in range(random.randint(3, 8)):
                pygame.draw.rect(surface, crack_color, (start_x + i, 10 + i * 2, 1, 2))

        return surface

    @staticmethod
    def generate_stairs_tile(size: int = 32, going_down: bool = True) -> pygame.Surface:
        """Generate stairs tile"""
        surface = SpriteGenerator.create_surface(size, size, False)

        # Base floor
        surface.fill((45, 42, 40))

        # Draw stairs
        step_count = 5
        step_height = size // step_count

        for i in range(step_count):
            y = i * step_height if going_down else (step_count - 1 - i) * step_height
            # Step surface
            step_color = (100 - i * 10, 90 - i * 10, 80 - i * 10)
            pygame.draw.rect(surface, step_color, (4, y, size - 8, step_height - 1))
            # Step edge highlight
            pygame.draw.line(surface, (130, 120, 110), (4, y), (size - 5, y), 1)

        # Add arrow indicator
        arrow_color = (200, 180, 100)
        center_x = size // 2
        if going_down:
            # Down arrow
            pygame.draw.polygon(surface, arrow_color, [
                (center_x, size - 6),
                (center_x - 5, size - 12),
                (center_x + 5, size - 12)
            ])
        else:
            # Up arrow
            pygame.draw.polygon(surface, arrow_color, [
                (center_x, 6),
                (center_x - 5, 12),
                (center_x + 5, 12)
            ])

        return surface

    @staticmethod
    def generate_player_sprite(size: int = 32, frame: int = 0) -> pygame.Surface:
        """Generate player character sprite"""
        surface = SpriteGenerator.create_surface(size, size)

        # Colors
        skin_color = (255, 200, 150)
        armor_color = (70, 130, 180)  # Steel blue
        armor_dark = (50, 100, 140)
        armor_light = (100, 160, 210)
        cape_color = (139, 0, 0)  # Dark red
        hair_color = (80, 50, 30)

        center_x = size // 2

        # Animation offset
        bob = math.sin(frame * 0.3) * 1

        # Cape (behind body)
        cape_points = [
            (center_x - 6, 10 + bob),
            (center_x - 8, 24 + bob),
            (center_x + 8, 24 + bob),
            (center_x + 6, 10 + bob)
        ]
        pygame.draw.polygon(surface, cape_color, cape_points)

        # Body/Armor
        body_rect = pygame.Rect(center_x - 5, int(12 + bob), 10, 10)
        pygame.draw.rect(surface, armor_color, body_rect)
        pygame.draw.rect(surface, armor_dark, body_rect, 1)
        # Armor highlight
        pygame.draw.line(surface, armor_light, (center_x - 4, int(13 + bob)), (center_x - 4, int(20 + bob)), 1)

        # Head
        head_rect = pygame.Rect(center_x - 4, int(4 + bob), 8, 8)
        pygame.draw.ellipse(surface, skin_color, head_rect)

        # Hair
        pygame.draw.arc(surface, hair_color, (center_x - 5, int(2 + bob), 10, 6), 0, math.pi, 2)

        # Eyes
        pygame.draw.rect(surface, (40, 40, 40), (center_x - 2, int(7 + bob), 2, 2))
        pygame.draw.rect(surface, (40, 40, 40), (center_x + 1, int(7 + bob), 2, 2))

        # Legs
        leg_offset = math.sin(frame * 0.5) * 2 if frame > 0 else 0
        pygame.draw.rect(surface, armor_dark, (center_x - 4, int(22 + bob), 3, 6))
        pygame.draw.rect(surface, armor_dark, (center_x + 1, int(22 + bob), 3, 6))

        # Boots
        pygame.draw.rect(surface, (60, 40, 20), (center_x - 5, int(27 + bob), 4, 3))
        pygame.draw.rect(surface, (60, 40, 20), (center_x + 1, int(27 + bob), 4, 3))

        # Sword (right side)
        sword_color = (180, 180, 190)
        pygame.draw.rect(surface, sword_color, (center_x + 7, int(10 + bob), 2, 14))
        pygame.draw.rect(surface, (139, 90, 43), (center_x + 6, int(20 + bob), 4, 4))  # Handle

        return surface

    @staticmethod
    def generate_enemy_sprite(enemy_type: str, size: int = 32, frame: int = 0) -> pygame.Surface:
        """Generate enemy sprite based on type"""
        if enemy_type == 'goblin':
            return SpriteGenerator._generate_goblin(size, frame)
        elif enemy_type == 'orc':
            return SpriteGenerator._generate_orc(size, frame)
        elif enemy_type == 'skeleton':
            return SpriteGenerator._generate_skeleton(size, frame)
        elif enemy_type == 'dragon':
            return SpriteGenerator._generate_dragon(size, frame)
        else:
            return SpriteGenerator._generate_goblin(size, frame)

    @staticmethod
    def _generate_goblin(size: int, frame: int) -> pygame.Surface:
        """Generate goblin sprite"""
        surface = SpriteGenerator.create_surface(size, size)

        skin_color = (80, 140, 80)
        skin_dark = (60, 110, 60)
        eye_color = (255, 255, 0)

        center_x = size // 2
        bob = math.sin(frame * 0.4) * 1

        # Body
        pygame.draw.ellipse(surface, skin_color, (center_x - 5, int(14 + bob), 10, 12))

        # Head (larger, goblin-like)
        pygame.draw.ellipse(surface, skin_color, (center_x - 6, int(4 + bob), 12, 12))

        # Ears (pointed)
        pygame.draw.polygon(surface, skin_color, [
            (center_x - 6, int(6 + bob)),
            (center_x - 10, int(2 + bob)),
            (center_x - 5, int(10 + bob))
        ])
        pygame.draw.polygon(surface, skin_color, [
            (center_x + 6, int(6 + bob)),
            (center_x + 10, int(2 + bob)),
            (center_x + 5, int(10 + bob))
        ])

        # Eyes (menacing yellow)
        pygame.draw.ellipse(surface, eye_color, (center_x - 4, int(7 + bob), 3, 3))
        pygame.draw.ellipse(surface, eye_color, (center_x + 1, int(7 + bob), 3, 3))
        pygame.draw.rect(surface, (0, 0, 0), (center_x - 3, int(8 + bob), 1, 1))
        pygame.draw.rect(surface, (0, 0, 0), (center_x + 2, int(8 + bob), 1, 1))

        # Nose
        pygame.draw.ellipse(surface, skin_dark, (center_x - 2, int(10 + bob), 4, 3))

        # Legs
        pygame.draw.rect(surface, skin_dark, (center_x - 4, int(24 + bob), 3, 5))
        pygame.draw.rect(surface, skin_dark, (center_x + 1, int(24 + bob), 3, 5))

        # Club weapon
        pygame.draw.rect(surface, (100, 70, 40), (center_x + 6, int(12 + bob), 3, 10))
        pygame.draw.ellipse(surface, (80, 50, 30), (center_x + 4, int(8 + bob), 6, 6))

        return surface

    @staticmethod
    def _generate_orc(size: int, frame: int) -> pygame.Surface:
        """Generate orc sprite"""
        surface = SpriteGenerator.create_surface(size, size)

        skin_color = (100, 120, 80)
        skin_dark = (70, 90, 50)
        armor_color = (80, 60, 40)

        center_x = size // 2
        bob = math.sin(frame * 0.3) * 1

        # Body (bulky)
        pygame.draw.ellipse(surface, skin_color, (center_x - 7, int(12 + bob), 14, 14))
        # Armor vest
        pygame.draw.ellipse(surface, armor_color, (center_x - 5, int(14 + bob), 10, 10))

        # Head
        pygame.draw.ellipse(surface, skin_color, (center_x - 5, int(4 + bob), 10, 10))

        # Tusks
        pygame.draw.polygon(surface, (240, 230, 200), [
            (center_x - 4, int(11 + bob)),
            (center_x - 5, int(15 + bob)),
            (center_x - 2, int(12 + bob))
        ])
        pygame.draw.polygon(surface, (240, 230, 200), [
            (center_x + 4, int(11 + bob)),
            (center_x + 5, int(15 + bob)),
            (center_x + 2, int(12 + bob))
        ])

        # Eyes (angry)
        pygame.draw.rect(surface, (200, 50, 50), (center_x - 3, int(7 + bob), 2, 2))
        pygame.draw.rect(surface, (200, 50, 50), (center_x + 1, int(7 + bob), 2, 2))

        # Eyebrow ridge
        pygame.draw.line(surface, skin_dark, (center_x - 4, int(6 + bob)), (center_x - 1, int(5 + bob)), 2)
        pygame.draw.line(surface, skin_dark, (center_x + 4, int(6 + bob)), (center_x + 1, int(5 + bob)), 2)

        # Arms
        pygame.draw.ellipse(surface, skin_color, (center_x - 10, int(14 + bob), 5, 10))
        pygame.draw.ellipse(surface, skin_color, (center_x + 5, int(14 + bob), 5, 10))

        # Legs
        pygame.draw.rect(surface, skin_dark, (center_x - 5, int(24 + bob), 4, 6))
        pygame.draw.rect(surface, skin_dark, (center_x + 1, int(24 + bob), 4, 6))

        # Axe
        pygame.draw.rect(surface, (100, 70, 40), (center_x + 8, int(8 + bob), 2, 16))
        pygame.draw.polygon(surface, (150, 150, 160), [
            (center_x + 7, int(6 + bob)),
            (center_x + 14, int(10 + bob)),
            (center_x + 7, int(14 + bob))
        ])

        return surface

    @staticmethod
    def _generate_skeleton(size: int, frame: int) -> pygame.Surface:
        """Generate skeleton sprite"""
        surface = SpriteGenerator.create_surface(size, size)

        bone_color = (230, 220, 200)
        bone_dark = (180, 170, 150)

        center_x = size // 2
        bob = math.sin(frame * 0.5) * 1

        # Skull
        pygame.draw.ellipse(surface, bone_color, (center_x - 5, int(3 + bob), 10, 10))
        # Eye sockets
        pygame.draw.ellipse(surface, (20, 20, 30), (center_x - 4, int(5 + bob), 3, 4))
        pygame.draw.ellipse(surface, (20, 20, 30), (center_x + 1, int(5 + bob), 3, 4))
        # Red eye glow
        pygame.draw.rect(surface, (255, 50, 50), (center_x - 3, int(6 + bob), 1, 2))
        pygame.draw.rect(surface, (255, 50, 50), (center_x + 2, int(6 + bob), 1, 2))
        # Nose hole
        pygame.draw.polygon(surface, (20, 20, 30), [
            (center_x, int(8 + bob)),
            (center_x - 1, int(10 + bob)),
            (center_x + 1, int(10 + bob))
        ])
        # Jaw
        pygame.draw.rect(surface, bone_color, (center_x - 3, int(11 + bob), 6, 2))

        # Spine/ribcage
        pygame.draw.rect(surface, bone_color, (center_x - 1, int(13 + bob), 2, 10))
        # Ribs
        for i in range(3):
            y = 15 + i * 3 + bob
            pygame.draw.ellipse(surface, bone_dark, (center_x - 5, int(y), 10, 2))

        # Arms (bone segments)
        pygame.draw.line(surface, bone_color, (center_x - 5, int(15 + bob)), (center_x - 9, int(22 + bob)), 2)
        pygame.draw.line(surface, bone_color, (center_x + 5, int(15 + bob)), (center_x + 9, int(22 + bob)), 2)

        # Pelvis
        pygame.draw.ellipse(surface, bone_color, (center_x - 4, int(22 + bob), 8, 4))

        # Legs
        pygame.draw.line(surface, bone_color, (center_x - 3, int(25 + bob)), (center_x - 4, int(30 + bob)), 2)
        pygame.draw.line(surface, bone_color, (center_x + 3, int(25 + bob)), (center_x + 4, int(30 + bob)), 2)

        # Sword
        pygame.draw.rect(surface, (150, 150, 160), (center_x + 8, int(12 + bob), 2, 12))
        pygame.draw.rect(surface, (100, 80, 60), (center_x + 6, int(22 + bob), 6, 3))

        return surface

    @staticmethod
    def _generate_dragon(size: int, frame: int) -> pygame.Surface:
        """Generate dragon sprite (larger, more detailed)"""
        surface = SpriteGenerator.create_surface(size, size)

        body_color = (100, 40, 120)  # Purple
        body_dark = (70, 20, 90)
        belly_color = (160, 100, 140)
        wing_color = (80, 30, 100)

        center_x = size // 2
        bob = math.sin(frame * 0.25) * 2
        wing_flap = math.sin(frame * 0.4) * 3

        # Wings (behind body)
        # Left wing
        wing_points = [
            (center_x - 6, int(10 + bob)),
            (center_x - 14, int(4 + bob - wing_flap)),
            (center_x - 12, int(16 + bob)),
            (center_x - 6, int(16 + bob))
        ]
        pygame.draw.polygon(surface, wing_color, wing_points)
        # Right wing
        wing_points = [
            (center_x + 6, int(10 + bob)),
            (center_x + 14, int(4 + bob - wing_flap)),
            (center_x + 12, int(16 + bob)),
            (center_x + 6, int(16 + bob))
        ]
        pygame.draw.polygon(surface, wing_color, wing_points)

        # Body
        pygame.draw.ellipse(surface, body_color, (center_x - 7, int(12 + bob), 14, 12))
        pygame.draw.ellipse(surface, belly_color, (center_x - 4, int(14 + bob), 8, 8))

        # Tail
        tail_points = [
            (center_x + 5, int(20 + bob)),
            (center_x + 12, int(26 + bob)),
            (center_x + 14, int(24 + bob)),
            (center_x + 6, int(18 + bob))
        ]
        pygame.draw.polygon(surface, body_color, tail_points)
        # Tail spike
        pygame.draw.polygon(surface, body_dark, [
            (center_x + 12, int(26 + bob)),
            (center_x + 16, int(25 + bob)),
            (center_x + 14, int(24 + bob))
        ])

        # Neck
        pygame.draw.ellipse(surface, body_color, (center_x - 4, int(6 + bob), 8, 10))

        # Head
        pygame.draw.ellipse(surface, body_color, (center_x - 5, int(2 + bob), 10, 8))
        # Snout
        pygame.draw.ellipse(surface, body_color, (center_x - 2, int(1 + bob), 8, 5))

        # Horns
        pygame.draw.polygon(surface, body_dark, [
            (center_x - 4, int(3 + bob)),
            (center_x - 6, int(-2 + bob)),
            (center_x - 2, int(4 + bob))
        ])
        pygame.draw.polygon(surface, body_dark, [
            (center_x + 4, int(3 + bob)),
            (center_x + 6, int(-2 + bob)),
            (center_x + 2, int(4 + bob))
        ])

        # Eyes (menacing)
        pygame.draw.ellipse(surface, (255, 200, 0), (center_x - 3, int(4 + bob), 3, 2))
        pygame.draw.ellipse(surface, (255, 200, 0), (center_x + 1, int(4 + bob), 3, 2))
        pygame.draw.rect(surface, (0, 0, 0), (center_x - 2, int(4 + bob), 1, 2))
        pygame.draw.rect(surface, (0, 0, 0), (center_x + 2, int(4 + bob), 1, 2))

        # Nostrils with smoke
        pygame.draw.rect(surface, (30, 30, 30), (center_x, int(2 + bob), 1, 1))
        pygame.draw.rect(surface, (30, 30, 30), (center_x + 2, int(2 + bob), 1, 1))

        # Legs
        pygame.draw.ellipse(surface, body_dark, (center_x - 6, int(20 + bob), 4, 8))
        pygame.draw.ellipse(surface, body_dark, (center_x + 2, int(20 + bob), 4, 8))
        # Claws
        pygame.draw.polygon(surface, (50, 50, 50), [
            (center_x - 6, int(27 + bob)),
            (center_x - 8, int(30 + bob)),
            (center_x - 5, int(28 + bob))
        ])
        pygame.draw.polygon(surface, (50, 50, 50), [
            (center_x + 4, int(27 + bob)),
            (center_x + 6, int(30 + bob)),
            (center_x + 3, int(28 + bob))
        ])

        return surface

    @staticmethod
    def generate_item_sprite(item_type: str, size: int = 32) -> pygame.Surface:
        """Generate item sprite based on type"""
        surface = SpriteGenerator.create_surface(size, size)
        center_x = size // 2
        center_y = size // 2

        if item_type == 'health_potion':
            # Red potion bottle
            bottle_color = (200, 50, 50)
            glass_color = (255, 100, 100)
            pygame.draw.ellipse(surface, bottle_color, (center_x - 5, center_y - 2, 10, 12))
            pygame.draw.rect(surface, bottle_color, (center_x - 2, center_y - 8, 4, 8))
            pygame.draw.rect(surface, (139, 90, 43), (center_x - 3, center_y - 10, 6, 3))  # Cork
            pygame.draw.ellipse(surface, glass_color, (center_x - 3, center_y, 3, 4))  # Highlight

        elif item_type == 'mana_potion':
            # Blue potion bottle
            bottle_color = (50, 50, 200)
            glass_color = (100, 100, 255)
            pygame.draw.ellipse(surface, bottle_color, (center_x - 5, center_y - 2, 10, 12))
            pygame.draw.rect(surface, bottle_color, (center_x - 2, center_y - 8, 4, 8))
            pygame.draw.rect(surface, (139, 90, 43), (center_x - 3, center_y - 10, 6, 3))
            pygame.draw.ellipse(surface, glass_color, (center_x - 3, center_y, 3, 4))

        elif item_type == 'gold':
            # Gold coins
            coin_color = (255, 215, 0)
            coin_dark = (200, 160, 0)
            pygame.draw.ellipse(surface, coin_color, (center_x - 6, center_y - 2, 8, 8))
            pygame.draw.ellipse(surface, coin_dark, (center_x - 6, center_y - 2, 8, 8), 1)
            pygame.draw.ellipse(surface, coin_color, (center_x - 2, center_y - 4, 8, 8))
            pygame.draw.ellipse(surface, coin_dark, (center_x - 2, center_y - 4, 8, 8), 1)
            pygame.draw.ellipse(surface, coin_color, (center_x + 1, center_y, 8, 8))
            pygame.draw.ellipse(surface, coin_dark, (center_x + 1, center_y, 8, 8), 1)

        elif item_type == 'food':
            # Bread/meat
            bread_color = (180, 140, 80)
            pygame.draw.ellipse(surface, bread_color, (center_x - 7, center_y - 3, 14, 10))
            pygame.draw.ellipse(surface, (200, 160, 100), (center_x - 5, center_y - 2, 6, 4))  # Highlight

        elif item_type == 'weapon':
            # Sword
            blade_color = (180, 180, 190)
            handle_color = (139, 90, 43)
            pygame.draw.rect(surface, blade_color, (center_x - 1, center_y - 10, 3, 16))
            pygame.draw.polygon(surface, blade_color, [
                (center_x, center_y - 12),
                (center_x - 2, center_y - 10),
                (center_x + 3, center_y - 10)
            ])
            pygame.draw.rect(surface, handle_color, (center_x - 4, center_y + 4, 9, 3))  # Guard
            pygame.draw.rect(surface, (100, 60, 30), (center_x - 1, center_y + 7, 3, 6))  # Handle

        else:
            # Generic item (sparkle)
            pygame.draw.polygon(surface, (255, 255, 200), [
                (center_x, center_y - 8),
                (center_x + 2, center_y - 2),
                (center_x + 8, center_y),
                (center_x + 2, center_y + 2),
                (center_x, center_y + 8),
                (center_x - 2, center_y + 2),
                (center_x - 8, center_y),
                (center_x - 2, center_y - 2)
            ])

        return surface

    @staticmethod
    def generate_effect_sprite(effect_type: str, size: int = 32, frame: int = 0) -> pygame.Surface:
        """Generate visual effect sprites"""
        surface = SpriteGenerator.create_surface(size, size)
        center_x = size // 2
        center_y = size // 2

        if effect_type == 'attack_slash':
            # Sword slash effect
            alpha = max(0, 255 - frame * 40)
            color = (255, 255, 255, alpha)
            angle = frame * 15
            for i in range(3):
                offset = i * 3
                pygame.draw.arc(surface, color,
                              (center_x - 12 + offset, center_y - 12 + offset,
                               24 - offset * 2, 24 - offset * 2),
                              math.radians(angle), math.radians(angle + 90), 2)

        elif effect_type == 'hit':
            # Hit effect (star burst)
            alpha = max(0, 255 - frame * 50)
            expand = frame * 2
            for i in range(8):
                angle = i * (math.pi / 4)
                end_x = center_x + math.cos(angle) * (8 + expand)
                end_y = center_y + math.sin(angle) * (8 + expand)
                pygame.draw.line(surface, (255, 200, 0, alpha),
                               (center_x, center_y), (end_x, end_y), 2)

        elif effect_type == 'heal':
            # Green healing particles
            alpha = max(0, 255 - frame * 30)
            for i in range(5):
                y_offset = frame * 3 + i * 5
                x_offset = math.sin(frame * 0.5 + i) * 5
                pygame.draw.circle(surface, (100, 255, 100, alpha),
                                 (int(center_x + x_offset), int(center_y - y_offset)), 3)

        return surface


class SpriteManager:
    """Manages all game sprites and caching"""

    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.sprites: Dict[str, pygame.Surface] = {}
        self.animated_sprites: Dict[str, List[pygame.Surface]] = {}
        self.animation_frames = 8

        # Generate all sprites
        self._generate_all_sprites()

    def _generate_all_sprites(self):
        """Generate and cache all game sprites"""
        # Tiles
        self.sprites['wall'] = SpriteGenerator.generate_wall_tile(self.tile_size)
        self.sprites['stairs_down'] = SpriteGenerator.generate_stairs_tile(self.tile_size, True)
        self.sprites['stairs_up'] = SpriteGenerator.generate_stairs_tile(self.tile_size, False)

        # Generate floor tile variants
        for i in range(10):
            self.sprites[f'floor_{i}'] = SpriteGenerator.generate_floor_tile(self.tile_size, i)

        # Items
        self.sprites['health_potion'] = SpriteGenerator.generate_item_sprite('health_potion', self.tile_size)
        self.sprites['mana_potion'] = SpriteGenerator.generate_item_sprite('mana_potion', self.tile_size)
        self.sprites['gold'] = SpriteGenerator.generate_item_sprite('gold', self.tile_size)
        self.sprites['food'] = SpriteGenerator.generate_item_sprite('food', self.tile_size)
        self.sprites['weapon'] = SpriteGenerator.generate_item_sprite('weapon', self.tile_size)
        self.sprites['item'] = SpriteGenerator.generate_item_sprite('misc', self.tile_size)

        # Animated sprites - Player
        player_frames = []
        for i in range(self.animation_frames):
            player_frames.append(SpriteGenerator.generate_player_sprite(self.tile_size, i))
        self.animated_sprites['player'] = player_frames

        # Animated sprites - Enemies
        for enemy_type in ['goblin', 'orc', 'skeleton', 'dragon']:
            frames = []
            for i in range(self.animation_frames):
                frames.append(SpriteGenerator.generate_enemy_sprite(enemy_type, self.tile_size, i))
            self.animated_sprites[enemy_type] = frames

        # Effect sprites
        for effect in ['attack_slash', 'hit', 'heal']:
            frames = []
            for i in range(6):
                frames.append(SpriteGenerator.generate_effect_sprite(effect, self.tile_size, i))
            self.animated_sprites[effect] = frames

    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a static sprite by name"""
        return self.sprites.get(name)

    def get_animated_sprite(self, name: str, frame: int) -> Optional[pygame.Surface]:
        """Get an animated sprite frame"""
        frames = self.animated_sprites.get(name)
        if frames:
            return frames[frame % len(frames)]
        return None

    def get_floor_tile(self, x: int, y: int) -> pygame.Surface:
        """Get a floor tile with consistent variation based on position"""
        variant = (x * 7 + y * 13) % 10
        return self.sprites.get(f'floor_{variant}', self.sprites['floor_0'])

    def get_item_sprite(self, item) -> pygame.Surface:
        """Get sprite for an item based on its type"""
        item_type = getattr(item, 'item_type', 'misc')
        item_name = getattr(item, 'name', '').lower()

        if 'health' in item_name or 'healing' in item_name:
            return self.sprites.get('health_potion', self.sprites['item'])
        elif 'mana' in item_name:
            return self.sprites.get('mana_potion', self.sprites['item'])
        elif 'gold' in item_name or item_type == 'gold':
            return self.sprites.get('gold', self.sprites['item'])
        elif 'food' in item_name or 'bread' in item_name or 'meat' in item_name:
            return self.sprites.get('food', self.sprites['item'])
        elif item_type == 'weapon' or 'sword' in item_name or 'axe' in item_name:
            return self.sprites.get('weapon', self.sprites['item'])
        else:
            return self.sprites.get('item', self.sprites['item'])


class Animation:
    """Handles smooth animations for game entities"""

    def __init__(self, duration: float = 0.2):
        self.duration = duration
        self.elapsed = 0.0
        self.active = False
        self.start_pos: Optional[Tuple[float, float]] = None
        self.end_pos: Optional[Tuple[float, float]] = None
        self.callback = None

    def start(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], callback=None):
        """Start a movement animation"""
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.elapsed = 0.0
        self.active = True
        self.callback = callback

    def update(self, dt: float) -> Tuple[float, float]:
        """Update animation and return current position"""
        if not self.active or not self.start_pos or not self.end_pos:
            return self.end_pos or (0, 0)

        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration)

        # Smooth easing
        progress = self._ease_out_quad(progress)

        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress

        if self.elapsed >= self.duration:
            self.active = False
            if self.callback:
                self.callback()

        return (current_x, current_y)

    def _ease_out_quad(self, t: float) -> float:
        """Quadratic ease out function"""
        return 1 - (1 - t) * (1 - t)

    def is_complete(self) -> bool:
        """Check if animation is complete"""
        return not self.active


class VisualEffect:
    """Represents a visual effect in the game"""

    def __init__(self, effect_type: str, position: Tuple[int, int], duration: float = 0.3):
        self.effect_type = effect_type
        self.position = position
        self.duration = duration
        self.elapsed = 0.0
        self.frame = 0
        self.active = True

    def update(self, dt: float):
        """Update the effect"""
        self.elapsed += dt
        self.frame = int((self.elapsed / self.duration) * 6)

        if self.elapsed >= self.duration:
            self.active = False

    def is_finished(self) -> bool:
        """Check if effect has finished"""
        return not self.active


class EffectManager:
    """Manages visual effects"""

    def __init__(self, sprite_manager: SpriteManager):
        self.sprite_manager = sprite_manager
        self.effects: List[VisualEffect] = []

    def add_effect(self, effect_type: str, position: Tuple[int, int], duration: float = 0.3):
        """Add a new visual effect"""
        self.effects.append(VisualEffect(effect_type, position, duration))

    def update(self, dt: float):
        """Update all effects"""
        for effect in self.effects[:]:
            effect.update(dt)
            if effect.is_finished():
                self.effects.remove(effect)

    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int], tile_size: int):
        """Render all active effects"""
        for effect in self.effects:
            sprite = self.sprite_manager.get_animated_sprite(effect.effect_type, effect.frame)
            if sprite:
                x = effect.position[0] * tile_size - camera_offset[0]
                y = effect.position[1] * tile_size - camera_offset[1]
                screen.blit(sprite, (x, y))
