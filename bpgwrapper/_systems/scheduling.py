from typing import TYPE_CHECKING

from ..core import System
from ..types import Coroutine
from ..yieldables import WaitForFrames, Yieldable

if TYPE_CHECKING:
    from ..game import Game


class Scheduling(System):
    def __init__(self, game: 'Game') -> None:
        super().__init__(game)

        self._coroutines: dict[Coroutine, Yieldable] = {}

    def start_coroutine(self, func: Coroutine) -> None:
        self._coroutines[func] = self._get_next(func)

    def stop_coroutine(self, func: Coroutine) -> None:
        self._coroutines.pop(func)

    def update(self) -> None:
        for coroutine, yieldable in list(self._coroutines.items()):
            if yieldable.is_ready():
                try:
                    self._coroutines[coroutine] = self._get_next(coroutine)
                except StopIteration:
                    self.stop_coroutine(coroutine)

    def _get_next(self, func: Coroutine) -> Yieldable:
        n = next(func)
        return n if n is not None else WaitForFrames(self._game, 1)
