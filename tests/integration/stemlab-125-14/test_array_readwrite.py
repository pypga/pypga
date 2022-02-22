from pypga.core.logic_function import logic
from pypga.core import TopModule, Register
import pytest
import time
import math
import numpy as np


def ReadwriteArray(depth=1221, width=31):
    class _ReadwriteArray(TopModule):
        initial_data = [depth - i for i in range(depth)]
        array: Register(default=initial_data, depth=depth, width=width, readonly=False)
        value: Register(default=0, width=width, readonly=True)
        index: Register(default=0, width=32)

        @logic
        def _connect(self):
            self.comb += [
                self.array_index.eq(self.index),
                self.value.eq(self.array),
            ]

    return _ReadwriteArray


@pytest.fixture(scope="module")
def readwrite_array(host, board):
    dut = ReadwriteArray().run(host=host, board=board)
    yield dut
    dut.stop()


class TestReadonlyArray:
    @pytest.fixture
    def dut(self, readwrite_array):
        yield readwrite_array

    def test_read(self, dut):
        actual = dut.array
        expected = dut.initial_data
        assert np.array_equal(actual, expected)

    def test_write(self, dut):
        new_data = [i for i in range(len(dut.initial_data))]

        index = 123
        dut.index = index
        assert dut.value == dut.initial_data[index]

        dut.array = new_data
        actual = dut.array
        expected = new_data
        try:
            assert dut.value == new_data[index]
            assert np.array_equal(actual, expected)
        finally:
            # retore initial values for subsequent tests
            dut.array = dut.initial_data

    @pytest.mark.parametrize("repetitions", [10, 20])
    def test_write_time(self, dut, repetitions):
        start_time = time.time()
        for i in range(repetitions):
            dut.array = dut.initial_data
        duration = (time.time() - start_time) / repetitions
        print(duration, "s")
        assert duration < 0.01
