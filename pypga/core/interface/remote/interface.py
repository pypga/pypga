import time
from typing import List, Union

import numpy as np

from ..interface import BaseInterface
from .client import Client
from .server import Server
from .sshshell import SshShell


class RemoteInterface(BaseInterface):
    def __init__(self, result_path: str = None, host: str = "127.0.0.1"):
        super().__init__(result_path)
        self.host = host
        self.server = Server(
            host=host,
            bitstreamfile=self.build_result_path / Server._bitstreamname,
        )
        self.client = Client(host=host, token=self.server.token)
        self._extra_shell = None  # lazy instantiation

    def read_from_address(self, address: int, length: int = 1) -> Union[int, List[int]]:
        read_value = [int(v) for v in self.client.reads(address, length)]
        if len(read_value) == 1:
            return read_value[0]
        else:
            return read_value

    def write_to_address(self, address: int, value: Union[int, List[int]]):
        try:
            write_value = [int(v) for v in value]
        except TypeError:
            write_value = [int(value)]
        self.client.writes(address, write_value)

    def read_from_ram(self, offset: int = 0, length: int = 1) -> np.ndarray:
        return self.client.read_from_ram(offset, length)

    @property
    def extra_shell(self):
        if self._extra_shell is None:
            self._extra_shell = SshShell(
                hostname=self.host,
                sshport=22,
                user="root",
                password="root",
                delay=0.1,
                )
            time.sleep(0.2)
            self._extra_shell.read()  # purge any output
        return self._extra_shell

    def stop(self):
        self.client.stop()
        self.server.stop()
        if self._extra_shell is not None:
            self._extra_shell.stop()
            self._extra_shell = None
