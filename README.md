# Python 3D Roguelike

This project is a compact first-person 3D roguelike built with Python and pyglet. The world, rooms, and textures are generated procedurally at startup. Move through the dungeon, evade hazards, and fight roaming enemies while collecting treasure.

## Features
- Fully procedural dungeon layout with layered noise-based textures for floors, walls, and props.
- Keyboard and mouse controls for first-person navigation.
- Simple enemy AI that patrols and reacts to the player.
- HUD that shows health, energy, and contextual prompts.

## Controls
- **W/S**: Move forward/backward
- **A/D**: Strafe left/right
- **Mouse**: Look around
- **Space**: Attack
- **E**: Interact/open treasures
- **Escape**: Quit

## Running
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the game:
   ```bash
   python -m roguelike3d
   ```

The game opens in a window with the mouse captured. Press **Escape** to exit.
