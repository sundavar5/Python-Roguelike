from __future__ import annotations

import math
from typing import List, Tuple

import pyglet
from pyglet.window import key, mouse

import random
from .entities import Enemy, Player, Treasure, Rat, Goblin, Orc, Skeleton
from .hud import HUD
from .textures import ProceduralTextures
from .world import DungeonWorld
from .items import Weapon, Item

Vec3 = Tuple[float, float, float]

class GameState:
    INTRO = 0
    PLAYING = 1
    WIN = 2
    LOSE = 3

class RoguelikeApp(pyglet.window.Window):
    """Main application window and game loop."""

    def __init__(self, width: int = 1280, height: int = 720) -> None:
        super().__init__(width=width, height=height, caption="3D Roguelike", resizable=True)
        self.set_exclusive_mouse(True)

        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.state = GameState.INTRO
        self.intro_text = [
            "You enter the dark dungeon...",
            "Monsters lurk in the shadows.",
            "Scavenge for resources.",
            "Craft weapons.",
            "Descend to Level 5 to find the artifact.",
            "Press SPACE to begin."
        ]

        self.level = 1
        self.init_level()

        self.hud = HUD(self.width, self.height)

        self.pitch = 0.0
        self.yaw = 0.0
        self.mouse_sensitivity = 0.15
        self.speed = 5.5

        self.attack_cooldown = 0.0

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def init_level(self):
        self.world = DungeonWorld(width=32, height=32, depth=self.level)
        self.textures = ProceduralTextures()
        if not hasattr(self, 'player'):
            self.player = Player(self.world.player_spawn)
        else:
            self.player.position = self.world.player_spawn

        self.enemies: List[Enemy] = []
        for pos, etype in self.world.enemy_spawns:
            if etype == "Rat": self.enemies.append(Rat(pos))
            elif etype == "Goblin": self.enemies.append(Goblin(pos))
            elif etype == "Orc": self.enemies.append(Orc(pos))
            elif etype == "Skeleton": self.enemies.append(Skeleton(pos))
            else: self.enemies.append(Enemy(pos))

        self.treasures: List[Treasure] = [Treasure(pos) for pos in self.world.treasure_spawns]
        self.hud = HUD(self.width, self.height)

    # Camera helpers -----------------------------------------------------
    def _apply_camera(self) -> None:
        x, y, z = self.player.position
        gl = pyglet.gl
        gl.glRotatef(-self.pitch, 1, 0, 0)
        gl.glRotatef(-self.yaw, 0, 1, 0)
        gl.glTranslatef(-x, -y, -z)

    # Event handlers -----------------------------------------------------
    def on_draw(self) -> None:  # type: ignore[override]
        self.clear()

        if self.state == GameState.INTRO:
            self.draw_text_screen("Medieval Dungeon", self.intro_text)
            return
        if self.state == GameState.LOSE:
            self.draw_text_screen("GAME OVER", ["You died.", "Press ESC to quit."])
            return
        if self.state == GameState.WIN:
            self.draw_text_screen("VICTORY", ["You found the artifact!", "You are a hero.", "Press ESC to quit."])
            return

        gl = pyglet.gl
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
            entity.draw(self.textures, self.yaw)

        # Draw resources
        for node in self.world.resource_spawns:
            node.draw(self.textures, self.yaw)

        gl.glDisable(gl.GL_DEPTH_TEST)
        self.hud.draw(self.player, len(self.enemies), len(self.treasures), self.level)

    def draw_text_screen(self, title: str, lines: List[str]):
        # This is okay for now since game states don't change often/frequently enough to cause major GC
        # But for robustness, we could cache them. Given the scope, this simple optimization is acceptable.
        pyglet.text.Label(title, font_size=36, x=self.width//2, y=self.height - 100, anchor_x="center").draw()
        y = self.height - 200
        for line in lines:
            pyglet.text.Label(line, font_size=18, x=self.width//2, y=y, anchor_x="center").draw()
            y -= 30

    def on_resize(self, width: int, height: int) -> None:  # type: ignore[override]
        super().on_resize(width, height)
        self.hud.resize(width, height)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:  # type: ignore[override]
        self.yaw += dx * self.mouse_sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch + dy * self.mouse_sensitivity))

    def on_key_press(self, symbol: int, modifiers: int) -> None:  # type: ignore[override]
        if symbol == key.ESCAPE:
            self.close()

        if self.state == GameState.INTRO:
            if symbol == key.SPACE:
                self.state = GameState.PLAYING
            return

        if self.state != GameState.PLAYING:
            return

        if symbol == key.SPACE:
            self._attack()
        if symbol == key.E:
            self._interact()

        # Crafting shortcuts
        if symbol == key._1:
            self._craft("Dagger")
        if symbol == key._2:
            self._craft("Sword")

    # Game mechanics -----------------------------------------------------
    def _craft(self, item_type: str):
        # Simplified crafting
        wood = 0
        iron = 0
        for item in self.player.inventory:
            if item.name == "Wood": wood += item.count
            if item.name == "Iron": iron += item.count

        if item_type == "Sword":
            if wood >= 1 and iron >= 1:
                # Remove items
                self._remove_item("Wood", 1)
                self._remove_item("Iron", 1)
                self.player.equipped_weapon = Weapon(name="Iron Sword", damage=25.0, range=2.0, cooldown=0.8)
                self.player.inventory.append(self.player.equipped_weapon)
                self.hud.notify("Crafted Iron Sword!")
            else:
                self.hud.notify("Need 1 Wood, 1 Iron")
        elif item_type == "Dagger":
             if iron >= 1:
                self._remove_item("Iron", 1)
                self.player.equipped_weapon = Weapon(name="Iron Dagger", damage=15.0, range=1.5, cooldown=0.4)
                self.player.inventory.append(self.player.equipped_weapon)
                self.hud.notify("Crafted Iron Dagger!")
             else:
                self.hud.notify("Need 1 Iron")

    def _remove_item(self, name: str, count: int):
        to_remove = count
        for item in self.player.inventory[:]:
            if item.name == name:
                if item.count >= to_remove:
                    item.count -= to_remove
                    to_remove = 0
                else:
                    to_remove -= item.count
                    item.count = 0
                if item.count == 0:
                    self.player.inventory.remove(item)
            if to_remove == 0: break

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
        if self.attack_cooldown > 0: return

        weapon = self.player.equipped_weapon
        damage = weapon.damage if weapon else 5.0
        rng = weapon.range if weapon else 1.0
        cooldown = weapon.cooldown if weapon else 0.5

        self.attack_cooldown = cooldown

        facing = self.player.forward_vector(self.yaw)
        hit = None

        # Attack enemies
        for enemy in self.enemies:
            if enemy.is_alive and enemy.is_in_front(self.player.position, facing, rng):
                hit = enemy
                break

        if hit:
            hit.take_damage(damage)
            self.hud.notify(f"Hit {hit.name} for {damage}!", color=(255, 180, 140, 255))
        else:
            # Try hit resources
            for node in self.world.resource_spawns:
                # Simple distance check for resources
                dist = math.sqrt(sum((a-b)**2 for a,b in zip(self.player.position, node.position)))
                if dist < rng + 0.5:
                     self.world.resource_spawns.remove(node)
                     # Add resource
                     res_type = node.type
                     found = False
                     for item in self.player.inventory:
                         if item.name == res_type:
                             item.count += 1
                             found = True
                             break
                     if not found:
                         self.player.inventory.append(Item(name=res_type, count=1))
                     self.hud.notify(f"Gathered {res_type}", color=(100, 255, 100, 255))
                     return

            self.hud.notify("Miss", color=(200, 200, 200, 255))

    def _interact(self) -> None:
        facing = self.player.forward_vector(self.yaw)
        for treasure in self.treasures:
            if not treasure.opened and treasure.is_in_front(self.player.position, facing, 1.5):
                treasure.open()
                self.player.health = min(100, self.player.health + 10)
                self.player.energy = min(100, self.player.energy + 20)
                self.hud.notify("Found potion!", color=(120, 255, 180, 255))
                return

        # Stairs
        if self.world.stairs:
            dist = math.sqrt(sum((a-b)**2 for a,b in zip(self.player.position, self.world.stairs.position)))
            if dist < 1.5:
                self.level += 1
                if self.level > 5:
                    self.state = GameState.WIN
                else:
                    self.init_level()
                    self.hud.notify(f"Descended to Level {self.level}")
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
        if self.state != GameState.PLAYING:
            return

        if self.player.health <= 0:
            self.state = GameState.LOSE
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        vx, vy, vz = self._move_vector(dt)
        new_pos = (self.player.position[0] + vx, self.player.position[1], self.player.position[2] + vz)
        if self.world.walkable(new_pos):
            self.player.position = new_pos

        self.player.energy = max(0.0, self.player.energy - 1 * dt) # Reduced energy drain
        if self.player.energy <= 0:
            self.player.take_damage(1 * dt)

        self._update_enemies(dt)
        self._update_treasures()
