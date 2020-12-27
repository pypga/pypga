from pypga.core import Module, logic, Register
from pypga.modules.led import FourLeds
import logging
from migen import Signal


class Top(Module):
    ### FPGA definition ###
    state0: Register
    state1: Register.custom(size=32, reset=0)
    #state2 = Register()  # still worth considering
    led0to3: FourLeds
    led4to7: FourLeds
    # reason for type hint instead of submodule instance: do not call
    # FourLeds.__init__() to avoid

    ### interface logic ###
    def change_state_example(self, value):
        print("old:", self.state0)
        self.state0 = value
        print("new:", self.state0)

    # TODO: interface creation@add_client_creation(board="125-14")
    def __init__(self, a, b):
        logging.warning(f"Calling {self}.__init__({a}, {b}).")
        self.state = a

    # TODO: classmethod for interface creation if init-decorator does not work
    # @classmethod
    # def connect(cls, hostname):
    #     cls()



# example interface creation
# myclient = Top(a=7, b=2, hostname=3, board_type="stemlab125_14-125-14")
# print(myclient.led0to3.led0_state)
# myclient.led0to3.led0_state = 0
# myclient.led0to3.blink()
# plus tab expansion works