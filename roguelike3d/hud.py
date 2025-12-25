from __future__ import annotations

import time
from typing import Tuple

import pyglet

from .entities import Player


class HUD:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.notification: str | None = None
        self.notification_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.notification_time = 0.0

        self.health_bar = pyglet.shapes.Rectangle(20, height - 40, 0, 12, color=(220, 80, 80))
        self.energy_bar = pyglet.shapes.Rectangle(20, height - 60, 0, 12, color=(80, 180, 220))
        self.frame = pyglet.shapes.Rectangle(15, height - 70, 210, 50, color=(20, 20, 20))
        self.frame.opacity = 160
        self.label = pyglet.text.Label("", x=25, y=height - 48, font_name="Arial", font_size=10, anchor_y="center")

        # New persistent labels
        self.weapon_label = pyglet.text.Label("", x=25, y=height - 85, font_name="Arial", font_size=10)
        self.inv_label = pyglet.text.Label("", x=25, y=height - 100, font_name="Arial", font_size=9, width=width//2, multiline=True)

        self.toast = pyglet.text.Label("", x=width // 2, y=40, font_name="Arial", font_size=14, anchor_x="center")

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.frame.y = height - 70
        self.health_bar.y = height - 40
        self.energy_bar.y = height - 60
        self.weapon_label.y = height - 85
        self.inv_label.y = height - 100
        self.inv_label.width = width // 2
        self.toast.x = width // 2

    def notify(self, message: str, color: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> None:
        self.notification = message
        self.notification_color = color
        self.notification_time = time.time()

    def draw(self, player: Player, enemy_count: int, treasures: int, level: int = 1) -> None:
        self.frame.draw()
        self.health_bar.width = int(2 * player.health)
        self.energy_bar.width = int(2 * player.energy)
        self.health_bar.draw()
        self.energy_bar.draw()

        self.label.text = f"LVL {level}   HP {player.health:05.1f}   EN {player.energy:05.1f}"
        self.label.draw()

        # Equipment info
        weapon = player.equipped_weapon.name if player.equipped_weapon else "None"
        inventory_counts = {}
        for item in player.inventory:
            inventory_counts[item.name] = inventory_counts.get(item.name, 0) + item.count

        inv_str = " | ".join([f"{k} x{v}" for k, v in inventory_counts.items()])

        self.weapon_label.text = f"Weapon: {weapon}"
        self.weapon_label.draw()

        self.inv_label.text = f"Inv: {inv_str}"
        self.inv_label.draw()

        if self.notification and time.time() - self.notification_time < 3:
            self.toast.text = self.notification
            self.toast.color = self.notification_color
            self.toast.draw()
