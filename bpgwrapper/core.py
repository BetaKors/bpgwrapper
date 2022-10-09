from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game


class System:
    def __init__(self, game: 'Game') -> None:
        self._game = game
        self._game.systems.append(self)

    def update(self) -> None:
        pass

    def post_update(self) -> None:
        pass


class Component(ABC):
    def __init__(self, game: 'Game') -> None:
        self._game = game

    @abstractmethod
    def update(self) -> None:
        pass

    def should_remove(self) -> bool:
        pass
