from typing import Any, Union

from pypga.core import MigenModule

from migen import Cat, ClockDomainsRenamer, Constant, If, Signal
from migen.genlib.fifo import AsyncFIFOBuffered


class MigenAxiWriter(MigenModule):
    def __init__(
        self,
        address: Union[Signal, Constant, int],
        data: Signal,
        we: Signal,
        reset: Union[Signal, Constant, bool], 
        axi_hp: Any,  # an AXI_HP instance
    ):
        """
        A Module that writes the data given to it to RAM.

        Args:
            data: Data to write. Must be a 64-bit register.
            address: RAM address to write to. Must be a 32-bit register.
            we: Write enable signal, data is written when high.

        Output signals:
            ack: .
        """
        # high-level signals
        self.idle = Signal()
        self.error = Signal()
        # low-level signals
        self.ready = Signal()
        # obsolete
        self.aw_valid = Signal()
        self.w_valid = Signal()
        self.aw_ready = Signal()
        self.w_ready = Signal()

        ###
        fifo = ClockDomainsRenamer({"write": "sys", "read": "sys"})(AsyncFIFOBuffered(64, 32))  # 64 bits, 32 samples
        self.submodules += fifo

        aw = axi_hp.aw
        w = axi_hp.w
        b = axi_hp.b

        aw_valid = Signal()
        w_valid = Signal()

        self.sync += [
            If(
                (we==1), 
                aw_valid.eq(1)
            ).Elif(
                aw.ready,
                aw_valid.eq(0),
            ).Else(
                aw_valid.eq(0),
            ),
            If(
                (we==1),
                w_valid.eq(1)
            ).Elif(
                w.ready,
                w_valid.eq(0),
            ).Else(
                w_valid.eq(0),
            ),
        ]
        
        # address part
        self.offset = Signal(25, reset=0)  # 32 MB
        self.sync += If(
            reset == 1,
            self.offset.eq(0)
        ).Else(
            self.offset.eq(self.offset + 0)
        )

        self.comb += [
            aw.id.eq(0), 
            aw.addr.eq(address + self.offset),
            aw.len.eq(0),  # Number of transfers in burst (0->1 transfer, 1->2 transfers...).
            aw.size.eq(3), # Width of burst: 3 = 8 bytes = 64 bits.
            aw.burst.eq(0),  # no burst, fixed width
            aw.cache.eq(0b1111),  # bufferable, and cacheable
            aw.valid.eq(aw_valid),
            self.aw_valid.eq(aw_valid),
            self.aw_ready.eq(aw.ready),
        ]
        
        # data part
        self.comb += [
            w.id.eq(0),
            w.data.eq(Cat(data, data)),
            w.strb.eq(0b11111111),
            w.last.eq(w_valid),
            w.valid.eq(w_valid),
            self.w_valid.eq(w_valid),
            self.w_ready.eq(w.ready),
        ]
        #         beat_count = Signal(max=AXI_BURST_LEN)

        #         self.sync += [
        #             If(w.valid & w.ready,
        #                 w.last.eq(0),
        #                 If(w.last,
        #                     beat_count.eq(0)
        #                 ).Else(
        #                     If(beat_count == AXI_BURST_LEN-2, w.last.eq(1)),
        #                     beat_count.eq(beat_count + 1)
        #                 )
        #             )
        #         ]

        #         # status part
        self.comb += b.ready.eq(1)
        #         self.sync += [
        #             If(self.start.re, self.bus_error.status.eq(0)),
        #             If(b.valid & b.ready & (b.resp != axi.Response.okay),
        #                 self.bus_error.status.eq(1))
        #         ]

