import logging
from .register import Register
from .logic_function import is_logic


logger = logging.getLogger(__name__)


class Module:
    name = "top"

    def __set_name__(self, owner, name):
        if self.name == self.__class__.name:
            self.name = name
        self.owner = owner

    def __new__(cls, *args, **kwargs):
        logger.info(f"Running {cls.__name__}.__new__(*{args}, **{kwargs}).")
        # TODO: create descriptors for registers
        return super().__new__(cls)

    def _set_register(self, name, value, register=None):
        logger.debug(f"Setting register {self.name}/{name} = {hex(value)} (register={register})")

    def _get_register(self, name, register=None):
        logger.debug(f"reading register {self.name}/{name} (register={register})")
        return name
