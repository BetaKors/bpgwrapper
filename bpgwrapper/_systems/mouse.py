from typing import TYPE_CHECKING, Callable, Type

import pygame
from pygame.math import Vector2

from ..core import System
from ..enums import MouseButton, State
from ..event import Event

if TYPE_CHECKING:
    from ..game import Game


StatefulMouseButtonInputEvent = Callable[[MouseButton, State], None]
MouseButtonInputEvent = Callable[[MouseButton], None]


class Mouse(System):
    def __init__(self, game: 'Game') -> None:
        super().__init__(game)

        self.on_button = Event[StatefulMouseButtonInputEvent]()

        self.on_button_down = Event[MouseButtonInputEvent]()
        self.on_button_up = Event[MouseButtonInputEvent]()
        self.on_button_pressed = Event[MouseButtonInputEvent]()

        self._buttons_states = {
            MouseButton.left: State.none,
            MouseButton.middle: State.none,
            MouseButton.right: State.none
        }

        self._pixel_vel = Vector2()

    @property
    def pos(self) -> Vector2:
        return self._game.camera.pixel_to_world_pos(self.pixel_pos)

    @property
    def pixel_pos(self) -> Vector2:
        return Vector2(pygame.mouse.get_pos())

    @property
    def vel(self) -> Vector2:
        return self._game.camera.pixel_to_world_pos(self.pixel_vel)

    @property
    def pixel_vel(self) -> Vector2:
        return self._pixel_vel

    @property
    def scroll_delta(self) -> Vector2:
        # is it even possible to have multiple of these in one frame?
        if evts := self._game.events.list(pygame.MOUSEWHEEL):
            return Vector2(
                sum(evt.x for evt in evts),
                sum(evt.y for evt in evts)
            )
        return Vector2()

    @property
    def buttons_states(self) -> dict[MouseButton, State]:
        return self._buttons_states

    @property
    def visible(self) -> bool:
        return pygame.mouse.get_visible()

    @visible.setter
    def visible(self, value: bool) -> None:
        pygame.mouse.set_visible(value)
    
    def get_button(self, mouse_button: MouseButton | str | int, /) -> State:
        mouse_button = self._ensure_input_value_is_enum(mouse_button, MouseButton)
        return self._buttons_states[mouse_button]

    def get_button_pressed(self, mouse_button: MouseButton | str | int, /) -> bool:
        return bool(self.get_button(mouse_button) & State.pressed)

    def get_button_down(self, mouse_button: MouseButton | str | int, /) -> bool:
        return bool(self.get_button(mouse_button) & State.down)
    
    def get_button_up(self, mouse_button: MouseButton | str | int, /) -> bool:
        return bool(self.get_button(mouse_button) & State.up)

    def any_button(self, state: State=State.none, /) -> bool:
        if state == State.none:
            return any(btn_state != State.none for btn_state in self._buttons_states.values())
        return any(btn_state & state for btn_state in self._buttons_states.values())

    def update(self) -> None:
        all_buttons_pressed = pygame.mouse.get_pressed()

        for btn in MouseButton.__members__.values():
            self._buttons_states[btn] = State.from_bools(
                pressed=all_buttons_pressed[btn.value],
                up=self._is_btn_down_or_up(btn, pygame.MOUSEBUTTONUP),
                down=self._is_btn_down_or_up(btn, pygame.MOUSEBUTTONDOWN)
            )

        if self.any_button():
            for btn, state in self.buttons_states.items():
                if state != State.none:
                    self.on_button.invoke(btn, state)
                    # special case since State.down|pressed can't be grabbed using its name on getattr
                    # (not a problem with the handling of keyboard input since there we loop over each
                    # state individually - except for none - and as such a 'collision' can't happen)
                    if state == State.down | State.pressed:
                        self.on_button_down.invoke(btn)
                        self.on_button_pressed.invoke(btn)
                    else:
                        getattr(self, f'on_button_{state.name}').invoke(btn)

        self._pixel_vel = Vector2(pygame.mouse.get_rel())

    def _ensure_input_value_is_enum(self, value: MouseButton | str | int, type: Type[MouseButton]) -> MouseButton:
        if isinstance(value, int):
            return type(value)
        if isinstance(value, str):
            return type[value.lower()]
        return value

    # idfk what to name this func
    # probably better to define this method outside of update's scope
    # for perfomance reasons (idk probably this wouldn't be the main
    # issue if there are any perf problems with the input system -
    # which is very probable considering we do a lotta stuff here
    # to make it as flexible as possible)
    def _is_btn_down_or_up(self, btn: MouseButton, type: pygame.event.Event) -> bool:
        if evt := self._game.events.get(type):
            return evt.button - 1 == btn.value  # type: ignore
        return False
