from typing import Literal
import pytest
from migen import Constant, Signal, run_simulation
from migen.fhdl import verilog
from numpy.random import randint
from pypga.modules.migen.pid import MigenPid


class TestMigenPid:
    data_width = 8  # there seems to be a bug for "round" numbers like 32

    @pytest.fixture
    def dut(self):
        self.input_signal = Signal(bits_sign=(self.data_width, True))
        self.setpoint = Signal(self.data_width)
        self.k_p = Signal(self.data_width)
        self.k_i = Signal(self.data_width)
        pid = MigenPid(
            input=self.input_signal,
            setpoint=self.setpoint,
            k_p=self.k_p,
            k_i=self.k_i,
            width=self.data_width,
        )
        yield pid

    def test_verilog(self, dut):
        print(verilog.convert(dut))

    def get_random_number(self):
        return randint(-2**(self.data_width-1), 2**(self.data_width-1)-1)

    def test_pid(self, dut):
        print(f"\n\nStart {self.__class__.__name__}")
        def assertions():
            yield self.setpoint.eq(10)
            yield self.k_p.eq(1)
            for cycle in range(30):
                # random_int = self.get_random_number()
                random_int = cycle
                yield self.input_signal.eq(random_int)
                print(
                    f"Cycle {cycle:03d}: random_int={random_int} input_signal={(yield dut.input_signal)} error={(yield dut.error)} sum={(yield dut.sum)} out={(yield dut.out)}",
                )
                yield

        run_simulation(dut, assertions())

