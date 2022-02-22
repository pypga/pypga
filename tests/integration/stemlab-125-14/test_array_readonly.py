from pypga.core.logic_function import logic
from pypga.core import TopModule, Register
import pytest
import time
import math
import numpy as np


def ReadonlyArray(depth=1000, width=31):
    class _ReadonlyArray(TopModule):
        initial_data = [i for i in range(depth)]
        array: Register(default=initial_data, depth=depth, width=width, readonly=True)
        we: Register(default=0, width=1)
        dat_w: Register(default=0, width=width)
        index: Register(default=0, width=32)

        @logic
        def _connect(self):
            self.comb += [
                self.array.eq(self.dat_w),
                self.array_we.eq(self.we_re),
                self.array_index.eq(self.index),
            ]

    return _ReadonlyArray


@pytest.fixture(scope="module")
def readonly_array(host, board):
    dut = ReadonlyArray().run(host=host, board=board)
    yield dut
    dut.stop()


class TestReadonlyArray:
    @pytest.fixture
    def dut(self, readonly_array):
        yield readonly_array

    def test_read(self, dut):
        actual = dut.array
        expected = dut.initial_data
        assert np.array_equal(actual, expected)

    def test_write(self, dut):
        index = 99
        value = 1234
        dut.index = index
        dut.dat_w = value
        dut.we = 1
        actual = dut.array
        expected = [v for v in dut.initial_data]
        expected[index] = value
        try:
            assert actual[index] == value
            assert np.array_equal(actual, expected)
        finally:
            # retore initial values for subsequent tests
            dut.index = index
            dut.dat_w = dut.initial_data[index]
            dut.we = 1

    @pytest.mark.parametrize("repetitions", [10, 20])
    def test_read_time(self, dut, repetitions):
        start_time = time.time()
        for i in range(repetitions):
            dut.array
        duration = (time.time() - start_time) / repetitions
        print(duration, "s")
        assert duration < 0.01
