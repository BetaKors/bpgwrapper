from abc import ABC
from typing import Any, Callable, Generic, TypeVar


EH = TypeVar('EH', bound=Callable[..., None])
NoArgEvent = Callable[[], None]
EventSelf = TypeVar('EventSelf', bound='Event[Any]')


class Event(ABC, Generic[EH]):
    def __init__(self) -> None:
        self._handlers: set[EH] = set()

    def __iadd__(self: EventSelf, handler: EH) -> EventSelf:
        """
        Adds a handler to this `Event`'s set of handlers.
        """
        self._handlers.add(handler)
        return self

    def __isub__(self: EventSelf, handler: EH) -> EventSelf:
        """
        Removes a handler from this `Event`'s set of handlers.\n
        Doesn't raise exception if handler is not found.
        """
        self._handlers.discard(handler)
        return self

    # should this really be called a decorator?
    # i mean it works like one but it doesn't actually decorate `func` it simply adds it to a set.
    def __call__(self, func: EH) -> EH:
        """
        Allows `Event` instances to be used as decorators.\n
        Adds the decorated `func` to the set of handlers, and returns it.

        Parameters
        ----------
        func : `EH`
            The callable being decorated, that will be added to the set of event handlers.

        Returns
        -------
        `EH`
            The callable that was decorated.
        """
        self += func
        return func

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({len(self._handlers)} handlers)'

    def invoke(self, *args: Any, **kwargs: Any) -> None:
        """
        Invokes this `Event`.
        """
        for handler in self._handlers:
            handler(*args, **kwargs)

    def clear(self) -> None:
        """
        Clears all handlers attached to this `Event`.
        """
        self._handlers.clear()
