from migen import Cat, Constant
from ..core import Module, logic, BoolRegister, NumberRegister, MigenModule, Signal, If



class MigenPulseGen(MigenModule):
    def __init__(self, period=0, on=True, high_after_on=True):
        """
        Pulse generator that emits a pulse every ``period + 2`` clock cycles. 

        Args:
            period (int or Signal): period of low clock cycles between pulses.
              Set this to a negative number to indicate that the output should 
              be constantly high.
            on (bool or Signal): enables the pulse generator sequence when high.
            high_after_on (bool): when True, the output goes high for a single 
              clock cycle when ``on`` goes high, otherwise it only goes high 
              after the first period.

        Output signals:
            out: the pulse sequence, 0 between pulses and 1 for a single clock 
              cycle during a pulse.
        """
        self.out = Signal(reset=0)
        ###
        try:
            count_reset = period.reset
        except AttributeError:
            count_reset = period
        try:
            width = len(period)
        except TypeError:
            width = count_reset.bit_length()
        self.count = Signal(width, reset=count_reset)
        self.carry = Signal(1, reset=high_after_on)
        self.sync += [
            self.out.eq(self.carry & on),
            If(
                on == 0,  # prepare for the first pulse when off
                self.carry.eq(high_after_on),
                self.count.eq(period),
            ).Elif(
                self.carry,  # restart countdown
                self.carry.eq(0),
                self.count.eq(period),
            ).Else(  # regular countdown
                Cat(self.count, self.carry).eq(Cat(self.count, 0) - 1),
            )
        ]


def ExamplePulseGen(default_period=8, default_on=True, high_after_on=True, period_width=32):
    class _ExamplePulseGen(Module):
        period: NumberRegister(width=period_width, default=default_period-2, offset_from_python=-2, min=2)
        on: BoolRegister(default=default_on)
        out: BoolRegister(default=False, readonly=True)

        @logic
        def _setup(self):
            self.submodules.pulsegen = MigenPulseGen(
                period=self.period,
                on=self.on,
                high_after_on=high_after_on,
            )
            self.comb += self.out.eq(self.pulsegen.out)
            
    return _ExamplePulseGen
