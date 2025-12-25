from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Tuple, List, Optional
import pyglet

from .items import Item, Weapon, Resource
from .textures import generate_sprite_texture

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
    inventory: List[Item] = field(default_factory=list)
    equipped_weapon: Optional[Weapon] = None

    def __init__(self, position: Vec3) -> None:
        super().__init__(position=position, color=(180, 230, 255, 255))
        self.inventory = []
        # Starting weapon
        self.equipped_weapon = Weapon(name="Rusty Dagger", damage=10.0, range=1.5, cooldown=0.5)
        self.inventory.append(self.equipped_weapon)

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
    sprite: Optional[pyglet.image.Texture] = None
    name: str = "Enemy"
    color: Tuple[int, int, int] = (255, 120, 120)
    speed: float = 1.5
    scale: float = 0.6

    def __init__(self, position: Vec3) -> None:
        super().__init__(position=position, color=self.color + (255,))
        self.patrol_dir = random.uniform(0, 360)

        # Procedural sprite generation based on random seed for this instance
        # In a real game we might want consistent sprites per class, but variation is fun
        self.init_stats()
        self.sprite = generate_sprite_texture(random.randint(0, 10000), self.color)

    def init_stats(self):
        self.health = 50.0
        self.speed = 1.5

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
        step = (math.sin(rad) * dt * self.speed, 0.0, math.cos(rad) * dt * self.speed)
        new_pos = (self.position[0] + step[0], self.position[1], self.position[2] + step[2])
        if walkable(new_pos):
            self.position = new_pos

    def draw(self, textures: "ProceduralTextures", player_yaw: float = 0.0) -> None:
        from .graphics import draw_billboard
        if self.sprite:
            draw_billboard(self.position, self.scale, self.sprite, player_yaw)


class Rat(Enemy):
    def init_stats(self):
        self.name = "Rat"
        self.health = 20.0
        self.speed = 2.5
        self.color = (120, 100, 90)
        self.scale = 0.4

class Goblin(Enemy):
    def init_stats(self):
        self.name = "Goblin"
        self.health = 40.0
        self.speed = 2.0
        self.color = (50, 150, 50)
        self.scale = 0.6

class Orc(Enemy):
    def init_stats(self):
        self.name = "Orc"
        self.health = 80.0
        self.speed = 1.2
        self.color = (30, 100, 30)
        self.scale = 0.8

class Skeleton(Enemy):
    def init_stats(self):
        self.name = "Skeleton"
        self.health = 30.0
        self.speed = 1.8
        self.color = (200, 200, 200)
        self.scale = 0.7


@dataclass
class Treasure(Entity):
    opened: bool = False

    def __init__(self, position: Vec3) -> None:
        super().__init__(position=position, color=(255, 215, 140, 255))

    def open(self) -> None:
        self.opened = True

    def draw(self, textures: "ProceduralTextures", player_yaw: float = 0.0) -> None:
        if self.opened:
            return
        from .graphics import draw_cube

        draw_cube(self.position, 0.3, textures.treasure_texture)
