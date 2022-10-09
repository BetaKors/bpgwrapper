from random import randint
from typing import Any, Iterable, Iterator, Optional, Tuple, TypeVar

from pygame.color import Color
from pygame.math import Vector2

T = TypeVar('T')


def get_by_attrs(iterable: Iterable[T], **attrs: Any) -> Optional[T]:
    """
    Gets an element from an `Iterable` based on the specified attributes and values of those attributes.\n

    >>> people = [Person('Lucas', age=14), Person('Marcus', age=51), Person('Mary', age=23)]
    >>> aged_twenty_three = get(people, age=23)
    Person('Mary', age=23)

    Parameters
    ----------
    iterable : `Iterable[T]`
        The iterable to get an element from.

    Returns
    -------
    `Optional[T]`
        The element found. Or `None`, if no elements with matching attributes was found.

    Raises
    ------
    `AttributeError`
        If an attribute wasn't found in an object of the iterable.
    """
    return next(filter_by_attrs(iterable, **attrs), None)


def filter_by_attrs(iterable: Iterable[T], **attrs: Any) -> Iterator[T]:
    """
    Filters an `Iterable` based on the specified attributes and values of those attributes.\n

    Parameters
    ----------
    iterable : `Iterable[T]`
        The `Iterable` to be filtered.

    Returns
    -------
    `Iterable[T]`
        The filtered `Iterable`.

    Raises
    ------
    `AttributeError`
        If an attribute wasn't found in an object of the iterable.
    """
    pred = lambda e: all(getattr(e, name) == value for name, value in attrs.items())
    return filter(pred, iterable)


def ilen(iterable: Iterable[Any]) -> int:
    """
    Consumes an `Iterable` and returns its length.

    Parameters
    ----------
    iterable : `Iterable`
        The `Iterable` whose length shall be uncovered.

    Returns
    -------
    `int`
        The length of the `Iterable`.
    """
    return sum(1 for _ in iterable)


def clamp(value: float, min_: float, max_: float) -> float:
    """
    Clamps a value, constraining it to stay within a range of two values.

    Parameters
    ----------
    value : `float`
        The value to be clamped.
    min_ : `float`
        The minimum the value can go.
    max_ : `float`
        The maximum the value can go.

    Returns
    -------
    `float`
        The clamped value.
    """
    return max(min(value, max_), min_)


def remap(n: float, start1: float, stop1: float, start2: float, stop2: float) -> float:
    return ((n - start1) / (stop1 - start1)) * (stop2 - start2) + start2


def vec2_to_int_tuple(pos: Tuple[float, float] | Vector2) -> Tuple[int, int]:
    # mypy doesn't vibe very well with the fact that I'm using `int` as a
    # callable here    
    return tuple(map(int, pos))  # type: ignore


def normalize_vec2_if_possible(vec2: Vector2) -> Vector2:
    if vec2 == Vector2():
        return vec2
    return vec2.normalize()


def random_color(randomize_alpha: bool=False) -> Color:
    color = Color(
        randint(0, 255),
        randint(0, 255),
        randint(0, 255)
    )

    if randomize_alpha:
        color.a = randint(0, 255)

    return color
