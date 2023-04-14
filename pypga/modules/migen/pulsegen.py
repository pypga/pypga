from typing import Union

from migen import Cat, Constant

from pypga.core import If, MigenModule, Signal
from pypga.core.common import get_length, get_reset_value


class MigenPulseGen(MigenModule):
    def __init__(
        self,
        period: Union[Signal, int] = 0,
        on: Union[Signal, bool] = True,
        high_after_on: bool = True,
        first_cycle_period_offset: int = 0,
    ):
        """
        #DOC: Emits endless pulses
        
        
        Pulse generator that emits a pulse every ``period + 2`` clock cycles.

        Args:
            period: one less than the period of low clock cycles between pulses.
              Set this to a negative number to indicate that the output should
              be constantly high. Set this to zero for a pulse every other clock
              cycle, to one for a pulse every third clock cycle, and so on.
            on: enables the pulse generator sequence when high.
            high_after_on: when True, the output goes high for a single
              clock cycle when ``on`` goes high, otherwise it only goes high
              after the first period.

        Output signals:
            out: the pulse sequence, 0 between pulses and 1 for a single clock
              cycle during a pulse.
        """
        self.out = Signal(reset=0)
        ###
        width = get_length(period)
        period_reset = get_reset_value(period)
        if period_reset < 0:
            raise ValueError("period must be at least 0.")
        period_reset -= first_cycle_period_offset

        self.count = Signal(width, reset=period_reset)
        self.carry = Signal(1, reset=high_after_on)
        self.sync += [
            self.out.eq(self.carry & on),
            If(
                on == 0,  # prepare for the first pulse when off
                self.carry.eq(high_after_on),
                self.count.eq(period - first_cycle_period_offset),
            )
            .Elif(
                self.carry,  # restart countdown
                self.carry.eq(0),
                self.count.eq(period),
            )
            .Else(  # regular countdown
                Cat(self.count, self.carry).eq(Cat(self.count, 0) - 1),
            ),
        ]


class MigenPulseBurstGen(MigenModule):
    def __init__(
        self,
        trigger: Signal,
        reset: Union[Signal, bool] = False,
        pulses: Union[Signal, int] = 0,
        period: Union[Signal, int] = 0,
    ):
        """
        #DOC: make n pulses, Emits after trigger : | | | | |
        
        Pulse generator that a fixed number of pulses every ``period + 2`` clock cycles.

        Args:
            trigger: high triggers a new pulse sequence if the generator is idle.
            reset: sets status to idle and count to zero when high.
            pulses: the number of pulses per burst seqeuence is ``pulses + 1``.
            period: one less than the period of low clock cycles between pulses.
              Set this to a negative number to indicate that the output should
              be constantly high. Set this to zero for a pulse every other clock
              cycle, to one for a pulse every third clock cycle, and so on.

        Output signals:
            out: the pulse sequence, 0 between pulses and 1 for a single clock
              cycle during a pulse.
            count: the current count, going from ``pulses`` to zero during a
              burst sequence and staying zero afterwards.
        """
        self.out = Signal(reset=0)
        self.count = Signal(get_length(pulses), reset=0)
        self.busy = Signal(reset=False)
        ###
        pulsegen_on = Signal(reset=0)
        self.submodules.pulsegen = MigenPulseGen(
            period=period,
            on=pulsegen_on,
            high_after_on=False,
            first_cycle_period_offset=1,
        )
        self.sync += [
            self.out.eq(0),
            pulsegen_on.eq(~reset & (self.busy | trigger)),
            If(
                reset == 1,
                self.out.eq(0),
                self.busy.eq(0),
                self.count.eq(0),
                pulsegen_on.eq(0),
            )
            .Elif(
                self.busy == 0,
                If(
                    trigger == 1,
                    self.busy.eq(1),
                    self.out.eq(1),
                    self.count.eq(pulses),
                ),
            )
            .Else(
                If(
                    self.pulsegen.out == 1,
                    If(
                        self.count == 0,
                        If(trigger == 1, self.out.eq(1), self.count.eq(pulses),).Else(
                            self.busy.eq(0),
                        ),
                    ).Else(
                        self.out.eq(1),
                        self.count.eq(self.count - 1),
                    ),
                )
            ),
        ]
