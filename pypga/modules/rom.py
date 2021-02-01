from migen import *
from ..core import Module, logic, Register, Signal


def Rom(data: list, width: int = None, add_readout_registers: bool = False):
    _data = data   # we need this to be able to call a variable ``data`` in the class
    if width is None:
        assert min(_data) >= 0
        _width = max(_data).bit_length()
    else:
        _width = width
    _depth = len(_data)

    class _Rom(Module):
        width = _width
        depth = _depth
        data = _data

        @logic
        def _setup_memory(self):
            self.specials.memory = Memory(width=_width, depth=_depth, init=_data)
            self.specials.port = self.memory.get_port(write_capable=False)
            if not add_readout_registers:
                self.index = Signal(size=_depth.bit_length(), reset=0)
                self.value = Signal(size=_width, reset=0)
            self.comb += self.port.adr.eq(self.index)
            self.sync += self.value.eq(self.port.dat_r)

        if add_readout_registers:
            index: Register.custom(width=_depth.bit_length(), default=0)
            value: Register.custom(width=_width, readonly=True, default=0)

            def get(self, index):
                self.index = index
                return self.value

            @property
            def values(self):
                return [self.get(index) for index in range(self.depth)]

    return _Rom

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