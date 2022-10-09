from typing import TYPE_CHECKING, Iterator, Optional

import pygame
from pygame.event import Event

from ..core import System
from ..utils import filter_by_attrs, get_by_attrs

if TYPE_CHECKING:
    from ..game import Game


class Events(System):
    def __init__(self, game: 'Game') -> None:
        super().__init__(game)

        self.events: list[Event] = []

    def update(self) -> None:
        self.events = pygame.event.get()

    def cancel(self, event: Event) -> None:
        """
        Removes all occurances of `event` from the list of events, effectively cancelling it.

        Parameters
        ----------
        event : Event
            _description_
        """
        filtered = self.filter(event)

        self.events = [
            evt
            for evt in self.events
            if evt not in filtered
        ]

    def get(self, event: Event) -> Optional[Event]:
        return get_by_attrs(self.events, type=event)

    def filter(self, event: Event) -> Iterator[Event]:
        return filter_by_attrs(self.events, type=event)

    def list(self, event: Event) -> list[Event]:
        return list(self.filter(event))
