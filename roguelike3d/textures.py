from __future__ import annotations

import random
from typing import Tuple

import numpy as np
from noise import pnoise2
import pyglet

Color = Tuple[int, int, int]


def _generate_noise(width: int, height: int, scale: float, octaves: int = 3) -> np.ndarray:
    data = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            data[y, x] = pnoise2(x / scale, y / scale, octaves=octaves, persistence=0.6, lacunarity=2.0, repeatx=width, repeaty=height)
    data = (data - data.min()) / (data.ptp() + 1e-6)
    return data


def _mix(color_a: Color, color_b: Color, factor: float) -> Color:
    return tuple(int(a * (1 - factor) + b * factor) for a, b in zip(color_a, color_b))  # type: ignore[return-value]


def _texture_from_palette(base: Color, accent: Color, width: int = 64, height: int = 64) -> pyglet.image.Texture:
    noise = _generate_noise(width, height, scale=16.0)
    pixels = []
    for y in range(height):
        for x in range(width):
            mask = noise[y, x]
            color = _mix(base, accent, mask)
            pixels.extend((*color, 255))
    data = bytes(pixels)
    image = pyglet.image.ImageData(width, height, "RGBA", data)
    return image.get_texture()


def _stone_palette() -> Color:
    return random.choice([(80, 80, 90), (70, 70, 60), (95, 90, 85)])


def _moss_palette() -> Color:
    return random.choice([(60, 100, 60), (70, 120, 80), (80, 140, 90)])


class ProceduralTextures:
    def __init__(self) -> None:
        base_wall = _stone_palette()
        accent_wall = _moss_palette()
        base_floor = (90, 80, 70)
        accent_floor = (120, 110, 90)
        base_enemy = (170, 50, 50)
        accent_enemy = (250, 110, 90)
        base_treasure = (200, 160, 60)
        accent_treasure = (255, 220, 140)

        self.wall_texture = _texture_from_palette(base_wall, accent_wall)
        self.floor_texture = _texture_from_palette(base_floor, accent_floor)
        self.enemy_texture = _texture_from_palette(base_enemy, accent_enemy)
        self.treasure_texture = _texture_from_palette(base_treasure, accent_treasure)
