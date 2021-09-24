import pytest
from pypga.modules.pulsegen import MigenPulseGen


from migen import Signal, run_simulation, Constant
from pypga.core import MigenModule
from migen.fhdl import verilog



class TestMigenPulseGenIntPeriod:
    period = 10
    period_type = int
    on = True
    high_after_on = True

    @pytest.fixture
    def dut(self):
        period_argument = self.period_type(self.period - 2)  # the actual period is 2 clock cycles more than the setting
        yield MigenPulseGen(period=period_argument, on=self.on, high_after_on=self.high_after_on)
    
    def test_verilog(self, dut):
        print(verilog.convert(dut))

    def test_out(self, dut):
        print("\nStart")
        width = len(dut.count)
        def assertions():
            for cycle in range(30):
                expected_out = 0
                if self.on:
                    if self.high_after_on:
                        if (cycle % self.period) == 1:  # there is 1 cycle latency
                            expected_out = 1
                    else:
                        if (cycle % self.period) == 0:
                            if cycle != 0:  # 1 cycle latency causes the 0th clock cycle to have out=0
                                expected_out = 1
                print(f"Cycle {cycle:02d}: count={(yield dut.count):02d} (0b{(yield dut.count):0{width}b}) carry={(yield dut.carry)} out={(yield dut.out)} (expected={expected_out})")
                assert (yield dut.out) == expected_out           
                yield
        run_simulation(dut, assertions())


class TestMigenPulseGenConstantPeriod(TestMigenPulseGenIntPeriod):
    period = 9
    period_type = Constant


class TestMigenPulseGenSignalPeriod(TestMigenPulseGenIntPeriod):
    def period_type(self, period):
        return Signal(32, reset=period)
        

class TestMigenPulseGenLowAfterOn(TestMigenPulseGenIntPeriod):
    high_after_on = False
    period = 12


class TestMigenPulseGenOff(TestMigenPulseGenIntPeriod):
    on = False


class TestMigenPulseGenOffLowAfterOn(TestMigenPulseGenIntPeriod):
    on = False
    high_after_on = False
    