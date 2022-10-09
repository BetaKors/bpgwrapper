# TODO: split this file and put classes in separate files in a renderables folder

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass, field
from typing import TYPE_CHECKING, Callable, Literal, Optional, Tuple, final
from bisect import insort

from pygame import gfxdraw
from pygame.color import Color
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from .utils import vec2_to_int_tuple

if TYPE_CHECKING:
    from .game import Game


# this class isn't supposed to be instanced, but mypy apparently thinks it is
@dataclass  # type: ignore
class Renderable(ABC):
    _game: 'Game'
    _always_render: bool = field(default=False, init=False)
    layer: float = field(default=1, init=False)

    @property
    def always_render(self) -> bool:
        return self._always_render

    @always_render.setter
    def always_render(self, value: bool) -> None:
        if value:
            self.render()
        else:
            # consider the following code:
            #    renderable = SomeRenderable(game, Vector2(0, 0))
            #    renderable.always_render = True
            #    renderable.always_render = False
            # this would cause `renderable` to be rendered once, since when `always_render` is set
            # to `True` we add the renderable in questionto the list of renderables to be rendered.
            # as such, we must remove it if always_render is set to false.
            self.cancel_rendering()

        self._always_render = value

    @final
    def render(self) -> None:
        # if we didn't check for always_render and it was true, we would be adding this renderable
        # again to the list of renderables, and it would never be removed because of always_render
        # so each frame (if this was being called on some renderable on some component's update)
        # we would be adding this object again and again to the list of renderables, which would
        # lag the game, obviously
        if not self.always_render:
            insort(self._game.rendering.renderables, self, key=lambda r: r.layer)

    @final
    def cancel_rendering(self) -> None:
        if self in self._game.rendering.renderables:
            self._game.rendering.renderables.remove(self)

    @abstractmethod
    def draw(self) -> None:
        raise NotImplementedError()


@dataclass
class Circle(Renderable):
    pos: Vector2
    radius: float
    fill_color: Optional[Color]
    stroke_color: Optional[Color] = None
    _: KW_ONLY
    antialiasing: bool = True
    stroke_mode: Literal['inside', 'outside'] = 'inside'
    _use_aaellipse_for_aa: bool = field(default=True, init=False)

    @property
    def pixel_pos(self) -> Tuple[int, int]:
        return vec2_to_int_tuple(
            self._game.camera.world_to_pixel_pos(self.pos)
        )

    @property
    def pixel_radius(self) -> int:
        return int(self._game.camera.world_to_pixel_scale(self.radius))

    def draw(self) -> None:
        # just so we don't have to keep doing the calculations everytime we cache this stuff
        pixel_pos = self.pixel_pos
        pixel_radius = self.pixel_radius

        if self.fill_color is not None:
            gfxdraw.filled_circle(
                self._game.window.surface,
                *pixel_pos,
                pixel_radius,
                self.fill_color
            )

            if self.antialiasing and self.stroke_color is None:
                # gfxdraw.filled_circle isn't antialiased, so we do this to apply antialiasing.
                # we don't have to do this if there's a stroke_color because it's gonna be done
                # if there is one.
                # we also have to use an ellipse here because apparently gfxdraw's aacircle and
                # filled_circle draw circles differently, and simply using aacircle here would
                # cause the poles of the circle to be antialiased and the sides not.
                # to mitigate this, we make the radius of the ellipse in the x axis just a little
                # bigger.
                # this *will* cause holes, and will cause smaller circles to look elliptical in
                # the x axis.
                # because of this behaviour, this can be switched off using `_use_aaellipse_for_aa`.
                self._draw_aa(pixel_pos, pixel_radius, self.fill_color)

        if self.stroke_color is not None:
            if self.antialiasing:
                self._draw_aa(pixel_pos, pixel_radius, self.stroke_color)
            else:
                # this uses the same tecnique as the antialiasing thing to draw the border outside
                # of the circle instead of inside, but we change the drawing methods used so as to
                # not apply antialising (that's what `ellipse_func` and `circle_func` do).
                # for the same reasons stated above, just drawing a circle with a radius one unit
                # larger to draw the stroke wouldn't work as expected, so we have to do this.
                self._conditionally_draw_circle_or_ellipse(
                    pixel_pos,
                    pixel_radius,
                    self.stroke_color,
                    self.stroke_mode == 'outside',
                    ellipse_func=gfxdraw.ellipse,
                    circle_func=gfxdraw.circle
                )

    def _draw_aa(self, pos: Tuple[int, int], radius: int, color: Color) -> None:
        self._conditionally_draw_circle_or_ellipse(pos, radius, color, self._use_aaellipse_for_aa)

    # the only reason why this method takes position and radius as parameters is because we cache
    # at the beggining of the draw method, and as since they're local variables they have to be
    # passed as arguments here.
    # TODO: perhaps calculating that kinda stuff and caching it on a per-frame basis can solve
    # this, making so that when we use the property `pixel_pos` or `pixel_radius` more than once
    # in one frame, we get a cached value.
    def _conditionally_draw_circle_or_ellipse(
        self,
        pos: Tuple[int, int],
        radius: int,
        color: Color,
        flag: bool,
        *,
        ellipse_func: Callable[[Surface, int, int, int, int, Color], None] = gfxdraw.aaellipse,
        circle_func: Callable[[Surface, int, int, int, Color], None] = gfxdraw.aacircle
    ) -> None:
        if flag:
            ellipse_func(
                self._game.window.surface,
                *pos,
                radius + 1,
                radius,
                color
            )
        else:
            circle_func(
                self._game.window.surface,
                *pos,
                radius,
                color
            )


@dataclass
class Rectangle(Renderable):
    pos: Vector2
    width: float
    height: float
    fill_color: Optional[Color]
    stroke_color: Optional[Color] = None
    _: KW_ONLY
    rect_mode: Literal['center', 'top_right'] = 'center'
    stroke_mode: Literal['inside', 'outside'] = 'inside'

    @property
    def pixel_pos(self) -> Tuple[int, int]:
        return vec2_to_int_tuple(
            self._game.camera.world_to_pixel_pos(self.pos)
        )

    @property
    def pixel_size(self) -> Tuple[int, int]:
        return vec2_to_int_tuple((
            self._game.camera.world_to_pixel_scale(self.width),
            self._game.camera.world_to_pixel_scale(self.height)
        ))

    # no reason to cache `pixel_pos` and `pixel_size` here because they're only ever used once
    def draw(self) -> None:
        if self.rect_mode == 'center':
            rect = Rect(0, 0, *self.pixel_size)
            rect.center = self.pixel_pos
        else:
            rect = Rect(*self.pixel_pos, *self.pixel_size)

        if self.fill_color is not None:
            points = [
                rect.topleft,
                rect.topright,
                rect.bottomright,
                rect.bottomleft,
            ]

            gfxdraw.filled_polygon(
                self._game.window.surface,
                points,
                self.fill_color
            )

        if self.stroke_color is not None:
            if self.stroke_mode == 'inside':
                rect.width += 1
                rect.height += 1
            else:
                rect.x -= 1
                rect.y -= 1
                rect.width += 3
                rect.height += 3

            gfxdraw.rectangle(
                self._game.window.surface,
                rect,
                self.stroke_color
            )
