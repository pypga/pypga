from ....core import TopModule, logic
from .adc import Adc
from .clock import Clock
from .dac import Dac


class Stemlab125_14(TopModule):
    clock: Clock()
    dac: Dac()
    adc: Adc
    #
    # @logic
    # def _connect_dac_to_pll(self):
    #     pass
    #
    # @logic
    # def _shortcuts(self):
    #     self.out1 = self.dac.out1
    #     self.out2 = self.dac.out2
