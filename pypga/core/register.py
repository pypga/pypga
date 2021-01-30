import logging
from .common import CustomizableMixin

logger = logging.getLogger(__name__)


class Register(CustomizableMixin):
    name: str = None
    width: int = 1
    default: int = 0
    readonly: bool = False
    doc: str = ""

    _SEP = "_"

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name

    def _get_full_name(self, instance):
        parents = instance._get_parents()
        return f"{parents[0]}.{'_'.join(parents[1:] + [self.name])}_csr"

    def to_python(self, instance, value):
        return value

    def from_python(self, instance, value):
        value = int(value)
        if value < 0:
            value = 0
            logger.warning(f"Negative saturation of register {self.name}")
        elif value >= (1 << self.width):
            value = (1 << self.width)
            logger.warning(f"Positive saturation of register {self.name}")
        return value

    def __get__(self, instance, owner=None):
        logger.debug(f"Reading {self.name} with {instance}/{owner}")
        if instance is None:
            return self
        value = instance._interface.read(self._get_full_name(instance))
        return self.to_python(instance, value)

    def __set__(self, instance, value):
        if self.readonly:
            raise ValueError(f"The register {self.instance.name}.{self.name} is read-only.")
        value = self.before_from_python(instance, value)
        value = self.from_python(instance, value)
        instance._interface.write(self._get_full_name(instance), value)

    def before_from_python(self, instance, value):
        return value


class BoolRegister(Register):
    invert: bool = False
    bit: int = 0
    width: int = 1

    def to_python(self, instance, value):
        value = Register.to_python(self, instance, value)
        value = bool((value >> self.bit) & 0x1)
        if self.invert:
            value = not value
        return value

    def from_python(self, instance, value):
        if self.invert:
            value = not bool(value)
        value = int(bool(value)) << self.bit
        value = Register.from_python(self, instance, value)
        return value


class NumberRegister(Register):
    signed: bool = False
    min: int = None
    max: int = None

    @property
    def _int_max(self):
        if self.signed:
            return int((1 << (self.width - 1)) - 1)
        else:
            return int((1 << self.width) - 1)

    @property
    def _int_min(self):
        if self.signed:
            return -int(1 << (self.width - 1))
        else:
            return 0

    def to_python(self, instance, value):
        value = Register.to_python(self, instance, value)
        if self.signed and value >= (1 << (self.width - 1)):
            value -= (1 << self.width)
        return int(value)

    def before_from_python(self, instance, value):
        if self.max is not None and value > self.max:
            value = self.max
            logger.warning(f"Positive saturation for {self.name}")
        elif self.min is not None and value < self.min:
            value = self.min
            logger.warning(f"Negative saturation for {self.name}")
        return value

    def from_python(self, instance, value):
        # saturate at the integer level
        if value < self._int_min:
            value = self._int_min
            logger.warning(f"Negative saturation for {self.name}")
        elif value > self._int_max:
            value = self._int_max
            logger.warning(f"Positive saturation for {self.name}")
        if self.signed and value < 0:
            value += (1 << self.width)
        value = Register.from_python(self, instance, value)
        return value


class FixedPointRegister(NumberRegister):
    decimals: int = 0
    min: float = None
    max: float = None

    def to_python(self, instance, value):
        value = NumberRegister.to_python(self, instance, value)
        value = float(value) / (2 ** self.decimals - 1)
        return value

    def from_python(self, instance, value):
        value = int(round(float(value) * (2 ** self.decimals - 1)))
        value = NumberRegister.from_python(self, instance, value)
        return value
