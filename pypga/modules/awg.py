from migen import Memory, Cat
from ..core import Module, logic, Register, NumberRegister, BoolRegister, Signal, If, MigenModule
from .counter import MigenCounter
from .rom import MigenRom
from .pulsegen import MigenPulseGen


class MigenRomAwg(MigenModule):
    def __init__(self, data: list, width: int = None, reset=None, on=True, period=0):
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
            period: the sampling period.

        Output signals:
            value: a signal with the ROM value at the current index.
        """
        self.value = Signal(width)
        self.done = Signal(reset=0)
        ###
        if reset is None:
            reset = self.done
        counter_on = Signal()
        self.submodules.counter = MigenCounter(
            start=len(data)-1, 
            stop=0, 
            step=1, 
            direction="down", 
            width=(len(data)-1).bit_length(),
            on=counter_on, 
            reset=reset if reset is not None else self.done,
            )
        self.submodules.rom = MigenRom(index=self.counter.count, data=list(reversed(data)), width=width)
        self.submodules.pulsegen = MigenPulseGen(
            period=period,
            on=on,
            high_after_on=True,
        )
        self.comb += [
            self.value.eq(self.rom.value),
            self.done.eq(self.counter.done),
            counter_on.eq(self.pulsegen.out),
        ]


def ExampleRomAwg(data: list, default_on=True, period_width=32, default_period=8):
    width, _ = MigenRom._get_width_and_depth(data)

    class _ExampleRomAwg(Module):
        period: NumberRegister(width=period_width, default=default_period-2, offset_from_python=-2, min=2)
        out: Register(width=width, readonly=True, default=0, doc="the current output value")
        on: BoolRegister(default=default_on)

        @logic
        def _connections(self):
            self.done = Signal()
            self.submodules.awg = MigenRomAwg(data=data, width=width, period=self.period, on=self.on)
            self.comb += [
                self.out.eq(self.awg.value),
                self.done.eq(self.awg.done),
            ]

    return _ExampleRomAwg
