from abc import ABC, abstractmethod
from pathlib import Path
from .csrmap import CsrMap


class BaseInterface(ABC):
    def __init__(self, result_path):
        """Interface to the registers of a given FPGA board."""
        self.build_result_path = Path(result_path).resolve()
        self.csrmap = CsrMap(self.build_result_path / "csr.csv")

    def name_to_address(self, name):
        return self.csrmap.address[name]

    def read(self, name: str) -> int:
        """Reads the register with ``name`` and returns the result."""
        return self.read_from_address(self.name_to_address(name))

    def write(self, name: str, value: int):
        """Writes ``value`` to the register ``name``."""
        self.write_to_address(self.name_to_address(name), value)

    @abstractmethod
    def read_from_address(self, address: int) -> int:
        """Reads the register at ``address`` and returns the result."""

    @abstractmethod
    def write_to_address(self, address: int, value: int):
        """Writes ``value`` to the register at ``address``."""
