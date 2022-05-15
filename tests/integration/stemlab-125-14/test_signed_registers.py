import math
import time

import numpy as np
import pytest

from pypga.core import BoolRegister, NumberRegister, TopModule
from pypga.core.logic_function import logic


def AddMultiply(width=8):
    class _AddMultiply(TopModule):
        a: NumberRegister(default=0, width=width, signed=True, readonly=False)
        b: NumberRegister(default=1, width=width, signed=True, readonly=False)
        sum: NumberRegister(default=2, width=width+1, signed=True, readonly=True)
        product: NumberRegister(default=2, width=width*2, signed=True, readonly=True)
        sum_unsigned: NumberRegister(default=2, width=width+1, signed=False, readonly=True)
        product_unsigned: NumberRegister(default=2, width=width*2, signed=False, readonly=True)
        a_above_b: BoolRegister(readonly=True)

        @logic
        def _connect(self):
            self.sync += [
                self.sum.eq(self.a + self.b),
                self.product.eq(self.a * self.b),
                self.sum_unsigned.eq(self.a + self.b),
                self.product_unsigned.eq(self.a * self.b),
                self.a_above_b.eq(self.a > self.b),
            ]
    return _AddMultiply


@pytest.fixture(scope="module")
def add_multiply(host, board):
    dut = AddMultiply().run(host=host, board=board)
    yield dut
    dut.stop()


class TestReadonlyArray:
    @pytest.fixture
    def dut(self, add_multiply):
        yield add_multiply

    _eight_bit_numbers = [0, 1, 2, 127, -1, -127, -128]

    @pytest.mark.parametrize("operation", ["sum", "product", "sum_unsigned", "product_unsigned", "compare"])
    @pytest.mark.parametrize("a", _eight_bit_numbers)
    @pytest.mark.parametrize("b", _eight_bit_numbers)
    def test_add_multiply(self, dut, operation, a, b):
        assert a < 2**15-1
        assert a > -2**15
        assert b < 2**15-1
        assert b > -2**15
        dut.a = a
        dut.b = b
        assert dut.a == a
        assert dut.b == b
        if operation == "sum":
            assert dut.sum == a + b
        elif operation == "product":
            assert dut.product == a * b
        elif operation == "sum_unsigned":
            result = a + b
            if result < 0:
                result += 2**9
            assert dut.sum_unsigned == result
        elif operation == "product_unsigned":
            result = a * b
            if result < 0:
                result += 2**16
            assert dut.product_unsigned == result
        elif operation == "compare":
            assert dut.a_above_b == (a > b)
        else:
            raise ValueError(f"Unknown operation.")