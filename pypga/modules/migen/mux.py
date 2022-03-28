from typing import List, Union

from migen import Case, Cat, Constant

from pypga.core import If, MigenModule, Signal
from pypga.core.common import get_length


class MigenMux(MigenModule):
    def __init__(
        self,
        select: Signal,
        options: List[Union[Signal, int, Constant]],
        width: int = None,
        default=0,
    ):
        """
        Multiplexer that outputs the signal selected by "select".

        Args:
            select: the index of the option to output.
            options: a list of options to select from.

        Output signals:
            count: the current counter value.
            carry: the carry bit of the counter, which goes high every time
              the counter wraps through zero.
            done: high when the counter value is equal or beyond ``stop``.
        """
        if width is None:
            width = max([get_length(signal) for signal in options])
        self.out = Signal(width)
        ###
        self.comb += Case(
            select,
            {
                "default": self.out.eq(default),
                **{i: self.out.eq(option) for i, option in enumerate(options)},
            },
        )
