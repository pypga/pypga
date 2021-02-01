from ..core import Module, logic, Register, BoolRegister, MigenModule, Signal, If


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
        self.count = Signal(width)
        self.carry = Signal()
        self.done = Signal()
        ###
        count_with_carry = Signal(width+1, reset=start if isinstance(start, int) else start.reset)
        done = Signal(reset=0)
        self.comb += [
            self.count.eq(count_with_carry[:-1]),
            self.carry.eq(count_with_carry[-1]),
        ]
        if stop is not None:
            self.comb += If(
                (self.count >= stop) if direction == "up" else (self.count <= stop),
                done.eq(1)).Else(done.eq(0)
            )
        self.sync += [
            If(reset == 1,
               count_with_carry.eq(start),
               self.done.eq(0)
            ).Elif(self.done == 0,
                   self.done.eq(done),
                   If(on==1,
                      count_with_carry.eq((self.count + step) if direction == "up" else (self.count - step))
                   ),
            )
        ]


def CounterTest(width=32, default_start=0, default_stop=None, default_step=1, direction="up"):
    class _CounterTest(Module):
        start: Register.custom(width=width, default=default_start)
        step: Register.custom(width=width, default=default_step)
        if default_stop is not None:
            stop: Register.custom(width=width, default=default_stop)
        on: Register.custom(width=1, default=1)
        reset: Register.custom(width=1, default=0)
        count: Register.custom(readonly=True, width=width, default=default_start)
        carry: BoolRegister.custom(readonly=True, width=1, default=0)
        done: BoolRegister.custom(readonly=True, width=1, default=0)

        @logic
        def _count(self):
            self.submodules.counter = MigenCounter(
                start=self.start,
                stop=None if default_stop is None else self.stop,
                step=self.step,
                on=self.on,
                reset=self.reset_re,
            )
            self.comb += [
                self.count.eq(self.counter.count),
                self.carry.eq(self.counter.carry),
                self.done.eq(self.counter.done),
            ]

    return _CounterTest


