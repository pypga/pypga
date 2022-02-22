from pypga.boards.stemlab125_14.modules.clock import Clock
from pypga.boards.stemlab125_14.modules.dac import Dac
from pypga.core import TopModule, logic
from pypga.modules.awg import Awg
from pypga.modules.daq import DAQ


class MyStemlabTest(TopModule):
    _clock: Clock()
    _dac: Dac()
    awg: Awg(
        data_depth=1024,
        data_width=14,
        data_decimals=13,
        initial_data=list(range(0, 2**13, 8)),
        sampling_period_width=32,
        default_sampling_period_cycles=10,
        repetitions_width=32,
        default_repetitions=1,
    )
    daq: DAQ(
        data_depth=2048,
        data_width=14,
        data_decimals=13,
        sampling_period_width=32,
        default_sampling_period=10,
    )

    @logic
    def _connection(self):
        self.comb += [
            self._dac.out2.eq(self.awg.out),
            self.daq.input.eq(self.awg.out),
        ]


if __name__ == "__main__":
    m = MyStemlabTest.run(host="rp")
    try:
        m.awg.on = True
        m.awg.data = range(0, 8000, 8)
        m.awg.period = 11
        m.daq.on = True

    finally:
        m.stop()
