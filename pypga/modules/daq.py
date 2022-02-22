import numpy as np

from pypga.core import (
    BoolRegister,
    FixedPointRegister,
    If,
    MigenModule,
    Module,
    NumberRegister,
    Register,
    Signal,
    logic,
)
from pypga.core.register import TriggerRegister
from pypga.modules.migen.axiramwriter import MigenAxiRamWriter
from pypga.modules.migen.pulsegen import MigenPulseBurstGen


def DAQ(
    data_depth: int = 1024,
    data_width: int = 14,
    data_decimals: int = 0,
    sampling_period_width: int = 32,
    default_sampling_period: int = 10,
):
    """
    A programmable DAQ module.

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

    class _DAQ(Module):
        data: FixedPointRegister(
            width=data_width,
            depth=data_depth,
            default=None,
            reversed=True,
            readonly=True,
            signed=True,
            decimals=data_decimals,
        )
        sampling_period_cycles: NumberRegister(
            width=sampling_period_width,
            default=default_sampling_period - 2,
            offset_from_python=-2,
            min=2,
        )
        software_trigger: TriggerRegister()
        busy: BoolRegister(readonly=True)

        @logic
        def _daq(self):
            self.trigger = Signal(reset=0)
            self.input = Signal(data_width, reset=0)
            self.trigger = Signal(reset=0)
            ###
            _trigger = Signal(reset=0)
            self.comb += [_trigger.eq(self.trigger | self.software_trigger)]
            self.submodules.pulseburst = MigenPulseBurstGen(
                trigger=_trigger,
                reset=False,
                pulses=data_depth - 1,
                period=self.sampling_period_cycles,
            )
            self.comb += [
                self.busy.eq(self.pulseburst.busy),
                self.data_index.eq(self.pulseburst.count),
                self.data_we.eq(self.pulseburst.out),
                If(
                    self.pulseburst.out == 1,
                    self.data.eq(self.input),
                ),
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

        def get_data(self, start: int = 0, stop: int = -1) -> list:
            return self.data[start:stop]

    return _DAQ


def RAMDAQ(
    data_depth: int = 1024,
    data_width: int = 14,
    data_decimals: int = 0,
    sampling_period_width: int = 32,
    default_sampling_period: int = 10,
    start_offset: int = 0,
):
    """
    A programmable DAQ module, using RAM instead of the system bus for passing data to PS.

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

    class _RAMDAQ(Module):
        sampling_period_cycles: NumberRegister(
            width=sampling_period_width,
            default=default_sampling_period - 2,
            offset_from_python=-2,
            min=2,
        )
        software_trigger: TriggerRegister()
        busy: BoolRegister(readonly=True)

        @property
        def data(self) -> np.ndarray:
            return self._interface.read_from_ram(start_offset, data_depth)

        ram_offset: Register(width=32)

        @logic
        def _daq(self):
            self.trigger = Signal(reset=0)
            self.input = Signal(data_width, reset=0)
            self.trigger = Signal(reset=0)
            ###
            _trigger = Signal(reset=0)
            self.comb += [_trigger.eq(self.trigger | self.software_trigger)]
            self.submodules.pulseburst = MigenPulseBurstGen(
                trigger=_trigger,
                reset=False,
                pulses=data_depth - 1,
                period=self.sampling_period_cycles,
            )
            self.comb += [
                self.busy.eq(self.pulseburst.busy),
                # self.data_index.eq(self.pulseburst.count),
                # self.data_we.eq(self.pulseburst.out),
                # If(
                #     self.pulseburst.out == 1,
                #     self.data.eq(self.input),
                # ),
            ]
            # RAM writer
            self.submodules.axiramwriter = MigenAxiRamWriter(
                address=0xA000000, we=1, data=123
            )
            # self.sync += [
            #     self.axiramwriter.address.eq(0xa000000),
            #     self.axiramwriter.we.eq(1),
            #     self.axiramwriter.data.eq(123),
            # ]

    return _RAMDAQ
