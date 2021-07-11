from pypga.modules.awg import ExampleRomAwg
from pypga.core import TopModule
import pytest
import time
import math


class MyExampleAwg(TopModule):
    rom_awg: ExampleRomAwg(data=[i for i in range(100)])


@pytest.fixture(scope="module")
def my_example_awg(host, board):
    dut = MyExampleAwg.run(host=host, board=board)
    yield dut
    dut.stop()

class TestRomAwg:
    @pytest.fixture
    def awg(self, my_example_awg):
        awg = my_example_awg.rom_awg
        yield awg

    def test_value_in_range(self, awg):
        data = [awg.value for _ in range(1000)]
        mini, maxi = min(data), max(data)
        assert mini >= 0
        assert mini <= 10
        assert maxi >= 90
        assert maxi < 100