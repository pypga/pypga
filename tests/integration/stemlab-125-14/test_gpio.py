import pytest

from pypga.core import TriggerRegister, Register, TopModule, logic
from pypga.boards.stemlab125_14.modules.gpio import get_migen_gpio


def GPIO(width=16):
    class _GPIO(TopModule):
        output: Register(default=0, width=4, readonly=False)
        input: Register(default=0, width=16, readonly=True)

        @logic
        def _connect(self, platform):
            self.submodules.gpio = get_migen_gpio(
                platform=platform,
                is_output=0b0000000000001111,
                output=self.output,
            )
            self.sync += self.input.eq(self.gpio.input)

    return _GPIO


@pytest.fixture(scope="module")
def gpio(host, board):
    dut = GPIO().run(host=host, board=board)
    yield dut
    dut.stop()


class TestSPI:
    @pytest.fixture
    def dut(self, gpio):
        yield gpio

    def test_gpio(self, dut):
        print(dut.output)
        for i in range(16):
            dut.output = i
            print(dut.output, dut.input)
