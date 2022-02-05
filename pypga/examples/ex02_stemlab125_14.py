from pypga.boards.stemlab125_14.modules.clock import Clock
from pypga.boards.stemlab125_14.modules.dac import Dac
from pypga.boards.stemlab125_14.modules.gpio import ExampleGpio
from pypga.core import TopModule, logic
from pypga.core.register import Register
from pypga.modules.awg import Awg
from pypga.modules.counter import Counter
from pypga.modules.pulsegen import PulseGen


class MyStemlabTest(TopModule):
    _clock: Clock()
    _dac: Dac()
    awg: Awg(data=[i for i in range(2 ** 13 - 1)])
    gpio: ExampleGpio(set_from_python=False)
    pulsegen0: PulseGen(default_period=1111)
    pulsegen1: PulseGen(high_after_on=False)

    @logic
    def _connection(self):
        self.comb += [
            self._dac.out2.eq(self.awg.out),
            self.gpio.output[1].eq(self.awg.done),
            self.gpio.output[0].eq(self.pulsegen1.out),
            self.gpio.is_output.eq(0x0F0F),  # 0-3 outputs, 4-7 inputs
        ]


if __name__ == "__main__":
    import time

    m = MyStemlabTest.run(host="rp")
    try:
        m.pulsegen0.on = True
        print(m.pulsegen0.on)
        # pulse generator
        m.pulsegen0.period = 1000
        time.sleep(1)
        m.pulsegen0.on = False
        time.sleep(1)
        m.pulsegen0.on = True
        m.awg.period = 10

    finally:
        m.stop()
