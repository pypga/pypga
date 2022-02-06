import shutil
from typing import Union, Tuple, List

from migen import Constant, Signal

from .settings import settings


class CustomizableMixin:
    """A mix-in to add a classmethod ``custom`` to any class."""

    @classmethod
    def custom(cls, **kwargs):
        """Returns a subclass with all passed kwargs set as class attributes."""
        return type(f"Custom{cls.__name__}", (cls,), kwargs)


def empty_path(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def get_length(signal: Union[Signal, Constant, int]) -> int:
    """Returns the number of bits required to represent the given signal."""
    try:
        length = len(signal)
    except TypeError:
        length = signal.bit_length()
    if length < 1:
        return 1
    else:
        return length


def get_reset_value(signal: Union[Signal, Constant, int]) -> int:
    """Returns the reset value of a signal or constant."""
    try:
        return int(signal.reset.value)
    except AttributeError:
        try:
            return int(signal.value)
        except AttributeError:
            return int(signal)

def get_width_and_depth(data: List[int], width: int = None) -> Tuple[int, int]:
    """Returns the width and depth required to store data."""
    if width is None:
        assert min(data) >= 0
        width = max(data).bit_length()
    return width, len(data)
