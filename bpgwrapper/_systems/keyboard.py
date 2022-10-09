from typing import TYPE_CHECKING, Callable, Type

import pygame
from ..core import System
from ..enums import Key, State
from ..event import Event

if TYPE_CHECKING:
    from ..game import Game


StatefulKeyInputEvent = Callable[[Key, State], None]
KeyInputEvent = Callable[[Key], None]


class Keyboard(System):
    def __init__(self, game: 'Game') -> None:
        super().__init__(game)

        self._keys_down: list[Key] = []
        self._keys_up: list[Key] = []
        self._keys_pressed: list[Key] = []

        self.on_key = Event[StatefulKeyInputEvent]()

        self.on_key_down = Event[KeyInputEvent]()
        self.on_key_up = Event[KeyInputEvent]()
        self.on_key_pressed = Event[KeyInputEvent]()

    @property
    def keys_down(self) -> list[Key]:
        return self._keys_down

    @property
    def keys_up(self) -> list[Key]:
        return self._keys_up

    @property
    def keys_pressed(self) -> list[Key]:
        return self._keys_pressed

    def get_key(self, key: Key | str | int, /) -> State:
        key = self._ensure_input_value_is_enum(key, Key)
        return State.from_bools(
            pressed=key in self.keys_pressed,
            up=key in self.keys_up,
            down=key in self.keys_down
        )

    def get_key_pressed(self, key: Key | str | int, /) -> bool:
        return bool(self.get_key(key) & State.pressed)

    def get_key_up(self, key: Key | str | int, /) -> bool:
        return bool(self.get_key(key) & State.up)

    def get_key_down(self, key: Key | str | int, /) -> bool:
        return bool(self.get_key(key) & State.down)

    def any_key(self, state: State=State.none, /) -> bool:
        if state == State.none:
            return bool(self.keys_down + self.keys_up + self.keys_pressed)
        return bool(getattr(self, f'keys_{state.name}'))

    def get_axis(self, negative: Key | str | int, positive: Key | str | int, /) -> float:
        neg = self.get_key_pressed(negative)
        pos = self.get_key_pressed(positive)

        if neg and pos:
            return 0
        if neg:
            return -1
        if pos:
            return 1
        return 0

    def update(self) -> None:
        self._keys_down = [Key(evt.key) for evt in self._game.events.filter(pygame.KEYDOWN)]
        self._keys_up = [Key(evt.key) for evt in self._game.events.filter(pygame.KEYUP)]

        all_keys_pressed = pygame.key.get_pressed()

        self._keys_pressed = list(filter(
            lambda key: all_keys_pressed[key.value],
            Key.__members__.values()
        ))

        if self.any_key():
            for state in [State.down, State.up, State.pressed]:
                for key in getattr(self, f'keys_{state.name}'):
                    self.on_key.invoke(key, state)
                    getattr(self, f'on_key_{state.name}').invoke(key)

    # TODO: remove this from here and mouse, and make this a method of a baseclass for Key and MouseButton
    def _ensure_input_value_is_enum(self, value: Key | str | int, type: Type[Key]) -> Key:
        if isinstance(value, int):
            return type(value)
        if isinstance(value, str):
            return type[value.lower()]
        return value
