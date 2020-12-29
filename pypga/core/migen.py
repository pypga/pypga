from migen import Module as _MigenModule
from migen.build.generic_platform import GenericPlatform
from misoc.interconnect.csr import AutoCSR, CSRStorage
from .register import Register
from .logic_function import is_logic
from .module import Module, scan_module_class
import logging
import typing


logger = logging.getLogger(__name__)


class MigenModule(_MigenModule, AutoCSR):
    """This class is the migen representation of a ``Module``.

    Args:
        module_class (:class:`Module`): The module definition to extract a migen module from.

    """
    def __init__(self, module_class: Module, platform: GenericPlatform):
        logger.debug(f"Creating migen module for module class {module_class.__name__}.")
        registers, logic_functions, submodules, other = scan_module_class(module_class)
        # OTHER ATTRIBUTES MIGHT HAVE TO BE SET TO GUARANTEE EXPECTED FUNCTIONALITY
        # SUCH AS ACCESSING CLASS ATTRIBuTES FROM LOGIC - CURRENTLY WE WORKED AROUND THIS
        # first set "other" attributes, such as constants etc
        # for name, value in other.items():
        #     logger.debug(f"Setting other attribute {name}={value}")
        #     setattr(self, name, value)
        # first create registers to be able to access them from submodules or logic
        for name, register in registers.items():
            self._add_register(register, name)
        # then create the submodules to be able to access them from the logic at this level
        for name, submodule in submodules.items():
            self._add_submodule(submodule, name, platform)
        # finally add all the custom logic
        for name, logic_function in logic_functions.items():
            self._add_logic_function(logic_function, name, platform)
        logger.debug(f"Finished migen module for module class {module_class.__name__}.")

    def _add_submodule(self, submodule, name, platform):
        logger.debug(f"Creating submodule {name} of type {submodule.__name__}.")
        migen_submodule = MigenModule(submodule, platform)
        setattr(self.submodules, name, migen_submodule)
        setattr(self, name, migen_submodule)  # also make the submodule available via `self.name`

    def _add_register(self, register, name):
        if not isinstance(register, Register):
            register = register()  # create a register instance to retrieve attributes in case a class was passed
        logger.debug(f"Creating register {name} of type {register.__class__.__name__}.")
        register_instance = CSRStorage(size=register.size, reset=register.reset, name=name)
        setattr(self, name, register_instance)

    def _add_logic_function(self, logic_function, name, platform):
        logger.debug(f"Implementing logic from function {name}.")
        try:
            return_value = logic_function(self, platform=platform)
        except TypeError:
            return_value = logic_function(self)
        if return_value is not None:
            setattr(self, function.__name__, return_value)
