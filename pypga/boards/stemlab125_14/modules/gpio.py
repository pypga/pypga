from migen import Cat, Signal, TSTriple

from pypga.core import MigenModule, Module, logic
from pypga.core.register import Register


class MigenGpio(MigenModule):
    def __init__(self, gpio_pins, is_output=0, output=0):
        """
        General purpose I/O pin interface.

        Args:
            gpio_pins: the I/O pins to connect to.

        Input signals:
            output: the level to set the pins to.
            is_output: which pins to use as outputs.

        Output signals:
            input: the level of the pins when they are used as input.
        """
        width = len(gpio_pins)
        self.input = Signal(width)
        is_output_signal = Signal(width)
        output_signal = Signal(width)
        self.comb += [
            is_output_signal.eq(is_output),
            output_signal.eq(output),
        ]
        tst = [TSTriple(1) for _ in range(width)]
        self.specials += [tst[i].get_tristate(gpio_pins[i]) for i in range(width)]
        for i in range(width):
            self.comb += [
                tst[i].oe.eq(is_output_signal[i]), 
                tst[i].o.eq(output_signal[i]), 
                self.input[i].eq(tst[i].i)
        ]


def get_migen_gpio(platform, is_output: Signal, output: Signal) -> MigenGpio:
    """
    Returns an interface to all general purpose I/O pins of the board.

    Args:
        platform: platform object for the design.
        output: the signal to set the pins to.
        is_output: array with 1-bit signals indicating which pins to use as outputs.

    Returns:
        A MigenGpio instance interfacing the pins.
    """
    exp = platform.request("exp")
    gpio_pins = [gpio[i] for gpio in [exp.p, exp.n] for i in range(len(gpio))]
    return MigenGpio(gpio_pins, is_output=is_output, output=output)


# TODO: Can we set these parameters, especially pulldown=true?
# set_property IOSTANDARD LVCMOS33 [get_ports {exp_p_io[*]}]
# set_property IOSTANDARD LVCMOS33 [get_ports {exp_n_io[*]}]
# set_property SLEW       FAST     [get_ports {exp_p_io[*]}]
# set_property SLEW       FAST     [get_ports {exp_n_io[*]}]
# set_property DRIVE      8        [get_ports {exp_p_io[*]}]
# set_property DRIVE      8        [get_ports {exp_n_io[*]}]
# set_property PULLDOWN   TRUE     [get_ports {exp_p_io[*]}]
# set_property PULLDOWN   TRUE     [get_ports {exp_n_io[*]}]


def ExampleGpio(width=16, set_from_python=False):
    class _ExampleGpio(Module):
        """
        Support for expansion connector DIO pins.

        All signals are 16-bit wide by default. The first 8 correspond to the DIO_P* pins,
        the last 8 to the DIO_N* pins.

        Input signals:
            is_output: sets the direction of a pin, high = output.
            output: sets the value of a pin, high = 3.3V.

        Output signals:
            input: returns the reading of a pin, high = 3.3V.
        """

        is_output: Register(width=width, default=0, readonly=not set_from_python)
        output: Register(width=width, default=0, readonly=not set_from_python)
        input: Register(width=width, default=0, readonly=True)

        @logic
        def _setup(self, platform):

            ###
            self.submodules.gpio = get_migen_gpio(
                platform=platform,
                is_output=self.is_output,
                output=self.output,
            )
            self.comb += self.input.eq(self.gpio.input)

    return _ExampleGpio
