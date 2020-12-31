from .settings import settings


class CustomizableMixin:
    """A minx-in to add a classmethod ``custom`` to any class."""

    @classmethod
    def custom(cls, **kwargs):
        """Returns a subclass with all passed kwargs set as class attributes."""
        return type(f"Custom{cls.__name__}", (cls,), kwargs)


def get_result_path(board, module_class):
    return (settings.result_path / str(board) / module_class.__name__ / cls._hash).resolve()


def get_build_path():
    return (settings.build_path).resolve()
