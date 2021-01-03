import shutil
from .settings import settings


class CustomizableMixin:
    """A minx-in to add a classmethod ``custom`` to any class."""

    @classmethod
    def custom(cls, **kwargs):
        """Returns a subclass with all passed kwargs set as class attributes."""
        return type(f"Custom{cls.__name__}", (cls,), kwargs)


def empty_path(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)

