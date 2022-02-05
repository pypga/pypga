import pytest
from pypga.core import MigenModule
from pypga.modules.migen.pulsegen import MigenPulseBurstGen, MigenPulseGen

from migen import Constant, Signal, run_simulation
from migen.fhdl import verilog


class TestMigenPulseGenIntPeriod:
    period = 10
    period_type = int
    on = True
    high_after_on = True
    first_cycle_period_offset = 0

    @pytest.fixture
    def dut(self):
        period_argument = self.period_type(self.period - 2)  # the actual period is 2 clock cycles more than the setting
        yield MigenPulseGen(period=period_argument, on=self.on, high_after_on=self.high_after_on, first_cycle_period_offset=self.first_cycle_period_offset)
    
    @pytest.mark.skip
    def test_verilog(self, dut):
        print(verilog.convert(dut))

    def test_out(self, dut):
        print(f"\n\nStart {self.__class__.__name__}")
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
                            if cycle > self.period - 1:  # 1 cycle latency causes the 0th clock cycle to have out=0
                                expected_out = 1
                print(f"Cycle {cycle:02d}: count={(yield dut.count):02d} (0b{(yield dut.count):0{width}b}) carry={(yield dut.carry)} out={(yield dut.out)} (expected={expected_out})")
                if self.first_cycle_period_offset == 0:  # TODO: extend test to nonzero values
                    assert (yield dut.out) == expected_out           
                yield
        run_simulation(dut, assertions())



class TestMigenPulseGenOff(TestMigenPulseGenIntPeriod):
    on = False


class TestMigenPulseGenConstantPeriod(TestMigenPulseGenIntPeriod):
    period = 2
    period_type = Constant


class TestMigenPulseGenSignalPeriod(TestMigenPulseGenIntPeriod):
    def period_type(self, period):
        return Signal(32, reset=period)
        

class TestMigenPulseGenLowAfterOn(TestMigenPulseGenIntPeriod):
    high_after_on = False
    period = 5


class TestMigenPulseGenFirstCycleOffset(TestMigenPulseGenIntPeriod):
    high_after_on = False
    period = 5
    first_cycle_period_offset = 1
    

class TestMigenPulseBurstGenIntPulses:
    period = 1  # actual period is two clock cycles more than the setting
    pulses = 5  # the actual number of pulses is 1 clock cycle more than the setting
    pulses_type = int
    trigger_delay = 2
    cycles_to_simulate = 30

    @pytest.fixture
    def dut(self):
        pulses_argument = self.pulses_type(self.pulses) 
        period_argument = self.period  
        reset = Signal(1, reset=False)
        trigger = Signal(1, reset=False)
        dut = MigenPulseBurstGen(trigger=trigger, reset=reset, pulses=pulses_argument, period=period_argument)
        dut._dut_reset = reset
        dut._dut_trigger = trigger
        yield dut

    @pytest.mark.skip
    def test_verilog(self, dut):
        print(verilog.convert(dut))

    def simulator(self):
        """Generator returning expected values for out, busy, and count."""
        trigger = self.trigger()
        yield 0, 0, 0
        while True:
            if next(trigger) == 0:
                yield 0, 0, 0
            else:
                for count in range(self.pulses, -1, -1):
                    print("Count", count)
                    # trigger for the first cycle has already been consumed, so skip in that case
                    if count != self.pulses:
                        next(trigger)
                    yield 1, 1, count
                    for _ in range(self.period + 1):
                        next(trigger)
                        yield 0, 1, count

    def trigger(self):
        for _ in range(self.trigger_delay):
            yield 0
        yield 1
        while True:
            yield 0

    def test_out(self, dut):
        print(f"\n\nStart {self.__class__.__name__}")
        expected = self.simulator()        
        trigger = self.trigger()
        next(trigger)  # advance trigger cycle by one, as we need 1 cycle latency to feed trigger into the dut (migen-related issue)
        def assertions():
            for cycle in range(self.cycles_to_simulate):
                trigger_value = next(trigger)
                yield dut._dut_trigger.eq(trigger_value)
                expected_out, expected_busy, expected_count = next(expected)
                print(f"Cycle {cycle:02d}: trigger={(yield dut._dut_trigger)} busy={(yield dut.busy)}({expected_busy}) out={(yield dut.out)}({expected_out}) count={(yield dut.count):02d}({expected_count:02d})")
                assert (yield dut.out) == expected_out
                assert (yield dut.busy) == expected_busy
                assert (yield dut.count) == expected_count
                yield
        run_simulation(dut, assertions())


class TestMigenPulseBurstGenSignalPulses(TestMigenPulseBurstGenIntPulses):
    def pulses_type(self, pulses):
        return Signal(32, reset=pulses)


class TestMigenPulseBurstGenContinuous(TestMigenPulseBurstGenIntPulses):
    def trigger(self):
        for _ in range(self.trigger_delay):
            yield 0
        while True:
            yield 1


@pytest.mark.skip(reason="period of zero is not yet supported")
class TestMigenPulseBurstGenIntPulsesFast(TestMigenPulseBurstGenIntPulses):
    period = 0  # actual period is two clock cycles more than the setting
