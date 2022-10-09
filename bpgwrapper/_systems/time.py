from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

import pygame

from ..core import System

if TYPE_CHECKING:
    from ..game import Game


class Time(System):
    def __init__(self, game: 'Game') -> None:
        super().__init__(game)

        self.clock = pygame.time.Clock()

        self._deltatime = 0
        self._frame_count = 0
        self._startup_time: Optional[datetime] = None

        self.target_framerate = 60

        self._game.on_start += self._on_start

    @property
    def deltatime(self) -> float:
        return self._deltatime

    @property
    def frame_count(self) -> float:
        return self._frame_count

    @property
    def framerate(self) -> float:
        return self.clock.get_fps()

    # docs: returns none if the game hasn't started
    @property
    def startup_time(self) -> Optional[datetime]:
        return self._startup_time

    # docs: returns none if the game hasn't started
    @property
    def time_since_startup(self) -> Optional[timedelta]:
        if self.startup_time is None:
            return None

        return datetime.now() - self.startup_time

    def _on_start(self) -> None:
        self._startup_time = datetime.now()

    def post_update(self) -> None:
        self._frame_count += 1
        # why is mypy so dumb why cant it see the / 1000 right there what the fu
        self._deltatime = self.clock.tick(0 if self.target_framerate is None else self.target_framerate) / 1000  # type: ignore
