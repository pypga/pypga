from migen import Module as MigenModule
from migen import Signal, If
from migen.build.generic_platform import GenericPlatform
from migen.fhdl.verilog import convert
from misoc.interconnect.csr import AutoCSR, CSRStorage, CSRStatus
from .register import Register
import logging
import typing
import hashlib


logger = logging.getLogger(__name__)


class AutoMigenModule(MigenModule, AutoCSR):
    """This class is the migen representation of a ``Module``.

    Args:
        module_class (:class:`Module`): The module definition to extract a migen module from.

    """
    def __init__(self, module_class, platform: GenericPlatform):
        logger.debug(f"Creating migen module for module class {module_class.__name__}.")
        registers = module_class._pypga_registers
        logic_functions = module_class._pypga_logic
        submodules = module_class._pypga_submodules
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
        migen_submodule = AutoMigenModule(submodule, platform)
        setattr(self.submodules, name, migen_submodule)
        # TODO: remove the next line, it seems to be redundant as migen automatically does this
        setattr(self, name, migen_submodule)  # also make the submodule available via `self.name`

    def _add_register(self, register, name):
        if not isinstance(register, Register):
            register = register()  # create a register instance to retrieve attributes in case a class was passed
        logger.debug(f"Creating register {name} of type {register.__class__.__name__}.")
        name_csr = f"{name}_csr"
        if register.readonly:
            register_instance = CSRStatus(size=register.width, reset=register.default, name=name_csr)
            setattr(self, name_csr, register_instance)
            setattr(self, name, register_instance.status)
        else:
            register_instance = CSRStorage(size=register.width, reset=register.default, name=name_csr)
            setattr(self, name_csr, register_instance)
            setattr(self, name, register_instance.storage)
            setattr(self, f"{name}_re", register_instance.re)

    def _add_logic_function(self, logic_function, name, platform):
        logger.debug(f"Implementing logic from function {name}.")
        try:
            return_value = logic_function(self, platform=platform)
        except TypeError:
            return_value = logic_function(self)
        if return_value is not None:
            setattr(self, logic_function.__name__, return_value)

    def _hash(self):
        """
        Returns a hash to unambiguously identify a design.

        This is used to decide whether a design has been build or still needs to be.
        """
        verilog = convert(self)
        hash_ = hashlib.sha256()
        hash_.update(verilog.main_source.encode())
        for filename, content in verilog.data_files.items():
            hash_.update(filename.encode())
            hash_.update(content.encode())
        return hash_.hexdigest()
