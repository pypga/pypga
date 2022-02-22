from migen import Signal

from pypga.core import Module, Register, TopModule, logic


# a Module is the basic building block in PyPGA. Often it is useful
# to create the Module class from a factory function to allow for
# parametrizations, such as the default_rate here
def SingleLedBlinker(default_rate=2**6):
    counter_width = 32

    class _SingleLedBlinker(Module):
        # define a register that is accessible from Python
        rate: Register.custom(width=counter_width, default=default_rate)

        # programmable logic is marked by the @logic decorator
        @logic
        def _blink(self, platform):
            self.counter = Signal(counter_width)
            self.sync += [self.counter.eq(self.counter + self.rate)]
            self.sync += [platform.request("user_led").eq(self.counter[-1])]

        # all methods without the @logic decorator are regular Python functions
        def speed_up(self):
            self.rate *= 2

        # the regular class constructor is run after connecting to your board
        def __init__(self):
            print(f"Current blink rate: {self.rate} (arbitrary units).")

    return _SingleLedBlinker


# a TopMpodule is one that can be run on a board
class EightLeds(TopModule):
    # submodules are defined using Python type hints with the submodule class
    led0: SingleLedBlinker(default_rate=2**4)
    led1: SingleLedBlinker(default_rate=2**5)
    led2: SingleLedBlinker(default_rate=2**6)
    led3: SingleLedBlinker(default_rate=2**7)
    led4: SingleLedBlinker(default_rate=2**8)
    led5: SingleLedBlinker(default_rate=2**9)
    led6: SingleLedBlinker(default_rate=2**10)
    led7: SingleLedBlinker(default_rate=2**11)


if __name__ == "__main__":
    # now we can try to run the new design on a STEMLab125-14 board with hostname "rp"
    # at first execution, this line will trigger the gatebare build process
    myboard = EightLeds.run(host="rp", board="stemlab125_14")

    # read the value of some registers
    print(f"Rates: {myboard.led0.rate}, {myboard.led1.rate}, {myboard.led2.rate}")
    # change the value of some registers
    myboard.led0.rate = 0
    myboard.led1.rate = 2**11
    myboard.led2.speed_up()
