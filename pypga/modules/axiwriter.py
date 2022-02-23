import numpy as np
from pypga.core import Module, logic
from pypga.core.register import BoolRegister, Register, TriggerRegister
from pypga.modules.migen.axiwriter import MigenAxiWriter



def AXIWriter(axi_hp_index=0):
    class AXIWriter_(Module):
        address: Register(width=32, default=0x0a000000)
        data: Register(width=32, default=0x00000000)

        t: TriggerRegister()
        trigger_count: Register(width=16, reset=100)

        aw_ready: BoolRegister(readonly=True)
        aw_valid: BoolRegister(readonly=True)        
        w_ready: BoolRegister(readonly=True)
        w_valid: BoolRegister(readonly=True)
        
        @logic
        def _connect_to_soc(self, platform, soc):
            hp = getattr(soc.ps7, f"s_axi_hp{axi_hp_index}")
            self.submodules.axiwriter = MigenAxiWriter(
                data=self.data,
                address=self.address,
                we=self.t,
                trigger_count=self.trigger_count,
                axi_hp=hp,
            )

        def read_from_ram(self, offset: int = 0, length: int = 1) -> np.ndarray:
            return self._interface.read_from_ram(offset, length)
        
    return AXIWriter_
