from migen import *
from ..core import Module, logic, Register, Signal, MigenModule


class MigenRam(MigenModule):
    @staticmethod
    def _get_width_and_depth(data, width):
        if width is None:
            assert min(data) >= 0
            width = max(data).bit_length()
        return width, len(data)

    def __init__(self, index, data: list, width: int = None):
        """
        A read-only memory module.

        Args:
            index (Signal): the signal to provide the index
            data (list): values of the rom.
            width (int or NoneType): the bit-width of each value, or None to
              automatically infer this from the data.

        Output signals:
            value: a signal with the ROM value at index.
        """
        width, depth = self._get_width_and_depth(data, width)
        self.value = Signal(width, reset=0)
        ###
        self.specials.memory = Memory(width=width, depth=depth, init=data)
        self.specials.port = self.memory.get_port(write_capable=True, we_granularity=False)
        self.comb += self.port.adr.eq(index)
        self.sync += self.value.eq(self.port.dat_r)
        self.width = width
        self.depth = depth
        self.data = data


def RomTest(data: list, width: int = None):
    width, depth = MigenRom._get_width_and_depth(data, width)

    class _RomTest(Module):
        index: Register.custom(width=depth, default=0)
        value: Register.custom(width=width, readonly=True, default=0)
        _data = data

        @logic
        def _rom_logic(self):
            self.submodules.rom = MigenRom(index=self.index, data=data, width=width)
            self.comb += [
                self.value.eq(self.rom.value),
            ]

        def _get(self, index):
            self.index = index
            return self.value

        @property
        def values(self):
            return [self._get(index) for index in range(len(self._data))]

    return _RomTest

#
# class Example(Module):
#     def __init__(self):
#         self.specials.mem = Memory(32, 10, init=[5, 18, 32, 12, 2, 22, 22, 22, 0xff])
#         p1 = self.mem.get_port(write_capable=True, we_granularity=False)
#         p2 = self.mem.get_port(has_re=True, clock_domain="rd")
#         self.specials += p1, p2
#         self.ios = {p1.adr, p1.dat_r, p1.we, p1.dat_w,
#             p2.adr, p2.dat_r, p2.re}
#  p2.re}
