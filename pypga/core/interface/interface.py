from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from .csrmap import CsrMap


class BaseInterface(ABC):
    def __init__(self, result_path):
        """Interface to the registers of a given FPGA board."""
        self.build_result_path = Path(result_path).resolve()
        self.csrmap = CsrMap(self.build_result_path / "csr.csv")

    def stop(self):
        """Stops the interface"""

    def name_to_address(self, name):
        return self.csrmap.address[name]

    def read(self, name: str) -> int:
        """Reads the register with ``name`` and returns the result."""
        return self.read_from_address(self.name_to_address(name))

    def read_array(self, name: str, length: int = 1) -> List[int]:
        """Reads the register with ``name`` multiple times and returns the result array."""
        return self.read_from_address(self.name_to_address(name), length=length)

    def write(self, name: str, value: int):
        """Writes ``value`` to the register ``name``."""
        self.write_to_address(self.name_to_address(name), value)

    def write_array(self, name: str, value: List[int]):
        """Writes each element in the array ``value`` to the register ``name``."""
        self.write_to_address(self.name_to_address(name), value)

    @abstractmethod
    def read_from_address(self, address: int, length: int = 1) -> Union[int, List[int]]:
        """Reads the register at ``address`` and returns the result."""

    @abstractmethod
    def write_to_address(self, address: int, value: Union[int, List[int]]):
        """Writes ``value`` to the register at ``address``."""
