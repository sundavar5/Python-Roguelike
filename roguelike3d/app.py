from __future__ import annotations

import math
from typing import List, Tuple

import pyglet
from pyglet.window import key, mouse

from .entities import Enemy, Player, Treasure
from .hud import HUD
from .textures import ProceduralTextures
from .world import DungeonWorld

Vec3 = Tuple[float, float, float]


class RoguelikeApp(pyglet.window.Window):
    """Main application window and game loop."""

    def __init__(self, width: int = 1280, height: int = 720) -> None:
        super().__init__(width=width, height=height, caption="3D Roguelike", resizable=True)
        self.set_exclusive_mouse(True)

        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.world = DungeonWorld(width=32, height=32)
        self.textures = ProceduralTextures()
        self.player = Player(self.world.player_spawn)
        self.enemies: List[Enemy] = [Enemy(pos) for pos in self.world.enemy_spawns]
        self.treasures: List[Treasure] = [Treasure(pos) for pos in self.world.treasure_spawns]

        self.hud = HUD(self.width, self.height)

        self.pitch = 0.0
        self.yaw = 0.0
        self.mouse_sensitivity = 0.15
        self.speed = 5.5

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    # Camera helpers -----------------------------------------------------
    def _apply_camera(self) -> None:
        x, y, z = self.player.position
        gl = pyglet.gl
        gl.glRotatef(-self.pitch, 1, 0, 0)
        gl.glRotatef(-self.yaw, 0, 1, 0)
        gl.glTranslatef(-x, -y, -z)

    # Event handlers -----------------------------------------------------
    def on_draw(self) -> None:  # type: ignore[override]
        gl = pyglet.gl
        self.clear()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        pyglet.gl.gluPerspective(70.0, self.width / float(self.height), 0.1, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        self._apply_camera()

        self.world.draw(self.textures)
        for entity in self.enemies + self.treasures:
            entity.draw(self.textures)

        gl.glDisable(gl.GL_DEPTH_TEST)
        self.hud.draw(self.player, len(self.enemies), len(self.treasures))

    def on_resize(self, width: int, height: int) -> None:  # type: ignore[override]
        super().on_resize(width, height)
        self.hud.resize(width, height)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:  # type: ignore[override]
        self.yaw += dx * self.mouse_sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch + dy * self.mouse_sensitivity))

    def on_key_press(self, symbol: int, modifiers: int) -> None:  # type: ignore[override]
        if symbol == key.ESCAPE:
            self.close()
        if symbol == key.SPACE:
            self._attack()
        if symbol == key.E:
            self._interact()

    # Game mechanics -----------------------------------------------------
    def _move_vector(self, dt: float) -> Vec3:
        forward = math.radians(self.yaw)
        right = forward - math.pi / 2
        dx = 0.0
        dz = 0.0
        if self.keys[key.W]:
            dx += math.sin(forward)
            dz += math.cos(forward)
        if self.keys[key.S]:
            dx -= math.sin(forward)
            dz -= math.cos(forward)
        if self.keys[key.A]:
            dx += math.sin(right)
            dz += math.cos(right)
        if self.keys[key.D]:
            dx -= math.sin(right)
            dz -= math.cos(right)
        length = math.hypot(dx, dz)
        if length == 0:
            return (0.0, 0.0, 0.0)
        norm = self.speed * dt / length
        return (dx * norm, 0.0, dz * norm)

    def _attack(self) -> None:
        facing = self.player.forward_vector(self.yaw)
        hit = None
        for enemy in self.enemies:
            if enemy.is_alive and enemy.is_in_front(self.player.position, facing, 1.5):
                hit = enemy
                break
        if hit:
            hit.take_damage(25)
            self.hud.notify("Hit!", color=(255, 180, 140, 255))
        else:
            self.hud.notify("Miss", color=(200, 200, 200, 255))

    def _interact(self) -> None:
        facing = self.player.forward_vector(self.yaw)
        for treasure in self.treasures:
            if not treasure.opened and treasure.is_in_front(self.player.position, facing, 1.5):
                treasure.open()
                self.player.health = min(100, self.player.health + 10)
                self.player.energy = min(100, self.player.energy + 20)
                self.hud.notify("Found energy shards!", color=(120, 255, 180, 255))
                return
        self.hud.notify("Nothing to interact with", color=(220, 220, 220, 255))

    def _update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            enemy.update(dt, self.world.walkable)
            if enemy.collides(self.player.position, 0.4):
                self.player.take_damage(5 * dt)

        self.enemies = [e for e in self.enemies if e.is_alive]

    def _update_treasures(self) -> None:
        self.treasures = [t for t in self.treasures if not t.opened]

    def update(self, dt: float) -> None:
        if self.player.health <= 0:
            self.hud.notify("You died. Press ESC to exit.", color=(255, 120, 120, 255))
            return

        vx, vy, vz = self._move_vector(dt)
        new_pos = (self.player.position[0] + vx, self.player.position[1], self.player.position[2] + vz)
        if self.world.walkable(new_pos):
            self.player.position = new_pos

        self.player.energy = max(0.0, self.player.energy - 5 * dt)
        if self.player.energy <= 0:
            self.player.take_damage(10 * dt)

        self._update_enemies(dt)
        self._update_treasures()
