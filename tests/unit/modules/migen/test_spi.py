import pytest
from migen import Constant, Signal, run_simulation
from migen.fhdl import verilog

from pypga.core import MigenModule
from pypga.modules.migen.spi import MigenSPI


class TestMigenSPI:
    data_width = 20  # there seems to be a bug for "round" numbers like 32
    cs_width = 3
    @pytest.fixture

    def dut(self):
        start = Signal()
        data = Signal(self.data_width)
        if False:
            spi = MigenSPI(
                cs=self.cs_width-1,
                start=start,
                data=data,
                data_width=self.data_width,
                clock_div=4,
                clock_polarity=False,
                clock_phase=False,
                cs_polarity=False,
                lsb_first=False,
                cs_width=self.cs_width,
            )
        else:
            data = Signal(24)
            spi = MigenSPI(
                start=start,  # triggers the next transfer
                cs=0,  # index of chip to select to assert during the next transfer
                data=data,  # data to write during the next transfer
                data_width=24,  # number of bits per transfer
                cs_width=1,  # number of CS wires to use
                cs_polarity=True,  # polarity of the chip-select signals, True = active high
                clock_div=2,  # fraction of the clock rate to use as SPI clock
                clock_polarity=True,  # clock polarity
                clock_phase=False,  # clock phase
                lsb_first=False,  # send LSB rather than MSB first
            )

        spi._start = start
        spi._data = data
        yield spi

    # @pytest.mark.skip
    def test_verilog(self, dut):
        print(verilog.convert(dut))

    start_delay = 5
    def start(self):
        for _ in range(self.start_delay):
            yield 0
        yield 1
        while True:
            yield 0  # 0

    def data(self):
        while True:
            yield 0b11011010011101101001

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
            for cycle in range(300):
                yield dut._data.eq(next(data))
                yield dut._start.eq(next(start))
                # yield dut.miso.eq(Constant(cycle%3%2))  # was removed
                print(
                    f"Cycle {cycle:03d}: start={(yield dut._start)} clk={(yield dut.clk)} cs={(yield dut.cs):0{self.cs_width}b} mosi={(yield dut.mosi)} busy={(yield dut.busy)}", 
                    f"\ndone={(yield dut.spi.cg.done)} reg.sdo={(yield dut.spi.reg.sdo)} reg.shift={(yield dut.spi.reg.shift)} reg.pdo={(yield dut.spi.reg.pdo):0{self.data_width}b}\n"
                )
                yield

        run_simulation(dut, assertions())

