from pypga.modules.rom import ExampleRom
from pypga.core import TopModule
import pytest
import time
import math


class MyExampleRom(TopModule):
    rom: ExampleRom(data=[i*10 for i in range(10000)])


@pytest.fixture(scope="module")
def my_example_rom(host, board):
    dut = MyExampleRom.run(host=host, board=board)
    yield dut
    dut.stop()


class TestRom:
    @pytest.fixture
    def rom(self, my_example_rom):
        rom = my_example_rom.rom
        rom._reset_index = True
        yield rom

    def test_read(self, rom):
        expected = rom._data
        actual = rom.value
        for i, (act, exp) in enumerate(zip(actual, expected)):
            assert act == exp

    @pytest.mark.parametrize("repetitions", [10, 20])
    def test_read_time(self, rom, repetitions):
        start_time = time.time()
        for i in range(repetitions):
            rom.value
        duration = (time.time() - start_time) / repetitions
        assert duration < 0.05

