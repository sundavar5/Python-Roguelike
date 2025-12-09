from __future__ import annotations

import random
from typing import List, Tuple

from .graphics import draw_cube
from .textures import ProceduralTextures

Vec3 = Tuple[float, float, float]


class DungeonWorld:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid: List[List[int]] = [[1 for _ in range(width)] for _ in range(height)]
        self.player_spawn: Vec3 = (1.5, 0.5, 1.5)
        self.enemy_spawns: List[Vec3] = []
        self.treasure_spawns: List[Vec3] = []
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
        self.enemy_spawns = walkable_tiles[: max(4, len(walkable_tiles) // 20)]
        self.treasure_spawns = walkable_tiles[len(self.enemy_spawns) : len(self.enemy_spawns) + 6]

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
