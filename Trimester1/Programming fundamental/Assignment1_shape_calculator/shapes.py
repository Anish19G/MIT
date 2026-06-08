"""Pure calculation functions for shapes.

This module provides small, well-tested functions for common shape
calculations (area, perimeter, surface area) so a CLI or GUI can import
and reuse them.
"""
from __future__ import annotations

import math

__all__ = [
    "rectangle_area",
    "rectangle_perimeter",
    "square_area",
    "square_perimeter",
    "circle_area",
    "circle_circumference",
    "cone_total_surface_area",
    "cone_base_circumference",
    "pyramid_total_surface_area",
    "pyramid_base_perimeter",
    "triangle_area",
    "triangle_perimeter",
]


def rectangle_area(length: float, width: float) -> float:
    """Return the area of a rectangle.

    Args:
        length: Length of the rectangle, must be positive.
        width: Width of the rectangle, must be positive.
    """
    return length * width


def rectangle_perimeter(length: float, width: float) -> float:
    return 2 * (length + width)


def square_area(side: float) -> float:
    return side * side


def square_perimeter(side: float) -> float:
    return 4 * side


def circle_area(radius: float) -> float:
    return math.pi * radius * radius


def circle_circumference(radius: float) -> float:
    return 2 * math.pi * radius


def cone_total_surface_area(radius: float, height: float) -> float:
    """Return total surface area of (right) cone.

    We compute slant height as hypot(radius, height) and use
    area = pi * r * (r + l).
    """
    slant = math.hypot(radius, height)
    return math.pi * radius * (radius + slant)


def cone_base_circumference(radius: float) -> float:
    return circle_circumference(radius)


def pyramid_total_surface_area(base_side: float, height: float) -> float:
    """Assumes square base regular pyramid. Height is the vertical height.

    total area = base_area + 4 * face_area, face_area = (base_side * slant)/2
    where slant = hypot(base_side/2, height)
    """
    base_area = base_side * base_side
    slant = math.hypot(base_side / 2.0, height)
    face_area = (base_side * slant) / 2.0
    return base_area + 4 * face_area


def pyramid_base_perimeter(base_side: float) -> float:
    return 4 * base_side


def triangle_area(base: float, height: float) -> float:
    return 0.5 * base * height


def triangle_perimeter(a: float, b: float, c: float) -> float:
    return a + b + c
