from ....core import TopModule, logic
from .dac import Dac
from .clock import Clock

class Stemlab125_14(TopModule):
    zclock: Clock

    dac: Dac

    @logic
    def _connect_dac_to_pll(self):
        pass

    @logic
    def _shortcuts(self):
        self.out1 = self.dac.out1
        self.out2 = self.dac.out2
