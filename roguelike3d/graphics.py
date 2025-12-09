from __future__ import annotations

from typing import Tuple

import pyglet

Vec3 = Tuple[float, float, float]


def draw_cube(position: Vec3, size: float, texture: pyglet.image.Texture) -> None:
    x, y, z = position
    s = size
    gl = pyglet.gl
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)
    gl.glBegin(gl.GL_QUADS)

    # Front
    gl.glTexCoord2f(0, 0); gl.glVertex3f(x - s, y - s, z + s)
    gl.glTexCoord2f(1, 0); gl.glVertex3f(x + s, y - s, z + s)
    gl.glTexCoord2f(1, 1); gl.glVertex3f(x + s, y + s, z + s)
    gl.glTexCoord2f(0, 1); gl.glVertex3f(x - s, y + s, z + s)

    # Back
    gl.glTexCoord2f(0, 0); gl.glVertex3f(x + s, y - s, z - s)
    gl.glTexCoord2f(1, 0); gl.glVertex3f(x - s, y - s, z - s)
    gl.glTexCoord2f(1, 1); gl.glVertex3f(x - s, y + s, z - s)
    gl.glTexCoord2f(0, 1); gl.glVertex3f(x + s, y + s, z - s)

    # Left
    gl.glTexCoord2f(0, 0); gl.glVertex3f(x - s, y - s, z - s)
    gl.glTexCoord2f(1, 0); gl.glVertex3f(x - s, y - s, z + s)
    gl.glTexCoord2f(1, 1); gl.glVertex3f(x - s, y + s, z + s)
    gl.glTexCoord2f(0, 1); gl.glVertex3f(x - s, y + s, z - s)

    # Right
    gl.glTexCoord2f(0, 0); gl.glVertex3f(x + s, y - s, z + s)
    gl.glTexCoord2f(1, 0); gl.glVertex3f(x + s, y - s, z - s)
    gl.glTexCoord2f(1, 1); gl.glVertex3f(x + s, y + s, z - s)
    gl.glTexCoord2f(0, 1); gl.glVertex3f(x + s, y + s, z + s)

    # Top
    gl.glTexCoord2f(0, 0); gl.glVertex3f(x - s, y + s, z + s)
    gl.glTexCoord2f(1, 0); gl.glVertex3f(x + s, y + s, z + s)
    gl.glTexCoord2f(1, 1); gl.glVertex3f(x + s, y + s, z - s)
    gl.glTexCoord2f(0, 1); gl.glVertex3f(x - s, y + s, z - s)

    # Bottom
    gl.glTexCoord2f(0, 0); gl.glVertex3f(x - s, y - s, z - s)
    gl.glTexCoord2f(1, 0); gl.glVertex3f(x + s, y - s, z - s)
    gl.glTexCoord2f(1, 1); gl.glVertex3f(x + s, y - s, z + s)
    gl.glTexCoord2f(0, 1); gl.glVertex3f(x - s, y - s, z + s)

    gl.glEnd()
