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

    def general_purpose_spi_readwrite(self, data: list[int], cpol: bool = True, cpha: bool = False, speed_hz: int = 1_000_000, spi_bus: int = 1, spi_dev: int = 0):
        command = "python3 -c \""
        command += "import spidev;"
        command += "spi = spidev.SpiDev();"
        command += f"spi.open({spi_bus},{spi_dev});"
        command += f"spi.max_speed_hz={speed_hz};"
        command += f"spi.mode={2 * int(cpol) + int(cpha)};"
        command += f"reply=spi.xfer({data});"
        command += "print('reply =', reply);"
        command += "spi.close();"
        command += "\""
        self.extra_shell.read()  # purge any "old" data
        result = self.extra_shell.ask(command)
        timeout = time.time() + 1
        while time.time() < timeout:
            if "reply = [" in result:
                break
            time.sleep(0.01)
            result += self.extra_shell.read()
        else:
            raise TimeoutError(f"Never received a good reply from SPI bus. {result}")
        for line in result.splitlines():
            if line.startswith("reply = ["):
                break
        else:
            raise RuntimeError(f"Result from SPI bus cannot be parsed: {result}")
        data = line.split("=", maxsplit=1)[1]
        return [int(item) for item in data.strip(" []\n").split(", ")]

    def general_purpose_i2c_write(self, i2c_addr: int, register: int, data: list[int]):
        command = "python3 -c \""
        command += "import smbus2;"
        command += "i2c = smbus2.SMBus(0);"
        command += f"reply=i2c.write_i2c_block_data({i2c_addr}, {register}, {data});"
        command += "print('reply =', reply);"
        command += "i2c.close();"
        command += "\""
        self.extra_shell.read()  # purge any "old" data
        result = self.extra_shell.ask(command)
        timeout = time.time() + 1
        while time.time() < timeout:
            if "reply = [" in result:
                break
            time.sleep(0.01)
            result += self.extra_shell.read()
        else:
            raise TimeoutError(f"Never received a good reply from bus. {result}")
        for line in result.splitlines():
            if line.startswith("reply = ["):
                break
        else:
            raise RuntimeError(f"Result from bus cannot be parsed: {result}")
        data = line.split("=", maxsplit=1)[1]
        return [int(item) for item in data.strip(" []\n").split(", ")]

    def general_purpose_i2c_read(self, i2c_addr: int, register: int, length: int):
        command = "python3 -c \""
        command += "import smbus2;"
        command += "i2c = smbus2.SMBus(0);"
        command += f"reply=i2c.read_i2c_block_data({i2c_addr}, {register}, {length});"
        command += "print('reply =', reply);"
        command += "i2c.close();"
        command += "\""
        self.extra_shell.read()  # purge any "old" data
        result = self.extra_shell.ask(command)
        timeout = time.time() + 1
        while time.time() < timeout:
            if "reply = [" in result:
                break
            time.sleep(0.01)
            result += self.extra_shell.read()
        else:
            raise TimeoutError(f"Never received a good reply from bus. {result}")
        for line in result.splitlines():
            if line.startswith("reply = ["):
                break
        else:
            raise RuntimeError(f"Result from bus cannot be parsed: {result}")
        data = line.split("=", maxsplit=1)[1]
        return [int(item) for item in data.strip(" []\n").split(", ")]
