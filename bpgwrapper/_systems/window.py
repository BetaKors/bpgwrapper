from ctypes import byref, windll
from ctypes.wintypes import RECT as cRect
from glob import glob
from pathlib import Path
from random import uniform
from typing import TYPE_CHECKING, Literal, Optional

import pygame
from pygame.color import Color
from pygame.math import Vector2
from pygame.surface import Surface

from ..backgrounds import Background, ColorBackground
from ..core import System
from ..utils import vec2_to_int_tuple
from ..event import Event, NoArgEvent

if TYPE_CHECKING:
    from ..game import Game


class Window(System):
    def __init__(self, game: 'Game') -> None:
        super().__init__(game)

        self.monitor_index = 0
        self.monitor_size = Vector2(pygame.display.get_desktop_sizes()[self.monitor_index])  # type: ignore

        self.windowed_size = self.monitor_size // 2
        self._fullscreen_size = self.monitor_size
        self._size = self.windowed_size

        self.windowed_screen_pos = self.monitor_size // 2 - self.windowed_size // 2
        ## TODO: test this with changing windowed size

        self._resizable = True
        self._fullscreen = False

        self.surface = self._setup_window()
        self._hwnd = pygame.display.get_wm_info()['window']

        self.background: Optional[Background] = ColorBackground(self.surface, Color('#FFEECF'))

        self.on_resize = Event[NoArgEvent]()

    @property
    def title(self) -> str:
        return pygame.display.get_caption()[0]

    @title.setter
    def title(self, title: str) -> None:
        pygame.display.set_caption(title)

    @property
    def icon(self) -> Surface:
        return self._icon

    @icon.setter
    def icon(self, icon: Surface) -> None:
        self._icon = icon
        pygame.display.set_icon(icon)

    @property
    def pos(self) -> Vector2:
        rect = cRect()
        windll.user32.GetWindowRect(self._hwnd, byref(rect))
        # wintypes.Rect's members are longs, not ints, so mypy complains
        return Vector2(rect.left, rect.top)  # type: ignore

    @pos.setter
    def pos(self, pos: Vector2) -> None:  # TODO:
        # for some reason setting the size of the window to an exact number will result in the window's
        # actual size being set to that number minus 16 on the x axis and 39 on the y axis.
        # no clue if this only happens in my machine but i'll offset self.size by that amount to
        # counteract that
        windll.user32.MoveWindow(
            self._hwnd,
            *vec2_to_int_tuple(pos),
            *vec2_to_int_tuple(self.size + Vector2(16, 39))
        )

    @property
    def size(self) -> Vector2:
        return self._size

    @size.setter
    def size(self, size: Vector2) -> None:
        self._size = size
        self.surface = self._set_mode_with_resizable(size)
        # apparently a WINDOWRESIZED event is not fired when `set_mode` is called so we have
        # to do this manually
        self.on_resize.invoke()

    @property
    def fullscreen(self) -> bool:
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, fullscreen: bool) -> None:
        self._fullscreen = fullscreen
        self.pos = Vector2(-8, -31) if fullscreen else self.windowed_screen_pos
        self.size = self._fullscreen_size if fullscreen else self.windowed_size

    @property
    def resizable(self) -> bool:
        return self._resizable

    @resizable.setter
    def resizable(self, value: bool) -> None:
        self._resizable = value
        self.surface = self._set_mode_with_resizable(self.size)

    @property
    def center(self) -> Vector2:
        return self._game.camera.pixel_to_world_pos(self.center_pixel_pos)

    @property
    def center_pixel_pos(self) -> Vector2:
        return self.size // 2

    @property
    def top_left(self) -> Vector2:
        return self._game.camera.pixel_to_world_pos(self.top_left_pixel_pos)

    @property
    def top_left_pixel_pos(self) -> Vector2:
        return Vector2()

    @property
    def bottom_right(self) -> Vector2:
        return self._game.camera.pixel_to_world_pos(self.bottom_right_pixel_pos)

    @property
    def bottom_right_pixel_pos(self) -> Vector2:
        return self.size

    def update(self) -> None:
        if self.background is not None:
            self.background.draw()

        if self._game.events.get(pygame.WINDOWRESIZED):
            self.on_resize.invoke()
            self._size = Vector2(pygame.display.get_window_size())

    def post_update(self) -> None:
        pygame.display.update()

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen

    def screenshot(
            self,
            path: Path | str, *,
            existance_handling: Literal['replace', 'error', 'count']='replace',
            count_separator: str='-'
        ) -> None:
        if not isinstance(path, Path):
            path = Path(path)

        has_directories = path.parent.name != ''

        if has_directories:
            path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            match existance_handling:  # replace is not handled since it is the default behaviour
                case 'error':
                    raise FileExistsError(f'Saving screenshot with path "{path}" failed since it already exists!')
                case 'count':
                    ext = path.suffix
                    pathstr = str(path).replace(ext, '')

                    count = len(glob(f'{pathstr}{count_separator}*{ext}'))

                    path = f'{pathstr}{count_separator}{count + 1}{ext}'

        pygame.image.save(self.surface, path)

    def random_position(self, unit: Literal['world', 'pixel']='world') -> Vector2:
        if unit == 'world':
            return Vector2(
                uniform(self.top_left.x, self.bottom_right.x),
                uniform(self.top_left.y, self.bottom_right.y)
            )
        else:
            return Vector2(
                uniform(self.top_left_pixel_pos.x, self.bottom_right_pixel_pos.x),
                uniform(self.top_left_pixel_pos.y, self.bottom_right_pixel_pos.y)
            )

    def _set_mode_with_resizable(self, size: Vector2) -> Surface:
        if self.resizable:
            return pygame.display.set_mode(size, pygame.RESIZABLE)

        return pygame.display.set_mode(size)

    def _setup_window(self) -> Surface:
        from pathlib import Path

        pygame.display.set_caption(Path().absolute().name)

        return self._set_mode_with_resizable(self.size)
