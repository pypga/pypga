from migen import *
from migen.genlib.fsm import FSM, NextState
from misoc.interconnect.csr import *
from misoc.interconnect.stream import *
from misoc.interconnect import wishbone


class ClockGen(Module):
    def __init__(self, width):
        # Cycle duration - 1
        self.div = Signal(width)
        # If `extend` is asserted, the next half cycle is
        # extended by the LSB of `div`
        self.extend = Signal()
        # Half cycle done
        self.done = Signal()
        # Continue counting or re-load counter
        self.count = Signal()

        ###

        cnt = Signal(width - 1)
        cnt_done = Signal()
        do_extend = Signal()

        self.comb += [
            cnt_done.eq(cnt == 0),
            self.done.eq(cnt_done & ~do_extend)
        ]
        self.sync += [
            If(self.count,
                If(cnt_done,
                    If(do_extend,
                        do_extend.eq(0)
                    ).Else(
                        #
                        cnt.eq(self.div[1:]),
                        do_extend.eq(self.extend & self.div[0])
                    )
                ).Else(
                    cnt.eq(cnt - 1)
                )
            )
        ]


class Register(Module):
    def __init__(self, width):
        # Parallel data out (to serial)
        self.pdo = Signal(width)
        # Parallel data out (from serial)
        self.pdi = Signal(width)
        # Serial data out (from parallel)
        self.sdo = Signal(reset_less=True)
        # Serial data in
        # Must be sampled at a higher layer at self.sample
        self.sdi = Signal()
        # Transmit LSB first
        self.lsb_first = Signal()
        # Load shift register from pdo
        self.load = Signal()
        # Shift SR
        self.shift = Signal()
        # Not used here. Use in Interface to sample into sdo.
        self.sample = Signal()

        ###

        sr = Signal(width, reset_less=True)

        self.comb += [
            self.pdi.eq(Mux(self.lsb_first,
                Cat(sr[1:], self.sdi),
                Cat(self.sdi, sr[:-1])))
        ]
        #
        self.sync += [
            If(self.shift,
                sr.eq(self.pdi),
                self.sdo.eq(Mux(self.lsb_first, self.pdi[0], self.pdi[-1]))
            ),
            If(self.load,
                sr.eq(self.pdo),
                self.sdo.eq(Mux(self.lsb_first, self.pdo[0], self.pdo[-1]))
            )
        ]


class SPIMachine(Module):
    def __init__(self, data_width=32, div_width=8):
        # Number of bits to transfer - 1
        self.length = Signal(max=data_width)
        # Freescale CPHA
        self.clk_phase = Signal()

        # Combinatorial cs and clk signals to be registered
        # in Interface on ce
        self.clk_next = Signal()
        self.cs_next = Signal()
        self.ce = Signal()

        # No transfer is in progress
        self.idle = Signal()
        # When asserted and writiable, load register and start transfer
        self.load = Signal()
        # reg.pdi valid and all bits transferred
        # Asserted at the end of the last hold interval.
        # For one cycle (if the transfer completes the transaction) or
        # until load is asserted.
        self.readable = Signal()
        # Asserted before a transfer until the data has been loaded
        self.writable = Signal()
        # When asserted during load end the transaction with
        # this transfer.
        self.end = Signal()

        self.submodules.reg = reg = Register(data_width)
        self.submodules.cg = cg = ClockGen(div_width)

        ###

        # Bit counter
        n = Signal.like(self.length, reset_less=True)
        # Capture end for the in-flight transfer
        end = Signal(reset_less=True)

        self.comb += [
                self.ce.eq(cg.done & cg.count)
        ]
        self.sync += [
                If(reg.load,
                    n.eq(self.length - 1),
                    end.eq(self.end)
                ),
                If(reg.shift,
                    n.eq(n - 1)
                )
        ]

        fsm = FSM("IDLE")
        self.submodules += fsm

        fsm.act("IDLE",
                self.idle.eq(1),
                self.writable.eq(1),
                self.cs_next.eq(0),#1
                If(self.load,
                    cg.count.eq(1),
                    NextState("START1")
                )
        )
        fsm.act("START1",
                self.cs_next.eq(1),
                cg.count.eq(1),
                cg.extend.eq(1),
                self.clk_next.eq(0),
                If(cg.done,
                   NextState("START2")
                )
        )
        fsm.act("START2",
                self.cs_next.eq(1),
                cg.count.eq(1),
                cg.extend.eq(1),
                self.clk_next.eq(0),
                If(cg.done,
                    If(self.clk_phase,
                        NextState("PRE"),
                    ).Else(
                        cg.extend.eq(1),
                        reg.load.eq(1),
                        NextState("SETUP"),
                    )
                )
        )
        fsm.act("PRE",
                # dummy half cycle after asserting CS in CPHA=1
                self.cs_next.eq(1),
                cg.count.eq(1),
                cg.extend.eq(1),
                self.clk_next.eq(0),
                reg.load.eq(1),
                If(cg.done,
                    NextState("SETUP")
                )
        )
        fsm.act("SETUP",
                self.cs_next.eq(1),
                cg.count.eq(1),
                self.clk_next.eq(self.clk_phase),
                If(cg.done,
                    reg.sample.eq(1),
                    NextState("HOLD")
                )
        )
        fsm.act("HOLD",
                self.cs_next.eq(1),
                cg.count.eq(1),
                cg.extend.eq(1),
                self.clk_next.eq(~self.clk_phase),
                If(cg.done,
                    If(n == 0,
                        self.readable.eq(1),
                        self.writable.eq(1),
                        If(end,
                            self.clk_next.eq(0),
                            self.writable.eq(0),
                            If(self.clk_phase,
                                #self.cs_next.eq(0),
                                NextState("WAIT")
                            ).Else(
                                NextState("POST")
                            )
                        ).Elif(self.load,
                            reg.load.eq(1),
                            NextState("SETUP")
                        ).Else(
                            cg.count.eq(0)
                        )
                    ).Else(
                        reg.shift.eq(1),
                        NextState("SETUP")
                    )
                )
        )
        fsm.act("POST",
                # dummy half cycle before deasserting CS in CPHA=0
                cg.count.eq(1),
                self.cs_next.eq(1),
                If(cg.done,
                    NextState("WAIT")
                )
        )
        fsm.act("WAIT",
                # dummy half cycle to meet CS deassertion minimum timing
                If(cg.done,
                    NextState("IDLE")
                ).Else(
                    cg.count.eq(1),
                    self.cs_next.eq(1)
                )
        )
        # fsm.act("END",
        #         cg.count.eq(1),
        #         self.cs_next.eq(1),#1
        #         If(cg.done,
        #             NextState("IDLE")
        #         )
        # )