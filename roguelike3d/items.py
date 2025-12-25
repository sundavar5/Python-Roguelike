from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Item:
    name: str
    count: int = 1

@dataclass
class Weapon(Item):
    damage: float = 10.0
    range: float = 1.5
    cooldown: float = 0.5
    count: int = 1

@dataclass
class Resource(Item):
    pass
