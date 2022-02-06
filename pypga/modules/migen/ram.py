from migen import Memory, Signal

from pypga.core import MigenModule, Module, Register, logic
from pypga.core.common import get_width_and_depth


class MigenRam(MigenModule):
    def __init__(self, index, data: list, width: int = None, readonly=False):
        """
        A memory module.

        Args:
            index (Signal): the signal to provide the index
            data (list): values of the rom.
            width (int or NoneType): the bit-width of each value, or None to
              automatically infer this from the data.
            readonly (bool): if True, a ROM instead of RAM is created.

        Output signals:
            value: a signal with the ROM value at index.
        """
        width, depth = get_width_and_depth(data, width)
        self.value = Signal(width, reset=0)
        ###
        self.specials.memory = Memory(width=width, depth=depth, init=data)
        self.specials.port = self.memory.get_port(
            write_capable=not readonly, we_granularity=False
        )
        self.comb += [
            self.port.adr.eq(index),
            self.value.eq(self.port.dat_r),
        ]
        self.width = width
        self.depth = depth
        self.data = data
