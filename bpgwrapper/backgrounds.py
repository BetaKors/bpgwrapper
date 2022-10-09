from abc import ABC, abstractmethod
from dataclasses import dataclass

from pygame.color import Color
from pygame.surface import Surface


@dataclass # type: ignore
class Background(ABC):
    surface: Surface

    @abstractmethod
    def draw(self) -> None:
        raise NotImplementedError()


# TODO: rename to solid color background
@dataclass
class ColorBackground(Background):
    color: Color

    def draw(self) -> None:
        self.surface.fill(self.color)


@dataclass
class ImageBackground(Background):
    image: Surface

    def draw(self) -> None:  # TODO: test and add resizing and (possibly optional) resizing-related args
        self.surface.blit(self.image, (0, 0))
