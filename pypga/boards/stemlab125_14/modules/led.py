from migen import *

from ..core import Module, Register, logic


class Led(Module):
    status: Register.custom(width=8, default=0)

    @logic
    def _change(self, platform):
        self.sync += [platform.request("user_led").eq(self.status[i]) for i in range(8)]
