from abc import ABC, abstractmethod
from .common import get_result_path, get_build_path
import shutil


class BaseBuilder(ABC):
    board = None

    def __init__(self, module_class):
        self.module_class = module_class
        self.build_path = get_build_path()
        self.result_path = get_result_path(board=self.board, module_class=module_class)

    _build_results = ["bitstream.bin", "csr.csv"]

    def copy_results(self):
        """Copy all build results to a persistent folder"""
        shutil.rmtree(self.result_path)
        self.result_path.mkdir(parents=True, exist_ok=True)
        for result in self._build_results:
            shutil.copy(self.build_path / result, self.result_path / result)

    @abstractmethod
    def build(self):
        pass

