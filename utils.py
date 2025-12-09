"""
Utility classes and functions
"""

import math
import random
from typing import List, Tuple, Optional

class Vector2:
    """2D vector class for positions and movement"""
    
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    
    @property
    def magnitude(self) -> float:
        """Get the magnitude (length) of the vector"""
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    @property
    def normalized(self) -> 'Vector2':
        """Get the normalized vector (unit vector)"""
        mag = self.magnitude
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)
    
    def distance_to(self, other: 'Vector2') -> float:
        """Calculate distance to another vector"""
        return (self - other).magnitude
    
    def manhattan_distance(self, other: 'Vector2') -> float:
        """Calculate Manhattan distance to another vector"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def copy(self) -> 'Vector2':
        """Create a copy of this vector"""
        return Vector2(self.x, self.y)

class Rect:
    """Rectangle class for rooms and areas"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    @property
    def left(self) -> int:
        return self.x
    
    @property
    def right(self) -> int:
        return self.x + self.width
    
    @property
    def top(self) -> int:
        return self.y
    
    @property
    def bottom(self) -> int:
        return self.y + self.height
    
    @property
    def center(self) -> Vector2:
        return Vector2(self.x + self.width // 2, self.y + self.height // 2)
    
    def intersects(self, other: 'Rect') -> bool:
        """Check if this rectangle intersects with another"""
        return not (
            self.right <= other.left or
            self.left >= other.right or
            self.bottom <= other.top or
            self.top >= other.bottom
        )
    
    def contains(self, point: Vector2) -> bool:
        """Check if the rectangle contains a point"""
        return (
            self.left <= point.x < self.right and
            self.top <= point.y < self.bottom
        )

class Dice:
    """Dice roller for random number generation"""
    
    @staticmethod
    def roll(sides: int = 6) -> int:
        """Roll a single die with the given number of sides"""
        return random.randint(1, sides)
    
    @staticmethod
    def roll_multiple(count: int, sides: int = 6) -> int:
        """Roll multiple dice and sum the results"""
        return sum(Dice.roll(sides) for _ in range(count))
    
    @staticmethod
    def roll_range(min_val: int, max_val: int) -> int:
        """Roll a random number in the given range (inclusive)"""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def choice(sequence):
        """Choose a random element from a sequence"""
        return random.choice(sequence)
    
    @staticmethod
    def sample(sequence, k):
        """Choose k unique random elements from a sequence"""
        return random.sample(sequence, k)
    
    @staticmethod
    def roll_dice_notation(dice_str: str) -> int:
        """Roll dice using notation like '2d6+3' or '1d20'"""
        try:
            if '+' in dice_str:
                dice_part, modifier = dice_str.split('+')
                modifier = int(modifier)
            elif '-' in dice_str:
                dice_part, modifier = dice_str.split('-')
                modifier = -int(modifier)
            else:
                dice_part = dice_str
                modifier = 0
            
            if 'd' in dice_part:
                count, sides = dice_part.split('d')
                count = int(count) if count else 1
                sides = int(sides)
                return Dice.roll_multiple(count, sides) + modifier
            else:
                return int(dice_part)
        except:
            return 0

class RandomUtils:
    """Utility functions for random generation"""
    
    @staticmethod
    def choice_weighted(choices: List[Tuple[str, float]]) -> str:
        """Make a weighted random choice from a list of (item, weight) tuples"""
        total_weight = sum(weight for _, weight in choices)
        r = random.uniform(0, total_weight)
        
        current_weight = 0
        for item, weight in choices:
            current_weight += weight
            if r <= current_weight:
                return item
        
        return choices[-1][0] if choices else None
    
    @staticmethod
    def random_direction() -> Vector2:
        """Get a random direction vector"""
        directions = [
            Vector2(0, -1),   # Up
            Vector2(0, 1),    # Down
            Vector2(-1, 0),   # Left
            Vector2(1, 0),    # Right
            Vector2(-1, -1),  # Up-left
            Vector2(1, -1),   # Up-right
            Vector2(-1, 1),   # Down-left
            Vector2(1, 1)     # Down-right
        ]
        return random.choice(directions)
    
    @staticmethod
    def random_in_circle(center: Vector2, radius: float) -> Vector2:
        """Get a random point within a circle"""
        angle = random.uniform(0, 2 * math.pi)
        r = radius * math.sqrt(random.uniform(0, 1))
        return Vector2(
            center.x + r * math.cos(angle),
            center.y + r * math.sin(angle)
        )

class MathUtils:
    """Mathematical utility functions"""
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp a value between min and max"""
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """Linear interpolation between a and b"""
        return a + (b - a) * MathUtils.clamp(t, 0, 1)
    
    @staticmethod
    def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
        """Map a value from one range to another"""
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    @staticmethod
    def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
        """Calculate Manhattan distance between two points"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    @staticmethod
    def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

class ColorUtils:
    """Color manipulation utilities"""
    
    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """Interpolate between two colors"""
        t = MathUtils.clamp(t, 0, 1)
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )
    
    @staticmethod
    def brighten_color(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Brighten a color by a given factor"""
        return (
            min(255, int(color[0] * (1 + factor))),
            min(255, int(color[1] * (1 + factor))),
            min(255, int(color[2] * (1 + factor)))
        )
    
    @staticmethod
    def darken_color(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Darken a color by a given factor"""
        return (
            int(color[0] * (1 - factor)),
            int(color[1] * (1 - factor)),
            int(color[2] * (1 - factor))
        )

class TextUtils:
    """Text manipulation utilities"""
    
    @staticmethod
    def wrap_text(text: str, max_width: int, font) -> List[str]:
        """Wrap text to fit within a given width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    @staticmethod
    def truncate_text(text: str, max_width: int, font) -> str:
        """Truncate text with ellipsis if it's too long"""
        if font.size(text)[0] <= max_width:
            return text
        
        ellipsis = "..."
        while text and font.size(text + ellipsis)[0] > max_width:
            text = text[:-1]
        
        return text + ellipsis if text else ellipsis