# Dungeon Delver - Python Roguelike Game

A fully-featured turn-based roguelike dungeon crawler written in Python using Pygame.

## Features

### Core Gameplay
- **Turn-based combat system** with tactical decision-making
- **Procedural dungeon generation** with multiple levels
- **Character progression** with experience points and leveling
- **Multiple enemy types** with unique AI behaviors
- **Weapon system** with different types and rarity levels
- **Inventory management** with stackable items and equipment

### Character System
- **Three main attributes**: Strength, Dexterity, Intelligence
- **Health and Mana systems** with potions and regeneration
- **Skill point allocation** for customizing your character
- **Equipment slots** for weapons, armor, and accessories

### Combat Mechanics
- **Critical hit system** based on dexterity and weapon properties
- **Damage reduction** from armor and defense stats
- **Dodge and block mechanics** for avoiding damage
- **Special enemy abilities** like dragon fire breath and orc berserker rage

### Items and Equipment
- **Weapon types**: Swords, Axes, Bows, Staves, Daggers
- **Rarity system**: Common, Uncommon, Rare, Epic, Legendary
- **Consumables**: Health potions, Mana potions, Food, Scrolls
- **Valuables**: Gold coins, Gems, Keys
- **Durability system** for weapons

### Dungeon Exploration
- **Room-based dungeon generation** with corridors
- **Fog of war** system for exploration
- **Minimap** for navigation
- **Multiple dungeon levels** with increasing difficulty
- **Treasure rooms** with valuable items

## Controls

- **Arrow Keys**: Move character
- **I**: Open/close inventory
- **Space**: Wait a turn / Confirm action
- **ESC**: Pause game / Close menus
- **Mouse**: Click on items and UI elements

## Installation

1. Install Python 3.7 or higher
2. Install Pygame: `pip install pygame`
3. Run the game: `python main.py`

## Game Structure

```
dungeon_delver/
├── main.py              # Game entry point
├── game.py              # Main game loop and state management
├── config.py            # Game configuration and constants
├── player.py            # Player character class
├── enemy.py             # Enemy AI and combat
├── weapon.py            # Weapon system and generation
├── item.py              # Item types and factory
├── inventory.py         # Inventory management
├── dungeon.py           # Dungeon generation and tiles
├── combat.py            # Combat system and calculations
├── ui.py                # User interface rendering
├── utils.py             # Utility classes and functions
└── README.md            # This file
```

## Game Design

### Combat System
The combat system features tactical turn-based battles where positioning, equipment choice, and resource management matter. Each attack has a chance to hit based on dexterity, with critical hits dealing bonus damage. Enemies have different AI behaviors and special abilities.

### Progression System
Characters gain experience by defeating enemies and can level up to increase their stats. Each level provides skill points that can be allocated to improve attributes. Equipment found in the dungeon provides significant power increases.

### Dungeon Generation
The dungeon is procedurally generated with interconnected rooms, corridors, and special areas. Each level increases in difficulty with stronger enemies and better rewards. The fog of war system encourages careful exploration.

### Item System
Items have different rarities with increasing power and special effects. Weapons can have elemental damage, life steal, and other magical properties. Consumables provide tactical options during combat and exploration.

## Technical Details

- **Graphics**: Uses Pygame for 2D rendering with tile-based graphics
- **Architecture**: Object-oriented design with separate systems for different game aspects
- **Data Management**: JSON-compatible save system (not implemented in this version)
- **Performance**: Efficient rendering with viewport culling and optimized tile updates

## Future Enhancements

- Save/load functionality
- More enemy types and AI behaviors
- Additional dungeon features (traps, puzzles, secrets)
- Magic system with spells and abilities
- Crafting system for item upgrades
- More weapon types and special effects
- Sound effects and music
- Character classes and skill trees

## Contributing

This is a learning project demonstrating roguelike game development in Python. Feel free to use the code as a reference for your own projects.

## License

This project is open source and available under the MIT License.