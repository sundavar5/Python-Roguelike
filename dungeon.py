"""
Dungeon generation and management system
"""

import random
from typing import List, Optional, Tuple, Set
from utils import Vector2, Rect, RandomUtils, Dice
from config import Config
from enemy import Enemy
from item import Item

class Tile:
    """Represents a single tile in the dungeon"""
    
    def __init__(self, tile_type: str = 'wall'):
        self.type = tile_type  # wall, floor, door, stairs, trap
        self.explored = False
        self.visible = False
        self.blocked = tile_type == 'wall'
        self.blocks_sight = tile_type == 'wall'
    
    def set_type(self, tile_type: str):
        """Set the tile type and update properties"""
        self.type = tile_type
        self.blocked = tile_type == 'wall'
        self.blocks_sight = tile_type == 'wall'
        
        if tile_type == 'door':
            self.blocked = True
            self.blocks_sight = True
        elif tile_type == 'open_door':
            self.blocked = False
            self.blocks_sight = False

class Dungeon:
    """Dungeon class with procedural generation"""
    
    def __init__(self, width: int, height: int):
        """Initialize dungeon"""
        self.width = width
        self.height = height
        self.tiles = [[Tile('wall') for _ in range(height)] for _ in range(width)]
        self.rooms: List[Rect] = []
        self.enemies: List[Enemy] = []
        self.items: List[Tuple[Vector2, Item]] = []
        self.current_level = 1
        self.stairs_up = None
        self.stairs_down = None
        
        # Generate initial dungeon
        self.generate()
    
    def generate(self):
        """Generate the dungeon layout"""
        self._generate_rooms()
        self._connect_rooms()
        self._place_stairs()
        self._place_enemies()
        self._place_items()
    
    def _generate_rooms(self):
        """Generate random rooms"""
        self.rooms.clear()
        max_rooms = 15
        min_room_size = 4
        max_room_size = 10
        
        for _ in range(max_rooms):
            # Random room size
            room_width = Dice.roll_range(min_room_size, max_room_size)
            room_height = Dice.roll_range(min_room_size, max_room_size)
            
            # Ensure room fits in dungeon
            if room_width >= self.width or room_height >= self.height:
                continue
                
            # Random position
            x = Dice.roll_range(1, max(1, self.width - room_width - 1))
            y = Dice.roll_range(1, max(1, self.height - room_height - 1))
            
            new_room = Rect(x, y, room_width, room_height)
            
            # Check if room overlaps with existing rooms
            if not any(new_room.intersects(room) for room in self.rooms):
                self.rooms.append(new_room)
                self._carve_room(new_room)
    
    def _carve_room(self, room: Rect):
        """Carve out a room in the dungeon"""
        for x in range(room.left, room.right):
            for y in range(room.top, room.bottom):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[x][y].set_type('floor')
    
    def _connect_rooms(self):
        """Connect rooms with corridors"""
        if len(self.rooms) < 2:
            return
        
        # Connect each room to the next one
        for i in range(len(self.rooms) - 1):
            self._connect_rooms_with_corridor(self.rooms[i], self.rooms[i + 1])
        
        # Add some random connections for more interesting layouts
        for _ in range(len(self.rooms) // 3):
            room1 = random.choice(self.rooms)
            room2 = random.choice(self.rooms)
            if room1 != room2:
                self._connect_rooms_with_corridor(room1, room2)
    
    def _connect_rooms_with_corridor(self, room1: Rect, room2: Rect):
        """Create a corridor between two rooms"""
        # Get center points of rooms
        center1 = room1.center
        center2 = room2.center
        
        # Decide whether to go horizontal first or vertical first
        if Dice.roll(2) == 1:
            # Horizontal first
            self._create_horizontal_corridor(int(center1.x), int(center2.x), int(center1.y))
            self._create_vertical_corridor(int(center1.y), int(center2.y), int(center2.x))
        else:
            # Vertical first
            self._create_vertical_corridor(int(center1.y), int(center2.y), int(center1.x))
            self._create_horizontal_corridor(int(center1.x), int(center2.x), int(center2.y))
    
    def _create_horizontal_corridor(self, x1: int, x2: int, y: int):
        """Create a horizontal corridor"""
        start_x = min(x1, x2)
        end_x = max(x1, x2)
        
        for x in range(start_x, end_x + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[x][y].set_type('floor')
    
    def _create_vertical_corridor(self, y1: int, y2: int, x: int):
        """Create a vertical corridor"""
        start_y = min(y1, y2)
        end_y = max(y1, y2)
        
        for y in range(start_y, end_y + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[x][y].set_type('floor')
    
    def _place_stairs(self):
        """Place stairs up and down"""
        if len(self.rooms) >= 2:
            # Stairs up in first room
            self.stairs_up = self.rooms[0].center
            self.tiles[int(self.stairs_up.x)][int(self.stairs_up.y)].set_type('stairs')
            
            # Stairs down in last room
            self.stairs_down = self.rooms[-1].center
            self.tiles[int(self.stairs_down.x)][int(self.stairs_down.y)].set_type('stairs')
    
    def _place_enemies(self):
        """Place enemies in rooms"""
        self.enemies.clear()
        
        # Skip the first room (player start)
        for room in self.rooms[1:]:
            # 50% chance to place an enemy in each room
            if Dice.roll(2) == 1:
                # Random position within room
                x = Dice.roll_range(room.left + 1, room.right - 1)
                y = Dice.roll_range(room.top + 1, room.bottom - 1)
                
                # Choose enemy type based on dungeon level
                enemy_type = self._choose_enemy_type()
                enemy = Enemy(enemy_type, Vector2(x, y), self.current_level)
                self.enemies.append(enemy)
    
    def _place_items(self):
        """Place items in rooms"""
        self.items.clear()
        
        for room in self.rooms:
            # 30% chance to place an item in each room
            if Dice.roll(10) <= 3:
                # Random position within room
                x = Dice.roll_range(room.left + 1, room.right - 1)
                y = Dice.roll_range(room.top + 1, room.bottom - 1)
                
                # Create random item
                item = self._create_random_item()
                self.items.append((Vector2(x, y), item))
    
    def _choose_enemy_type(self) -> str:
        """Choose enemy type based on dungeon level"""
        if self.current_level <= 2:
            return 'goblin'
        elif self.current_level <= 4:
            return random.choice(['goblin', 'orc'])
        elif self.current_level <= 6:
            return random.choice(['goblin', 'orc', 'skeleton'])
        else:
            return random.choice(['orc', 'skeleton', 'dragon'])
    
    def _create_random_item(self) -> Item:
        """Create a random item for dungeon placement"""
        # Import here to avoid circular import
        from item import HealthPotion, ManaPotion, Food, Gold
        from weapon import Weapon
        
        item_type = Dice.choice(['potion', 'gold', 'food', 'weapon'])
        
        if item_type == 'potion':
            return Dice.choice([
                HealthPotion.create_minor(),
                ManaPotion.create_minor()
            ])
        elif item_type == 'gold':
            return Gold(Dice.roll_range(5, 50))
        elif item_type == 'food':
            return Dice.choice([
                Food.create_bread(),
                Food.create_meat(),
                Food.create_fruit()
            ])
        elif item_type == 'weapon':
            return Weapon.generate_random()
        
        return Item("Mysterious Item", 'misc', 5, 1.0)
    
    def generate_next_level(self):
        """Generate the next dungeon level"""
        self.current_level += 1
        self.generate()
        print(f"Welcome to dungeon level {self.current_level}!")
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile is walkable"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check if tile is blocked
        if self.tiles[x][y].blocked:
            return False
        
        # Check if there's an enemy there
        for enemy in self.enemies:
            if enemy.is_alive and enemy.position.x == x and enemy.position.y == y:
                return False
        
        return True
    
    def is_stairs(self, x: int, y: int) -> bool:
        """Check if tile is stairs"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        return self.tiles[x][y].type == 'stairs'
    
    def get_enemy_at(self, x: int, y: int) -> Optional[Enemy]:
        """Get enemy at given position"""
        for enemy in self.enemies:
            if enemy.is_alive and enemy.position.x == x and enemy.position.y == y:
                return enemy
        return None
    
    def get_item_at(self, x: int, y: int) -> Optional[Item]:
        """Get item at given position"""
        for pos, item in self.items:
            if pos.x == x and pos.y == y:
                return item
        return None
    
    def remove_enemy(self, enemy: Enemy):
        """Remove an enemy from the dungeon"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
    
    def remove_item(self, x: int, y: int):
        """Remove item at given position"""
        self.items = [(pos, item) for pos, item in self.items 
                     if not (pos.x == x and pos.y == y)]
    
    def update_visibility(self, player_pos: Vector2, view_distance: int = 10):
        """Update tile visibility based on player position"""
        # Reset visibility
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[x][y].visible = False
        
        # Calculate visible tiles (simple circular visibility)
        for x in range(self.width):
            for y in range(self.height):
                distance = Vector2(x, y).distance_to(player_pos)
                if distance <= view_distance:
                    self.tiles[x][y].visible = True
                    self.tiles[x][y].explored = True
    
    def get_tile_at(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at given coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y]
        return None
    
    def get_char_at(self, x: int, y: int) -> str:
        """Get character representation for a tile"""
        # Check for enemies
        enemy = self.get_enemy_at(x, y)
        if enemy:
            return enemy.char
        
        # Check for items
        item = self.get_item_at(x, y)
        if item:
            return 'i'  # Item symbol
        
        # Check tile type
        tile = self.get_tile_at(x, y)
        if tile:
            if tile.type == 'wall':
                return '#'
            elif tile.type == 'floor':
                return '.'
            elif tile.type == 'door':
                return '+'
            elif tile.type == 'open_door':
                return "'"
            elif tile.type == 'stairs':
                return Config.STAIRS_COLOR
                return '>'
            elif tile.type == 'trap':
                return '^'
        
        return ' '  # Unknown/empty
    
    def get_color_at(self, x: int, y: int) -> tuple:
        """Get color for a tile"""
        # Check for enemies
        enemy = self.get_enemy_at(x, y)
        if enemy:
            return enemy.color
        
        # Check for items
        item = self.get_item_at(x, y)
        if item:
            return item.color
        
        # Check tile type
        tile = self.get_tile_at(x, y)
        if tile:
            if tile.type == 'wall':
                return Config.WALL_COLOR
            elif tile.type == 'floor':
                return Config.FLOOR_COLOR
            elif tile.type == 'door':
                return Config.BROWN
            elif tile.type == 'open_door':
                return Config.LIGHT_GRAY
            elif tile.type == 'stairs':
                return Config.STAIRS_COLOR