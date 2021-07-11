from pypga.core import TopModule, logic
from pypga.modules.awg import ExampleRomAwg
from pypga.modules.pulsegen import ExamplePulseGen, MigenPulseGen
from pypga.modules.counter import ExampleCounter
from pypga.boards.stemlab125_14.modules.dac import Dac
from pypga.boards.stemlab125_14.modules.clock import Clock
from pypga.boards.stemlab125_14.modules.gpio import ExampleGpio
from pypga.core.register import Register


class MyStemlabTest(TopModule):
    _clock: Clock()
    _dac: Dac()
    awg1: ExampleRomAwg(data=[i for i in range(2**13-1)])
    awg2: ExampleRomAwg(data=[i for i in reversed(range(2**14-1))])
    gpio: ExampleGpio(set_from_python=False)
    pulsegen0: ExamplePulseGen(default_period=1111)
    pulsegen1: ExamplePulseGen(high_after_on=False)

    @logic
    def _connection(self):
        self.comb += [
            self._dac.out1.eq(self.awg1.value),
            self._dac.out2.eq(self.awg2.value),
            self.gpio.output[0].eq(self.pulsegen0.out),
            self.gpio.output[1].eq(self.pulsegen1.out),
            self.gpio.is_output.eq(0x0F0F),  # 0-3 outputs, 4-7 inputs
        ]    
    

if __name__ == "__main__":
    import time
    m = MyStemlabTest.run(host="rp")
    try:
        m.pulsegen0.on = True
        print(m.pulsegen0.on)
        m.a = 0
        print(m.a)
        # pulse generator
        m.pulsegen0.period = 1000
        time.sleep(1)
        m.pulsegen0.on = False
        time.sleep(1)
        m.pulsegen0.on = True

    finally:
        m.stop()