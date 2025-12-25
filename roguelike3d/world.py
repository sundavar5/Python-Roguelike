from __future__ import annotations

import random
from typing import List, Tuple
from dataclasses import dataclass

from .graphics import draw_cube
from .textures import ProceduralTextures

Vec3 = Tuple[float, float, float]

@dataclass
class Stairs:
    position: Vec3

    def draw(self, textures: ProceduralTextures, player_yaw: float = 0.0) -> None:
        draw_cube(self.position, 0.5, textures.floor_texture)

@dataclass
class ResourceNode:
    position: Vec3
    type: str = "Wood" # Wood, Iron
    health: int = 3

    def draw(self, textures: ProceduralTextures, player_yaw: float = 0.0) -> None:
        # In a real implementation we would have different textures for resources
        draw_cube(self.position, 0.4, textures.wall_texture)

class DungeonWorld:
    def __init__(self, width: int, height: int, depth: int = 1) -> None:
        self.width = width
        self.height = height
        self.depth = depth
        self.grid: List[List[int]] = [[1 for _ in range(width)] for _ in range(height)]
        self.player_spawn: Vec3 = (1.5, 0.5, 1.5)
        self.enemy_spawns: List[Tuple[Vec3, str]] = [] # Position, Type
        self.treasure_spawns: List[Vec3] = []
        self.resource_spawns: List[ResourceNode] = []
        self.stairs: Stairs = None
        self._generate()

    def _carve_room(self, x: int, y: int, w: int, h: int) -> None:
        for j in range(y, min(self.height - 1, y + h)):
            for i in range(x, min(self.width - 1, x + w)):
                self.grid[j][i] = 0

    def _generate(self) -> None:
        # Start with a simple random walker carving rooms
        x, y = self.width // 2, self.height // 2
        for _ in range(self.width * self.height // 2):
            w, h = random.randint(2, 4), random.randint(2, 4)
            self._carve_room(max(1, x - w // 2), max(1, y - h // 2), w, h)
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            x = max(1, min(self.width - 2, x + dx))
            y = max(1, min(self.height - 2, y + dy))

        walkable_tiles = [(i + 0.5, 0.5, j + 0.5) for j in range(self.height) for i in range(self.width) if self.grid[j][i] == 0]
        random.shuffle(walkable_tiles)
        if walkable_tiles:
            self.player_spawn = walkable_tiles.pop()

        # Spawn Stairs
        if walkable_tiles:
            self.stairs = Stairs(walkable_tiles.pop())

        # Spawn Resources
        self.resource_spawns = [ResourceNode(pos, random.choice(["Wood", "Iron"])) for pos in walkable_tiles[:5]]
        walkable_tiles = walkable_tiles[5:]

        # Spawn Enemies
        enemy_count = max(4, len(walkable_tiles) // 10)
        for _ in range(enemy_count):
            if not walkable_tiles: break
            pos = walkable_tiles.pop()
            etype = random.choice(["Rat", "Goblin", "Orc", "Skeleton"])
            self.enemy_spawns.append((pos, etype))

        # Spawn Treasure
        self.treasure_spawns = walkable_tiles[:6]

    # Rendering & collision ----------------------------------------------
    def walkable(self, pos: Vec3) -> bool:
        x, _, z = pos
        gx, gz = int(x), int(z)
        if gx < 0 or gz < 0 or gx >= self.width or gz >= self.height:
            return False
        return self.grid[gz][gx] == 0

    def draw(self, textures: ProceduralTextures) -> None:
        for j in range(self.height):
            for i in range(self.width):
                world_pos = (i + 0.5, 0.0, j + 0.5)
                if self.grid[j][i] == 0:
                    draw_cube((world_pos[0], -0.5, world_pos[2]), 0.5, textures.floor_texture)
                else:
                    draw_cube((world_pos[0], 0.5, world_pos[2]), 0.5, textures.wall_texture)
        if self.stairs:
            self.stairs.draw(textures)
