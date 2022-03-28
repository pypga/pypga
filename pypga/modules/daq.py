from typing import Optional

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
from pypga.modules.migen.axiwriter import MigenAxiWriter
from pypga.modules.migen.pulsegen import MigenPulseBurstGen

from migen import Cat, Constant


def DAQ(
    data_depth: int = 1024,
    data_width: int = 14,
    data_decimals: int = 0,
    sampling_period_width: int = 32,
    default_sampling_period: int = 10,
    axi_hp_index: Optional[int] = None,
    _ram_start_address: int = 0xa000000,
    _ram_size: int = 0x2000000,
):
    """
    A programmable DAQ module.

    Args:
        axi_hp_index: If an integer is passed here, an AXI HP interface
          is used to directly write data to RAM, otherwise data is sent
          to the PS using a register. The value of this number can be one 
          in [0, 1, 2, 3], indicating the index of the AXI HP bus to use.

    Input signals / args:
        on: whether the AWG should go to its next point or pause.
        reset: resets the AWG to its initial state. If None, the
            AWG is automatically reset when it's done.
        sampling_period: the sampling period.

    Output signals:
        value: a signal with the ROM value at the current index.
    """
    class _DAQ(Module):
        sampling_period_cycles: NumberRegister(
            width=sampling_period_width,
            default=default_sampling_period - 2,
            offset_from_python=-2,
            min=2,
        )
        software_trigger: TriggerRegister()
        busy: BoolRegister(readonly=True)

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

        @logic
        def _daq(self):
            self.trigger = Signal(reset=0)
            self.input = Signal(data_width, reset=0)
            self.trigger = Signal(reset=0)
            ###
            self._trigger = Signal(reset=0)
            self.comb += [self._trigger.eq(self.trigger | self.software_trigger)]
            self.submodules.pulseburst = MigenPulseBurstGen(
                trigger=self._trigger,
                reset=False,
                pulses=data_depth - 1,
                period=self.sampling_period_cycles,
            )
            self.comb += [
                self.busy.eq(self.pulseburst.busy),
            ]

        data: FixedPointRegister(
            width=data_width,
            depth=data_depth,
            default=None,
            reversed=True,
            readonly=True,
            signed=True,
            decimals=data_decimals,
            ram_offset=None if axi_hp_index is None else 0,
        )

        if axi_hp_index is None:
            @logic
            def _daq_data(self):
                self.comb += [
                    self.data_index.eq(self.pulseburst.count),
                    self.data_we.eq(self.pulseburst.out),
                    If(
                        self.pulseburst.out == 1,
                        self.data.eq(self.input),
                    ),
                ]
        else:
            # bus_error: BoolRegister(readonly=True)
            @logic
            def _daq_data(self, platform, soc):
                if axi_hp_index not in range(4):
                    raise ValueError(f"Only 4 AXI_HP ports are available, the desired index {axi_hp_index} is out of range.")
                hp = getattr(soc.ps7, f"s_axi_hp{axi_hp_index}")
                address = Signal(32)
                ram_base_address = Constant(0xA000000, 32)
                ram_size = 0x2000000
                ram_mask = Constant(ram_size-1, 32)
                self.sync += address.eq(ram_base_address | (ram_mask & Cat(Constant(0, 3), self.pulseburst.count, Constant(0, 32))))
                self.submodules.axiwriter = MigenAxiWriter(
                    address=address,
                    data=self.input,
                    we=self.pulseburst.out,
                    reset=self._trigger,
                    axi_hp=hp,
                )



        
    return _DAQ
