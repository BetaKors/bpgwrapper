from typing import TYPE_CHECKING

from ..core import System
from ..event import Event, NoArgEvent
from ..renderables import Renderable
from ..utils import filter_by_attrs

if TYPE_CHECKING:
    from ..game import Game


class Rendering(System):
    def __init__(self, game: 'Game') -> None:
        super().__init__(game)

        self.renderables: list[Renderable] = []

        self.before_render = Event[NoArgEvent]()
        self.on_render = Event[NoArgEvent]()

    def post_update(self) -> None:
        self.before_render.invoke()

        for renderable in self.renderables:
            renderable.draw()
        
        self.on_render.invoke()

        self.renderables = list(filter_by_attrs(self.renderables, always_render=True))
