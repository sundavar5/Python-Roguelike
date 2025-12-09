from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Tuple

Vec3 = Tuple[float, float, float]


def _distance(a: Vec3, b: Vec3) -> float:
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


@dataclass
class Entity:
    position: Vec3
    color: Tuple[int, int, int, int]

    def is_in_front(self, origin: Vec3, facing: Vec3, distance: float) -> bool:
        to_self = (self.position[0] - origin[0], self.position[1] - origin[1], self.position[2] - origin[2])
        dot = sum(to_self[i] * facing[i] for i in range(3))
        return dot > 0 and _distance(origin, self.position) <= distance

    def collides(self, other: Vec3, radius: float) -> bool:
        return _distance(self.position, other) < radius


@dataclass
class Player(Entity):
    health: float = 100.0
    energy: float = 100.0

    def __init__(self, position: Vec3) -> None:
        super().__init__(position=position, color=(180, 230, 255, 255))

    def forward_vector(self, yaw: float) -> Vec3:
        rad = math.radians(yaw)
        return (math.sin(rad), 0.0, math.cos(rad))

    def take_damage(self, amount: float) -> None:
        self.health = max(0.0, self.health - amount)


@dataclass
class Enemy(Entity):
    is_alive: bool = True
    health: float = 50.0
    patrol_dir: float = 0.0
    wander_timer: float = 0.0

    def __init__(self, position: Vec3) -> None:
        super().__init__(position=position, color=(255, 120, 120, 255))
        self.patrol_dir = random.uniform(0, 360)
        self.health = 50.0

    def take_damage(self, amount: float) -> None:
        if not self.is_alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.is_alive = False

    def update(self, dt: float, walkable: Callable[[Vec3], bool]) -> None:
        if not self.is_alive:
            return
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            self.patrol_dir = random.uniform(0, 360)
            self.wander_timer = random.uniform(1.0, 3.0)
        rad = math.radians(self.patrol_dir)
        step = (math.sin(rad) * dt * 1.5, 0.0, math.cos(rad) * dt * 1.5)
        new_pos = (self.position[0] + step[0], self.position[1], self.position[2] + step[2])
        if walkable(new_pos):
            self.position = new_pos

    def draw(self, textures: "ProceduralTextures") -> None:
        from .graphics import draw_cube

        draw_cube(self.position, 0.4, textures.enemy_texture)


@dataclass
class Treasure(Entity):
    opened: bool = False

    def __init__(self, position: Vec3) -> None:
        super().__init__(position=position, color=(255, 215, 140, 255))

    def open(self) -> None:
        self.opened = True

    def draw(self, textures: "ProceduralTextures") -> None:
        if self.opened:
            return
        from .graphics import draw_cube

        draw_cube(self.position, 0.3, textures.treasure_texture)
