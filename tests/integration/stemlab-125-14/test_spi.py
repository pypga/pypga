import math
import time

import numpy as np
import pytest

from pypga.core import TriggerRegister, Register, TopModule, logic
from pypga.boards.stemlab125_14.modules.gpio import get_migen_gpio
from pypga.modules.migen.spi import MigenSPI


def SPI(width=8):
    """Creates an SPI module in loopback configuration, i.e. MISO connected to MOSI."""
    class _SPI(TopModule):
        write_data: Register(default=0, width=32, readonly=False)
        start: TriggerRegister()

        read_data: Register(default=0, width=32, readonly=True)

        output: Register(default=0, width=4, readonly=False)

        @logic
        def _connect(self, platform):
            self.submodules.gpio = get_migen_gpio(
                platform=platform,
                is_output=0b0000000000001111,
                output=self.output,
            )
            self.submodules.spi = MigenSPI()
            self.comb += self.spi.miso.eq(self.spi.mosi)
            self.sync += self.read_data.eq(self.spi.read_data)

    return _SPI


@pytest.fixture(scope="module")
def spi(host, board):
    dut = SPI().run(host=host, board=board)
    yield dut
    dut.stop()


class TestSPI:
    @pytest.fixture
    def dut(self, spi):
        yield spi

    @pytest.mark.parametrize("data", [b"abcd", b"\x00\x01\xff\xef"])
    def test_(self, dut, data):
        read_data = dut.read_data
        dut.write_data = 0
        assert dut.write_data == 0
        data = int.from_bytes(data, "big")
        dut.write_data = data
        assert dut.read_data == read_data
        dut.start()
        assert dut.read_data == data
        assert dut.write_data == data
