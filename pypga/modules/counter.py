from pypga.core import BoolRegister, Module, Register, TriggerRegister, logic

from .migen.counter import MigenCounter


def Counter(
    width=32,
    default_start=0,
    default_stop=None,
    default_step=1,
    default_on=True,
    direction="up",
):
    class _CounterTest(Module):
        start: Register(width=width, default=default_start)
        step: Register(width=width, default=default_step)
        if default_stop is not None:
            stop: Register(width=width, default=default_stop)
        on: Register(width=1, default=default_on)
        reset: TriggerRegister()

        count: Register(readonly=True, width=width, default=default_start)
        carry: BoolRegister(readonly=True, width=1, default=0)
        done: BoolRegister(readonly=True, width=1, default=0)

        @logic
        def _counter_logic(self):
            self.submodules.counter = MigenCounter(
                start=self.start,
                stop=None if default_stop is None else self.stop,
                step=self.step,
                on=self.on,
                reset=self.reset,
                direction=direction,
            )
            self.comb += [
                self.count.eq(self.counter.count),
                self.carry.eq(self.counter.carry),
                self.done.eq(self.counter.done),
            ]

    return _CounterTest
