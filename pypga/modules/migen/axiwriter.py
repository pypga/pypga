from pypga.core import MigenModule
from migen import Cat, If, Signal
from typing import Any
from pypga.modules.migen.counter import MigenCounter

class MigenAxiWriter(MigenModule):
    def __init__(
        self,
        data: Signal,
        address: Signal,
        we: Signal,
        trigger_count: Signal,
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
        self.idle = Signal()
        self.error = Signal()
        self.aw_valid = Signal()
        self.w_valid = Signal()
        self.aw_ready = Signal()
        self.w_ready = Signal()
        ###

        # add a counter to keep the trigger high for a few cycles
        self.submodules.counter = MigenCounter(
            start=trigger_count,
            stop=0,
            step=1,
            on=True,
            reset=we,
            direction="down",
        )

        aw = axi_hp.aw
        w = axi_hp.w
        b = axi_hp.b
        
        aw_valid = Signal()
        w_valid = Signal()
        t = Signal()
        self.sync += [
            t.eq(~self.counter.done),
            If(
                (t==1), 
                aw_valid.eq(1)
            ).Elif(
                aw.ready,
                aw_valid.eq(0),
            ).Else(
                aw_valid.eq(0),
            ),
            If(
                (t==1),
                w_valid.eq(1)
            ).Elif(
                w.ready,
                w_valid.eq(0),
            ).Else(
                w_valid.eq(0),
            ),
        ]
        
        # address part
        self.comb += [
            aw.addr.eq(address),
            aw.id.eq(0), 
            aw.burst.eq(0),
            aw.len.eq(0),  # Number of transfers in burst (0->1 transfer, 1->2 transfers...).
            aw.size.eq(3), # Width of burst: 3 = 8 bytes = 64 bits.
            aw.cache.eq(0b1111),
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

        #         # Busy generation
        #         remaining_sys = Signal(AXI_ADDRESS_WIDTH - log2_int(AXI_DATA_WIDTH//8))
        #         self.sync += [
        #            If(self.start, remaining_sys.eq(self.length << log2_int(AXI_BURST_LEN))),
        #            If(fifo.readable & fifo.re, remaining_sys.eq(remaining_sys - 1))
        #         ]
        #         self.comb += self.busy.eq(re_sys != 0)

        #         # status part
        self.comb += b.ready.eq(1)
        #         self.sync += [
        #             If(self.start.re, self.bus_error.status.eq(0)),
        #             If(b.valid & b.ready & (b.resp != axi.Response.okay),
        #                 self.bus_error.status.eq(1))
        #         ]

