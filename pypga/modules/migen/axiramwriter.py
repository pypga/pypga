from migen import *
from migen import Memory, Signal
from migen.genlib.cdc import MultiReg, PulseSynchronizer
from migen.genlib.fifo import AsyncFIFOBuffered
from migen.genlib.fsm import FSM
from migen_axi.interconnect import axi
from misoc.interconnect.csr import *

from pypga.core import MigenModule, Module, Register, logic

AXI_ADDRESS_WIDTH = 32
AXI_DATA_WIDTH = 64
AXI_BURST_LEN = 16
AXI_ALIGNMENT_BITS = log2_int(AXI_BURST_LEN * AXI_DATA_WIDTH // 8)
AXI_ALIGNED_ADDRESS_WIDTH = AXI_ADDRESS_WIDTH - AXI_ALIGNMENT_BITS


class MigenAxiRamWriter(MigenModule):
    def __init__(
        self,
        data: Signal,
        address: Signal,
        we: Signal,
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
        self.ack = Signal()
        ###
