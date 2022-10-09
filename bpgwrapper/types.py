from typing import Generator, Optional
from .yieldables import Yieldable


# is this the correct term? i mean thats what unity calls them
Coroutine = Generator[Optional[Yieldable], None, None]
