from typing import TYPE_CHECKING, Literal

from pygame.math import Vector2, Vector3

from ..core import System

if TYPE_CHECKING:
    from ..game import Game


PositionType = Literal['world', 'pixel']


class Camera(System):
    def __init__(self, game: 'Game'):
        super().__init__(game)

        self.pos = Vector3(0, 0, 1)

    def pixel_to_world_pos(self, pos: Vector2) -> Vector2:
        """
        Converts a position in pixel units to world units.

        Parameters
        ----------
        pos : `Vector2`
            The position to be converted.

        Returns
        -------
        `Vector2`
            The converted position.
        """
        return self._invert_y(pos - self._game.window.center_pixel_pos) / (self._game.window.size // 10).x + self.pos.xy

    def pixel_to_world_scale(self, scale: float) -> float:
        """
        Converts a scale in pixel units to world units.

        Parameters
        ----------
        scale : `float`
            The scale to be converted.

        Returns
        -------
        `float`
            The converted scale.
        """
        return scale / self.pos.z / 10 / (self._game.window.size // 200).x

    def world_to_pixel_pos(self, pos: Vector2) -> Vector2:
        """
        Converts a scale in world units to pixel units.

        Parameters
        ----------
        pos : `Vector2`
            The position to be converted.

        Returns
        -------
        `Vector2`
            The converted position.
        """
        return self._invert_y(pos - self.pos.xy) * (self._game.window.size // 10).x + self._game.window.center_pixel_pos

    def world_to_pixel_scale(self, scale: float) -> float:
        """
        Converts a scale in world units to pixel units.

        Parameters
        ----------
        scale : `float`
            The scale to be converted.

        Returns
        -------
        `float`
            The converted scale.
        """
        return scale * self.pos.z * 10 * (self._game.window.size // 200).x

    def is_circle_visible(self, pos: Vector2, radius: float, pos_type: PositionType='pixel') -> bool:
        """
        Checks whether or not a circle is visible, i.e. inside the screen.

        Parameters
        ----------
        pos : `Vector2`
            The circle's position
        radius : `float`
            The circle's radius
        pos_type : `PositionType, optional`
            A `str` containing the type of position being used.
            Either `world` or `pixel`, with the latter being used by default.

        Returns
        -------
        `bool`
            Whether or not the circle is visible.
        """
        window_size = self._game.window.size

        if pos_type == 'world':
            pos = self.world_to_pixel_pos(pos)
            radius = self.world_to_pixel_scale(radius)

        # horizontal visibility
        hv = pos.x > -radius and pos.x < window_size.x + radius
        # vertical visibility
        vv = pos.y > -radius and pos.y < window_size.y + radius

        return hv and vv

    def is_point_visible(self, pos: Vector2, pos_type: PositionType='pixel') -> bool:
        """
        Whether or not a point is inside the screen.

        Parameters
        ----------
        pos : `Vector2`
            The position of the point.
        pos_type : `PositionType, optional`
            A `str` containing the type of position being used.
            Either `world` or `pixel`, with the latter being used by default.

        Returns
        -------
        `bool`
            Whether or not the point is inside the screen.
        """
        return self.is_circle_visible(pos, 0, pos_type)

    def _invert_y(self, v: Vector2) -> Vector2:
        """
        Simply inverts the `y` component of a `Vector2`.\n
        In the context of this class, this is responsible
        for inverting the y axis of the world, since pixel
        coordinates use positive downwards, with [0, 0] being
        the top left of the window.

        Parameters
        ----------
        v : `Vector2`
            The `Vector2` in question.

        Returns
        -------
        `Vector2`
            The same exact `Vector2`, except that it has its `y` component inverted.
        """
        return Vector2(v.x, -v.y)
