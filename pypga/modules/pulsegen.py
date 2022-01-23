from pypga.core import Module, logic, BoolRegister, NumberRegister
from .migen.pulsegen import MigenPulseGen


def PulseGen(default_period=8, default_on=True, high_after_on=True, period_width=32):
    class _PulseGen(Module):
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
        
    return _PulseGen
