from typing import List, Union

from misoc.cores.spi2 import SPIInterface, SPIMachine, SPIMaster
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
    ):
        if data_width <= 16:
            raise ValueError("This module does not support data_width < 17 bits.")
        # signals to connect to SPI wires
        self.mosi = Signal()
        self.miso = Signal()
        self.clk = Signal()
        self.cs = Signal(cs_width)
        # other signals of interest to the user
        self.read_data = Signal(data_width)
        self.busy = Signal()

        ### logic
        clock_div_width = get_length(clock_div)
        self.submodules.spi = SPIMachine(
            data_width=data_width, 
            div_width=clock_div_width
        )
        self.sync += [
        ]

        self.comb += [
            self.spi.length.eq(data_width),
            self.spi.reg.pdo.eq(data),
            self.read_data.eq(self.spi.reg.pdi),
            self.spi.end.eq(True),
            self.spi.cg.div.eq(clock_div),
            self.spi.load.eq(start),
            self.spi.clk_phase.eq(clock_phase),
            self.spi.reg.lsb_first.eq(lsb_first),
            self.busy.eq(~self.spi.idle),
            self.mosi.eq(self.spi.reg.sdo),
            self.spi.reg.sdi.eq(self.miso),
            self.clk.eq(self.spi.clk_next ^ clock_polarity),
            self.cs.eq(
                (Replicate(self.spi.cs_next, cs_width) 
                & (Constant(1, cs_width) << cs))
                ^ Replicate(cs_polarity, cs_width)    
            ),
            # self.cs.eq(
            #     (Replicate(~self.spi.idle, cs_width) 
            #     & (Constant(1, cs_width) << cs))
            #     ^ Replicate(cs_polarity, cs_width)    
            # ),
            # interface.half_duplex.eq(self.half_duplex.storage),

            # self.data.we.eq(spi.readable),
            # self.readable.status.eq(spi.readable),
            # self.writable.status.eq(spi.writable),

            # interface.half_duplex.eq(self.half_duplex.storage),
            # interface.cs.eq(self.cs.storage),
            # interface.cs_polarity.eq(self.cs_polarity.storage),
            # interface.clk_polarity.eq(self.clk_polarity.storage),
            # interface.offline.eq(self.offline.storage),
            # interface.cs_next.eq(spi.cs_next),
            # interface.clk_next.eq(spi.clk_next),
            # interface.ce.eq(spi.ce),
            # interface.sample.eq(spi.reg.sample),
            # spi.reg.sdi.eq(interface.sdi),
            # interface.sdo.eq(spi.reg.sdo)
        ]
