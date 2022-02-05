from typing import List, Union

from migen import Case, Cat, Constant

from pypga.core import If, MigenModule, Signal
from pypga.core.common import get_length


class MigenSignedAdder(MigenModule):
    def __init__(
        self,
        *inputs,
        width: int = 32,
    ):
        """
        Adder that adds the two input signals and optionally performs saturation.


        Args:
            *inputs: the input signals that should be added together.

        Output signals:
            out: the sum of the two inputs.
            carry: high when an overflow has occurred. If
        """

        self.out = Signal(width)
        ###
        self.sync += [self.out.eq(sum(inputs))]
