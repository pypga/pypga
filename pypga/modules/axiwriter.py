import numpy as np
from pypga.core import Module, logic
from pypga.core.register import BoolRegister, Register, TriggerRegister

from migen import Cat, If, Signal


def AXIWriter(axi_hp_index=0):
    class AXIWriter_(Module):
        address: Register(width=32, default=0x0a000000)
        data: Register(width=32, default=0x00000000)

        t: TriggerRegister()

        aw_t: BoolRegister()
        aw_ready: BoolRegister(readonly=True)
        aw_valid: BoolRegister(readonly=True)        
        
        w_t: BoolRegister()
        w_ready: BoolRegister(readonly=True)
        w_valid: BoolRegister(readonly=True)
        
        def read_from_ram(self, offset: int = 0, length: int = 1) -> np.ndarray:
            return self._interface.read_from_ram(offset, length)

        @logic
        def _connect_to_soc(self, platform, soc):
            hp = getattr(soc.ps7, f"s_axi_hp{axi_hp_index}")
            aw = hp.aw
            w = hp.w
            b = hp.b
            
            aw_valid = Signal()
            w_valid = Signal()
            lastt = Signal()
            lasttt = Signal()
            lastttt = Signal()
            lasttttt = Signal()
            t = Signal()
            self.sync += [
                lastt.eq(self.t),
                lasttt.eq(lastt),
                lastttt.eq(lasttt),
                lasttttt.eq(lastttt),
                t.eq(self.t | lastt | lasttt | lastttt | lasttttt),
                If(
                    (self.aw_t | self.t), 
                    aw_valid.eq(1)
                ).Elif(
                    aw.ready,
                    aw_valid.eq(0),
                ).Elif(
                    (self.aw_t == 0),
                    aw_valid.eq(0),
                ),
                If(
                    (self.w_t | self.t),
                    w_valid.eq(1)
                ).Elif(
                    w.ready,
                    w_valid.eq(0),
                ).Elif(
                    (self.w_t == 0),
                    w_valid.eq(0),
                ),
            ]
            
            # address part
            self.comb += [
                aw.addr.eq(self.address),
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
                w.data.eq(Cat(self.data, self.data)),
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
        
    return AXIWriter_
