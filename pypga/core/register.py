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
            self.name = name

    def _get_full_name(self, instance):
        parents = instance._get_parents()
        return parents[0] + "." + "_".join(parents[1:] + [self.name])

    def __get__(self, instance, owner=None):
        logger.debug(f"Reading {self.name} with {instance}/{owner}")
        if instance is None:
            return self
        return instance._interface.read(self._get_full_name(instance))

    def __set__(self, instance, value):
        if self.writable:
            instance._interface.write(self._get_full_name(instance), value)
