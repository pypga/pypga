import math
import time

import numpy as np
import pytest
from pypga.core import Register, TopModule
from pypga.core.logic_function import logic
from pypga.modules.axiwriter import AXIWriter


class TestAxiWriterHP0:
    _axi_hp_index = 0

    @pytest.fixture(scope="class")
    def axiwriter(self, host, board):
        class AxiWriterTester(TopModule):
            axiwriter: AXIWriter(axi_hp_index=self._axi_hp_index)
        
        dut = AxiWriterTester.run(host=host, board=board)
        yield dut
        dut.stop()

    @pytest.fixture
    def dut(self, axiwriter):
        dut = axiwriter.axiwriter
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
        dut.trigger_count = 150
        dut.t()
        time.sleep(0.01)
        data = dut.read_from_ram(offset=offset, length=2)
        print(data)
        assert tuple(data) == (value, value)


# class TestAxiWriterHP1(TestAxiWriterHP0):
#     _axi_hp_index = 1

# class TestAxiWriterHP2(TestAxiWriterHP0):
#     _axi_hp_index = 2

# class TestAxiWriterHP3(TestAxiWriterHP0):
#     _axi_hp_index = 3
