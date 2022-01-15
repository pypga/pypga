from migen import Cat, Constant
from ..core import Module, logic, Register, BoolRegister, TriggerRegister, MigenModule, Signal, If


class MigenCounter(MigenModule):
    def __init__(self, start=0, stop=None, step=1, reset=0, on=1, width=32, direction="up"):
        """
        Counter that can count either "up" or "down".

        Args:
            start (int or Signal): value to start counting from.
            stop (int, Signal, or None): value at or beyond which to stop
              counting. If ``None``, the counter will wrap through zero.
            step (int or Signal): counting step.
            reset (bool or Signal): when high, the counter will to its starting
              configuration.
            on (bool or Signal): the counter will only keep counting when this
              signal is high.
            width (int): width of the count register.
            direction (str, "up" or "down"): the direction to count in. step
              should always be positive.

        Output signals:
            count: the current counter value.
            carry: the carry bit of the counter, which goes high every time
              the counter wraps through zero.
            done: high when the counter value is equal or beyond ``stop``.
        """
        self.count = Signal(width+1)
        self.carry = Signal(1)
        self.done = Signal(reset=0)
        ###
        if isinstance(start, int):
            initial_count = start
        else:
            initial_count = start.reset
        count_with_carry = Signal(width+1, reset=initial_count)
        self.comb += [
            self.count.eq(Cat(count_with_carry[:-1], 0)),
            self.carry.eq(count_with_carry[-1]),
        ]
        if stop is not None:
            self.comb += If((self.count == stop), self.done.eq(1)).Else(self.done.eq(0))
        self.sync += [
            If(
                reset == 1,
                count_with_carry.eq(start),
            ).Elif(
                (~self.done & on) == 1,
                count_with_carry.eq(self.count + step) if direction == "up" else count_with_carry.eq(self.count - step) 
            )
        ]


def ExampleCounter(width=32, default_start=0, default_stop=None, default_step=1, default_on=True, direction="up"):
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
