from migen import Memory, Cat
from ..core import Module, logic, Register, Signal, If, MigenModule


class MigenRam(MigenModule):
    @staticmethod
    def _get_width_and_depth(data, width=None):
        if width is None:
            assert min(data) >= 0
            width = max(data).bit_length()
        return width, len(data)

    def __init__(self, index, data: list, width: int = None, readonly=False):
        """
        A read-only memory module.

        Args:
            index (Signal): the signal to provide the index
            data (list): values of the rom.
            width (int or NoneType): the bit-width of each value, or None to
              automatically infer this from the data.
            readonly (bool): if True, a ROM instead of RAM is created.

        Output signals:
            value: a signal with the ROM value at index.
        """
        width, depth = self._get_width_and_depth(data, width)
        self.value = Signal(width, reset=0)
        ###
        self.specials.memory = Memory(width=width, depth=depth, init=data)
        self.specials.port = self.memory.get_port(write_capable=not readonly, we_granularity=False)
        self.comb += [
            self.port.adr.eq(index),
            self.value.eq(self.port.dat_r),
        ]
        self.width = width
        self.depth = depth
        self.data = data


def ExampleRom(data: list, width: int = None):
    width, depth = MigenRam._get_width_and_depth(data, width)

    class _ExampleRom(Module):
        value: Register(width=width, readonly=True, default=0, depth=depth)
        _data = data

        @logic
        def _rom_logic(self):
            self.submodules.rom = MigenRam(index=self.value_index, data=data, width=width, readonly=True)
            self.comb += [
                self.value.eq(self.rom.value)
            ]
            self.sync += [
                self.value_we.eq(self.value_re),
            ]
    return _ExampleRom


def ExampleRam(data: list = None, width: int = None):
    width, depth = MigenRam._get_width_and_depth(data, width)

    class _ExampleRam(Module):
        value: Register(width=width, readonly=True, default=0, depth=depth)
        _data = data

        @logic
        def _rom_logic(self):
            self.submodules.rom = MigenRam(index=self.value_index, data=data, width=width, readonly=False)
            self.we = self.rom.port.we
            """set self.we to high to enable writing the data in dat_w"""
            self.dat_w = self.rom.port.dat_w
            """set self.dat_w to the data to write"""
            self.comb += [
                self.value.eq(self.rom.value)
            ]
            self.sync += [
                self.value_we.eq(self.value_re),
            ]
    return _ExampleRam

