from typing import List, Union

# from misoc.cores.spi2 import SPIInterface, SPIMachine, SPIMaster
from .spimachine import SPIMachine
from pypga.core import If, MigenModule, Signal

from migen import Case, Cat, Constant, Record, Replicate
from pypga.core.common import get_length


class MigenSPI(MigenModule):
    """A full-duplex SPI interface module."""
    def __init__(
        self,
        # data required for each transfer
        start: Union[Signal, bool] = False,  # triggers the next transfer
        cs: Union[Signal, int] = 0,  # index of chip to select to assert during the next transfer
        data: Union[Signal, int] = 0,  # data to write during the next transfer
        # SPI settings
        data_width: int = 32,  # number of bits per transfer
        cs_width: int = 1,  # number of CS wires to use
        cs_polarity: bool = False,  # polarity of the chip-select signals, True = active high
        clock_div: int = 32,  # fraction of the clock rate to use as SPI clock
        clock_polarity: bool = False,  # clock polarity
        clock_phase: bool = False,  # clock phase
        lsb_first: bool = False,  # send LSB rather than MSB first
        leading_halfcycles: Union[Signal, int] = 1,
        trailing_halfcycles: Union[Signal, int] = 1,
        idle_halfcycles: Union[Signal, int] = 1,
    ):
        if data_width <= 16:
            raise ValueError("This module does not support data_width < 17 bits.")
        # Signals to connect to SPI wires
        self.mosi = Signal()
        # Currently, MISO is not implemented
        # self.miso = Signal()
        self.clk = Signal()
        self.cs = Signal(cs_width)
        # Other signals of interest to the user
        # self.read_data = Signal(data_width)
        self.busy = Signal()

        ### logic
        self.submodules.spi = SPIMachine(
            data_width=data_width, 
            clock_div=clock_div,
            leading_halfcycles=leading_halfcycles,
            trailing_halfcycles=trailing_halfcycles,
            idle_halfcycles=idle_halfcycles
        )
        self.sync += [
        ]

        self.comb += [
            self.spi.reg.pdo.eq(data),
            # self.read_data.eq(self.spi.reg.pdi),
            self.spi.start.eq(start),
            self.spi.clk_phase.eq(clock_phase),
            self.busy.eq(~self.spi.idle),
            self.mosi.eq(self.spi.reg.sdo),
            # self.spi.reg.sdi.eq(self.miso),
            self.clk.eq(self.spi.clk ^ clock_polarity),
            self.cs.eq(
                (Replicate(self.spi.cs, cs_width) 
                & (Constant(1, cs_width) << cs))
                ^ Replicate(cs_polarity, cs_width)    
            ),
        ]
