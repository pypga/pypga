from migen import TSTriple, Cat, Signal
from pypga.core import Module, logic, MigenModule
from pypga.core.register import Register


class MigenGpio(MigenModule):
    def __init__(self, gpio_pins, is_output, output):
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
        tst = TSTriple(width)
        self.specials += tst.get_tristate(gpio_pins)
        self.comb += [
            tst.oe.eq(is_output),
            tst.o.eq(output),
            self.input.eq(tst.i)
        ]
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
            exp = platform.request("exp")
            gpio_pins = Cat(exp.p, exp.n)  #[:width]
            ###
            self.submodules.gpio = MigenGpio(
                gpio_pins=gpio_pins,
                is_output=self.is_output,
                output=self.output,
            )
            self.comb += self.input.eq(self.gpio.input)

    return _ExampleGpio
