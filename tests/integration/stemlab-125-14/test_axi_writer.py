import math
import time

import numpy as np
import pytest
from pypga.core import Register, TopModule
from pypga.core.logic_function import logic
from pypga.modules.axiwriter import AXIWriter


class AxiWriterTester(TopModule):
    axi_writer: AXIWriter(axi_hp_index=0)


@pytest.fixture(scope="module")
def axiwriter(host, board):
    dut = AxiWriterTester.run(host=host)
    yield dut
    dut.stop()


class TestAxiWriter:
    @pytest.fixture
    def dut(self, axiwriter):
        dut = axiwriter.axi_writer
        dut.aw_t = False
        dut.w_t = False
        dut.address = 0xa000000
        yield dut
        dut.aw_t = False
        dut.w_t = False
        dut.address = 0xa000000

    @pytest.mark.parametrize("value", [0, 1, 100, 2345])
    @pytest.mark.parametrize("offset", [0, 8, 16, 80])
    def test_write(self, dut, value, offset):
        dut.data = value
        dut.address += offset
        dut.aw_t = True
        dut.w_t = True
        dut.t()
        data = dut.read_from_ram(offset=offset, length=4)
        print(data)
        assert data[0] == value
        assert data[1] == value
