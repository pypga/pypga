import math
import time

import numpy as np
import pytest
from migen import Cat, Constant
from pypga.core import TriggerRegister, Register, TopModule, logic
from pypga.boards.stemlab125_14.modules.gpio import get_migen_gpio
from pypga.modules.migen.spi import MigenSPI
from pypga.modules.migen.pulsegen import MigenPulseBurstGen


def SPI(width=24):
    """Creates an SPI module in loopback configuration, i.e. MISO connected to MOSI."""
    class _SPI(TopModule):
        write_data: Register(default=0, width=width, readonly=False)
        read_data: Register(default=0, width=width, readonly=True)
        start: TriggerRegister()

        _digital_outputs: Register(default=0, width=8, readonly=True)
        _digital_inputs: Register(default=0, width=8, readonly=True)

        @logic
        def _connect(self, platform):
            self.submodules.gpio = get_migen_gpio(
                platform=platform,
                is_output=0x00ff,
                output=Cat([self._digital_outputs, Constant(0, 8)]),
            )
            self.submodules.spi = MigenSPI(
                start=self.start,  # triggers the next transfer
                cs=1,  # index of chip to select to assert during the next transfer
                data=self.write_data,  # data to write during the next transfer
                data_width=width,  # number of bits per transfer
                cs_width=2,  # number of CS wires to use
                cs_polarity=False,  # active of the chip-select signals, True = active high
                clock_div=2, #10, #128,  # fraction of the clock rate to use as SPI clock
                clock_polarity=False,  # clock polarity
                clock_phase=True,  # clock phase
                lsb_first=False,  # send LSB rather than MSB first
            )
            self.comb += self.spi.miso.eq(self.spi.mosi)  # havent tested miso yet
            self.sync += self.read_data.eq(self.spi.read_data)

            self.submodules.pulseburst = MigenPulseBurstGen(
                trigger=self.start,
                reset=False,
                pulses=10,
                period=125_000,
            )
            self.sync += self._digital_outputs.eq(Cat([
                self.spi.mosi, 
                self.spi.clk, 
                self.spi.cs[0], 
                self.spi.cs[1], 
                self.spi.busy, 
                self.pulseburst.out, 
                self.pulseburst.busy, 
                self.pulseburst.count[-1],
            ]))  # PIN0 = MOSI, PIN1 = CLK, PIN3 = CS

            self.comb += self._digital_inputs.eq(self.gpio.input[8:])

        start_pulsegen: TriggerRegister()
        test1: TriggerRegister()
        test2: TriggerRegister()


    return _SPI


@pytest.fixture(scope="module")
def spi(host, board):
    dut = SPI().run(host=host, board=board)
    yield dut
    dut.stop()


class TestSPI:
    @pytest.fixture
    def dut(self, spi):
        yield spi

    @pytest.mark.parametrize("data", [[i*0+128, 64, 253] for i in range(256)])
    def test_spi(self, dut, data):
        time.sleep(0.05)
        print(bin(dut._digital_outputs))
        read_data = dut.read_data
        dut.write_data = 0
        assert dut.write_data == 0
        data = int.from_bytes(data, "big")
        dut.write_data = data
        assert dut.read_data == read_data
        print(bin(dut._digital_outputs))
        dut.start()
        print(bin(dut._digital_outputs))
        assert dut.write_data == data, (hex(dut.write_data), hex(data))
        assert dut.read_data == data, (hex(dut.read_data), hex(data))
        print(bin(dut._digital_outputs))

    # def test_pulses(self, dut):
    #     for i in range(10):
    #         dut.test1()
    #         dut.test2()
    #         dut.start_pulsegen()
    #         time.sleep(1.1)

    # def test_1(self, dut):
    #     for i in range(10):
    #         dut.test1()
    #         time.sleep(1)

    # def test_2(self, dut):
    #     for i in range(10):
    #         dut.test2()
    #         time.sleep(1)


    def test_spi(self, dut):
        time.sleep(0.05)
        print(bin(dut._digital_outputs))
        read_data = dut.read_data
        dut.write_data = 0
        assert dut.write_data == 0
        values = 1024
        factor = 2**20 // values
        for i in range(10):
            for code in range(values):
                code = (code * factor) << 4
                code = min(code, 2**24 - 1)
                dut.write_data = code
                print(bin(dut._digital_outputs))
                dut.start()
        
