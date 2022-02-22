from pypga.core import MigenModule
from migen import Signal


class MigenAxiWriter(MigenModule):
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
