from pypga.core import TopModule, logic, Register
from pypga.modules.led import FourLeds
import logging


class ExampleDesign(TopModule):
    state0: Register
    state1: Register.custom(size=32, reset=0)
    state2 = Register()  # still worth considering
    led0to3: FourLeds
    led4to7: FourLeds
    # reason for type hint instead of submodule instance: do not call
    # FourLeds.__init__() at class creation

    def __init__(self, a, b=2):
        logging.warning(f"Calling {self}.__init__({a}, {b}).")
        self.led = a


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    # create an interface to a remote board and run the design on it
    pypga_instance = ExampleDesign.run(a=1, b=2, host="rp", board="stemlab125_14")
    # read a register
    print(f"Rate of led0: {pypga_instance.led0to3.led0.rate}")
    # write a register
    pypga_instance.led0to3.led0.rate = 123
    print(f"Updated rate of led0: {pypga_instance.led0to3.led0.rate}")
    # tab expansion also works to find your way through the hierarchy of submodules
