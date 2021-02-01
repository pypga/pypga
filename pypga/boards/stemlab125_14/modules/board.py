from ....core import TopModule, logic
from .dac import Dac
from .adc import Adc
from .clock import Clock
from .led import Led

class Stemlab125_14(TopModule):
    clock: Clock
    dac: Dac
    adc: Adc
    led: Led
