from migen import Memory, Cat
from ..core import Module, logic, Register, Signal, If, MigenModule
from .counter import MigenCounter
from .rom import MigenRom



class MigenRomAwg(MigenModule):
    def __init__(self, data: list, width: int = None, reset=None, on=True):
        """
        A read-only memory module.

        Args:
            data (list): values of the rom.
            width (int or NoneType): the bit-width of each value, or None to
              automatically infer this from the data.
        
        Input signals / args:
            on: whether the AWG should go to its next point or pause.
            reset: resets the AWG to its initial state. If None, the 
              AWG is automatically reset when it's done.

        Output signals:
            value: a signal with the ROM value at the current index.
        """
        self.value = Signal(width)
        self.done = Signal(reset=0)
        ###
        if reset is None:
            reset = self.done
        self.submodules.counter = MigenCounter(
            start=len(data)-1, 
            stop=0, 
            step=1, 
            direction="down", 
            width=(len(data)-1).bit_length(),
            on=on, 
            reset=reset if reset is not None else self.done,
            )
        self.submodules.rom = MigenRom(index=self.counter.count, data=list(reversed(data)), width=width)
        self.comb += [
            self.value.eq(self.rom.value),
            self.done.eq(self.counter.done),
        ]


def ExampleRomAwg(data: list):
    width, _ = MigenRom._get_width_and_depth(data)

    class _ExampleRomAwg(Module):
        value: Register(width=width, readonly=True, default=0)
        
        @logic
        def _connections(self):
            self.submodules.awg = MigenRomAwg(data=data, width=width)
            self.comb += self.value.eq(self.awg.value)

    return _ExampleRomAwg
