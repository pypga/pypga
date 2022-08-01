from ....core import TopModule, logic
from .adc import Adc
from .dac import Dac


class Stemlab125_14(TopModule):
    _dac: Dac()
    _adc: Adc()
    