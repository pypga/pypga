import functools
import logging
import typing
from typing import Callable

from .builder import get_builder
from .interface import LocalInterface, RemoteInterface
from .logic_function import is_logic
from .register import _Register

logger = logging.getLogger(__name__)


def scan_module_class(module_class) -> typing.Tuple[dict, dict, dict, dict]:
    """
    Returns all pypga objects defined in a given module class.

    The returned tuple contains the four dicts ``(registers, logic, submodules, other)``.
    """
    registers = {}
    logic = {}
    submodules = {}
    other = {}
    for name, value in typing.get_type_hints(module_class).items():
        if isinstance(value, type) and issubclass(value, Module):
            submodules[name] = value
        elif isinstance(value, type) and issubclass(value, _Register):
            registers[name] = value
        else:
            # let common coding mistakes produce an error
            if isinstance(value, _Register):
                raise ValueError(
                    f"Register {name} should not be instantiated. "
                    f"Type annotations require the type, not an "
                    f"instance. Consider removing `()` from the "
                    f"register definition."
                )
            elif isinstance(value, Module):
                raise ValueError(
                    f"Submodule {name} should not be instantiated. "
                    f"Type annotations require the type, not an "
                    f"instance. Consider removing `()` from the "
                    f"module definition."
                )
            else:
                logger.debug(f"Ignoring annotated type {name}: {value}.")
    for name in dir(module_class):
        value = getattr(module_class, name)
        if is_logic(value):
            logic[name] = value
        elif isinstance(value, _Register):
            logger.warning(
                f"The register {name} was already instantiated. This is "
                f"currently discouraged and not fully supported."
            )
            registers[name] = value
        else:
            if not name.startswith("__"):
                other[name] = value
    return registers, logic, submodules, other


def hash_module(module_class) -> str:
    return "latest"


class Module:
    @classmethod
    def __init_subclass__(cls):
        logger.debug(f"Running {cls}.__init_subclass__.")
        # 1. extract which registers and submodules are defined
        (
            cls._pypga_registers,
            cls._pypga_logic,
            cls._pypga_submodules,
            other,
        ) = scan_module_class(cls)
        # 2. instantiate all registers
        for name, register_cls in cls._pypga_registers.items():
            try:
                register = getattr(cls, name)
            except AttributeError:
                register = register_cls()
                register.name = name
                setattr(cls, name, register)
            else:
                # register was already instantiated
                assert isinstance(register, _Register)
                assert register.name == name
        # 3. insert call to _init_module into constructor for submodule instantiation at runtime
        old_init = functools.partial(cls.__init__)

        @functools.wraps(cls.__init__)
        def new_init(self, *args, name="top", parent=None, interface=None, **kwargs):
            self._init_module(name, parent, interface)
            old_init(self, *args, **kwargs)

        cls.__init__ = new_init
        # 4. compute hash for module
        cls._hash = hash_module(cls)

    def _init_module(self, name, parent, interface):
        """Initializes the pypga module hierarchy before the actual constructor is called."""
        if hasattr(self, "_parent") and hasattr(self, "_interface"):
            logger.debug(f"Skipping {self}._init_module because it has already run.")
            return
        logger.debug(
            f"Running {self}._init_module(self={self}, parent={parent}, interface={interface})."
        )
        self._name = name
        self._parent = parent
        self._interface = interface
        for name, submodule_cls in self._pypga_submodules.items():
            setattr(
                self, name, submodule_cls(name=name, parent=self, interface=interface)
            )

    def _get_parents(self):
        parents = [self._name]
        parent = self._parent
        while parent is not None:
            parents.insert(0, parent._name)
            parent = parent._parent
        return parents

    def _get_full_name(self):
        parents = self._get_parents()
        return parents[0] + "." + "_".join(parents[1:])

    @property
    def registers(self):
        registers = {name: getattr(self, name) for name in self._pypga_registers}
        return {k: v for k, v in registers.items() if not isinstance(v, Callable)}

    @property
    def _clock_period(self):
        # TODO: generalize to multiple boards
        return 8e-9

    @property
    def _clock_rate(self):
        # TODO: generalize to multiple boards
        return 1 / self._clock_period

    @property
    def _ram_start(self):
        # TODO: generalize to multiple boards
        return 0xa000000


DEFAULT_BOARD = "stemlab125_14"


class TopModule(Module):
    @classmethod
    def _build(cls, board=DEFAULT_BOARD):
        builder = get_builder(board=board, module_class=cls)
        return builder.build()

    @classmethod
    @functools.wraps(RemoteInterface)
    def run(cls, *args, host=None, board=DEFAULT_BOARD, autobuild=True, **kwargs):
        """Runs the design on a board and returns an interfaced instance."""
        builder = get_builder(board=board, module_class=cls)
        if not builder.result_exists:
            if autobuild:
                builder.build()
            else:
                raise ValueError(
                    "The design you are trying to instantiate must be built first. Try "
                    "running this function call with the argument ``autobuild=True``."
                )
        if host is None:
            interface = LocalInterface(result_path=builder.result_path)
        else:
            interface = RemoteInterface(host=host, result_path=builder.result_path)
        return cls(*args, interface=interface, **kwargs)

    def stop(self):
        self._interface.stop()

    def __del__(self):
        self.stop()
