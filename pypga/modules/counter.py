from migen import *
from ..core import Module, logic, Register, Signal


def Counter(width=32, default_start=0, default_stop=0, default_step=1):
    class _Counter(Module):
        start: Register.custom(width=width, default=default_start)
        #stop: Register.custom(width=width, default=default_stop)
        step: Register.custom(width=width, default=default_step)
        reset: Register.custom(width=1, default=0)  # writing to this register triggers a reset
        count: Register.custom(readonly=True, width=width, default=default_start)

        @logic
        def _count(self):
            self.sync += [If(
                self.reset_re == 1,
                self.count.eq(self.start)
            ).Else(
                self.count.eq(self.count + self.step)
            )]

    return _Counter
