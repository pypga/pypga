import numpy as np

from pypga.core import (
    BoolRegister,
    FixedPointRegister,
    MigenModule,
    Module,
    NumberRegister,
    Register,
    Signal,
    logic,
)
from pypga.core.register import TriggerRegister
from pypga.modules.migen.pulsegen import MigenPulseBurstGen


def ramp(start: float = -1, stop: float = 1, points: int = 1024):
    """Returns a ramp signal."""
    ramp = np.empty(points, dtype=float)
    ramp[: points // 2] = np.linspace(start, stop, points // 2)
    ramp[points // 2 :] = np.linspace(start, stop, (points - points // 2))[::-1]
    return ramp


def Awg(
    data_depth: int = 1024,
    data_width: int = 14,
    data_decimals: int = 0,
    initial_data: list = None,
    sampling_period_width=32,
    default_sampling_period_cycles=10,
    repetitions_width=32,
    default_repetitions=1,
):
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

    class _Awg(Module):
        data: FixedPointRegister(
            width=data_width,
            depth=data_depth,
            default=initial_data,
            reverse=True,
            readonly=False,
            signed=True,
            decimals=data_decimals,
        )
        sampling_period_cycles: NumberRegister(
            width=sampling_period_width,
            default=default_sampling_period_cycles - 2,
            offset_from_python=-2,
            min=2,
        )
        # repetitions: NumberRegister(width=repetitions_width, default=default_repetitions, offset_from_python=0, min=0)
        out: NumberRegister(
            width=data_width,
            readonly=True,
            default=0,
            doc="the current output value",
            signed=True,
        )
        always_on: BoolRegister(default=False)
        software_trigger: TriggerRegister()

        @logic
        def _awg(self):
            self.done = Signal(reset=0)
            self.trigger = Signal(reset=0)
            self.out_trigger = Signal(reset=0)
            ###
            _trigger = Signal(reset=0)
            self.comb += [
                _trigger.eq(self.trigger | self.software_trigger | self.always_on)
            ]
            self.submodules.pulseburst = MigenPulseBurstGen(
                trigger=_trigger,
                reset=False,
                pulses=data_depth - 1,
                period=self.sampling_period_cycles,
            )
            self.comb += [
                self.done.eq(~self.pulseburst.busy),
                self.data_index.eq(self.pulseburst.count),
                self.out_trigger.eq(self.pulseburst.out),
                self.out.eq(self.data),
            ]

        @property
        def sampling_period(self) -> float:
            return self.sampling_period_cycles * self._clock_period

        @sampling_period.setter
        def sampling_period(self, sampling_period: float):
            self.sampling_period_cycles = sampling_period / self._clock_period

        @property
        def period(self) -> float:
            return data_depth * self.sampling_period

        @period.setter
        def period(self, period: float):
            self.sampling_period = period / data_depth

        @property
        def frequency(self) -> float:
            return 1.0 / self.period

        @frequency.setter
        def frequency(self, frequency: float):
            self.period = 1.0 / frequency

        def set_ramp(self, start: float = -1.0, stop: float = 1.0):
            self.data = ramp(start=start, stop=stop, points=data_depth)

    return _Awg
