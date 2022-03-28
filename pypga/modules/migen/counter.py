from migen import Cat

from pypga.core import If, MigenModule, Signal


class MigenCounter(MigenModule):
    def __init__(
        self, start=0, stop=None, step=1, reset=0, on=1, width=32, direction="up"
    ):
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
        self.count = Signal(width + 1)
        self.carry = Signal(1)
        self.done = Signal(reset=0)
        ###
        if isinstance(start, int):
            initial_count = start
        else:
            initial_count = start.reset
        count_with_carry = Signal(width + 1, reset=initial_count)
        self.comb += [
            self.count.eq(Cat(count_with_carry[:-1], 0)),
            self.carry.eq(count_with_carry[-1]),
        ]
        if stop is not None:
            self.comb += If((self.count == stop), self.done.eq(1)).Else(self.done.eq(0))
        self.sync += [
            If(reset == 1, count_with_carry.eq(start),).Elif(
                (~self.done & on) == 1,
                count_with_carry.eq(self.count + step)
                if direction == "up"
                else count_with_carry.eq(self.count - step),
            )
        ]
