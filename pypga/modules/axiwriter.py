import numpy as np
from pypga.core import Module, logic
from pypga.core.register import BoolRegister, Register, TriggerRegister
from pypga.modules.migen.axiwriter import MigenAxiWriter



def AXIWriter(axi_hp_index=0):
    class AXIWriter_(Module):
        address: Register(width=32, default=0x0a000000)
        data: Register(width=32, default=0x00000000)

        we: TriggerRegister()
        reset: TriggerRegister()

        error: BoolRegister(readonly=True)
        idle: BoolRegister(readonly=True)        
        ready: BoolRegister(readonly=True)
        
        @logic
        def _connect_to_soc(self, platform, soc):
            hp = getattr(soc.ps7, f"s_axi_hp{axi_hp_index}")
            self.submodules.axiwriter = MigenAxiWriter(
                address=self.address,
                data=self.data,
                we=self.we,
                reset=self.reset,
                axi_hp=hp,
            )

        def read_from_ram(self, offset: int = 0, length: int = 1) -> np.ndarray:
            return self._interface.read_from_ram(offset, length)
        
    return AXIWriter_
