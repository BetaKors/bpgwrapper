from typing import Callable, Iterator, Type, TypeVar, cast

import pygame

from ._systems import *
from .core import Component, System
from .event import Event, NoArgEvent


CL = TypeVar('CL', bound=Component)


class Game:
    def __init__(self) -> None:
        pygame.init()

        self.systems: list[System] = []
        self.components: list[Component] = []

        self.on_start = Event[NoArgEvent]()
        self.before_update = Event[NoArgEvent]()
        self.on_update = Event[NoArgEvent]()
        self.on_quit = Event[NoArgEvent]()

        # changing the order of some stuff here will cause problems
        self.time = Time(self)
        self.events = Events(self)
        self.scheduling = Scheduling(self)
        self.mouse = Mouse(self)
        self.keyboard = Keyboard(self)
        self.camera = Camera(self)
        self.rendering = Rendering(self)
        self.window = Window(self)

    def mainloop(self) -> None:
        self.on_start.invoke()

        while not self._should_quit():
            for system in self.systems:
                system.update()

            self.before_update.invoke()

            for component in self.components:
                component.update()

            self.on_update.invoke()

            for system in self.systems:
                system.post_update()

            self._cleanup()

        self.on_quit.invoke()

        pygame.quit()

    def filter_components(self, pred_type_name: Callable[[Component], bool] | Type[CL] | str) -> Iterator[CL]:
        pred: Callable[[Component], bool]

        # why tf is mypy mad
        if isinstance(pred_type_name, type):
            pred = lambda c: isinstance(c, pred_type_name)  # type: ignore

        elif isinstance(pred_type_name, str):
            pred = lambda c: c.__class__.__name__ == pred_type_name

        elif callable(pred_type_name):
            pred = pred_type_name

        return filter(pred, self.components)  # type: ignore

    def add_component(self, component: Type[Component] | Component) -> None:
        if isinstance(component, type):
            component = component(self)

        self.components.append(component)

    def quit(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _should_quit(self) -> bool:
        return cast(bool, self.events.get(pygame.QUIT))

    def _cleanup(self) -> None:
        self.components = [
            component
            for component in self.components
            if not component.should_remove()
        ]
