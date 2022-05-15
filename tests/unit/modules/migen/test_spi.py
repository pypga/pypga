import pytest
from migen import Constant, Signal, run_simulation
from migen.fhdl import verilog

from pypga.core import MigenModule
from pypga.modules.migen.spi import MigenSPI


class TestMigenSPI:
    data_width = 16

    @pytest.fixture
    def dut(self):
        start = Signal()
        data = Signal(self.data_width)
        spi = MigenSPI(
            start=start,
            data=data,
            data_width=self.data_width,
            clock_div=3,
            clock_polarity=True,
            cs_polarity=False,
        )
        spi._start = start
        spi._data = data
        yield spi

    # @pytest.mark.skip
    def test_verilog(self, dut):
        print(verilog.convert(dut))

    start_delay = 8
    def start(self):
        for _ in range(self.start_delay):
            yield 0
        yield 1
        while True:
            yield 0  # 0

    def data(self):
        while True:
            yield 1234

    def simulator(self):
        """Generator returning expected values for out, busy, and count."""
        start = self.start()
        data = self.data()
        while True:
            yield 0

    def test_spi(self, dut):
        print(f"\n\nStart {self.__class__.__name__}")
        data = self.data()
        start = self.start()
        simulator = self.simulator()
        def assertions():
            for cycle in range(100):
                yield dut._data.eq(next(data))
                yield dut._start.eq(next(start))
                print(
                    f"Cycle {cycle:02d}: start={(yield dut._start)} clk={(yield dut.clk)} cs={(yield dut.cs)} mosi={(yield dut.mosi)} busy={(yield dut.busy)}",
                    f"Cycle {cycle:02d}: start={(yield dut._start)} count={(yield dut.spi.cg.count)} done={(yield dut.spi.cg.done)} extend={(yield dut.spi.cg.extend)} div={(yield dut.spi.cg.div)} length={(yield dut.spi.length)} n={(yield dut.spi.n)}"
                )
                yield

        run_simulation(dut, assertions())
