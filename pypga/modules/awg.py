from ..core import Module, MigenModule, logic, Register, NumberRegister, BoolRegister, Signal
from .counter import MigenCounter
from .pulsegen import MigenPulseGen
from .ram import MigenRam


def Awg(data: list, default_on=True, sampling_period_width=32, default_period=8, repetitions_width=32, reset=None):
    """
    A programmable AWG module.

    Args:
        data (list): initial values of the AWG.
        width (int or NoneType): the bit-width of each value, or None to
            automatically infer this from the data.
    
    Input signals / args:
        on: whether the AWG should go to its next point or pause.
        reset: resets the AWG to its initial state. If None, the 
            AWG is automatically reset when it's done.
        sampling_period: the sampling period.

    Output signals:
        value: a signal with the ROM value at the current index.
    """
    width, depth = MigenRam._get_width_and_depth(data)
    initial_data = data

    class _Awg(Module):
        data: NumberRegister(width=width, depth=depth, default=initial_data, readonly=False)
        sampling_period: NumberRegister(width=sampling_period_width, default=default_period-2, offset_from_python=-2, min=2)
        repetitions: NumberRegister(width=repetitions_width, default=1, offset_from_python=0, min=0)
        out: Register(width=width, readonly=True, default=0, doc="the current output value")
        on: BoolRegister(default=default_on)

        @logic
        def _awg(self):
            self.done = Signal(reset=0)
            ###
            counter_on = Signal()
            self.submodules.counter = MigenCounter(
                start=0,
                stop=len(data)-1, 
                step=1, 
                direction="up", 
                width=width,
                on=counter_on, 
                reset=self.done if reset is None else reset,
                )
            self.submodules.pulsegen = MigenPulseGen(
                period=self.sampling_period,
                on=self.on,
                high_after_on=True,
            )
            self.comb += [
                self.done.eq(self.counter.done),
                counter_on.eq(self.pulsegen.out),
                self.out.eq(self.data),
                self.data_index.eq(self.counter.count)
            ]

    return _Awg
