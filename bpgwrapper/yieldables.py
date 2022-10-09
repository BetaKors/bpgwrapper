from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .game import Game


@dataclass  # type: ignore
class Yieldable(ABC):
    _game: 'Game'

    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError()


@dataclass
class WaitForFrames(Yieldable):
    frames: int

    def __post_init__(self) -> None:
        self._ready_frame = self._game.time.frame_count + self.frames

    def is_ready(self) -> bool:
        return self._game.time.frame_count == self._ready_frame


@dataclass
class WaitForSeconds(Yieldable):
    seconds: float

    def __post_init__(self) -> None:
        self._ready_datetime = datetime.now() + timedelta(seconds=self.seconds)

    def is_ready(self) -> bool:
        return datetime.now() >= self._ready_datetime


@dataclass
class WaitUntil(Yieldable):
    func: Callable[[], bool]

    def is_ready(self) -> bool:
        return self.func()
