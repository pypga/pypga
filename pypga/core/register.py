import logging
from .common import CustomizableMixin

logger = logging.getLogger(__name__)


class Register(CustomizableMixin):
    name: str = None
    size: int = 1
    reset: int = 0
    readable: bool = True
    writable: bool = True

    _SEP = "_"

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = f"{owner.name}{self._SEP}{name}"

    def __get__(self, instance, owner=None):
        logger.debug(f"Reading {self.name} with {instance}/{owner}")
        if instance is None:
            return self
        return instance._get_register(self.name, self)

    def __set__(self, instance, value):
        instance._set_register(self.name, value, self)
