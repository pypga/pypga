from pypga.modules.led import FourLeds
from pypga.boards.stemlab125_14.modules.board import Stemlab125_14
from pypga.core import TopModule
import logging


class MyStemlabDesign(TopModule):
    board: Stemlab125_14
    led0to3: FourLeds
    led4to7: FourLeds


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    pypga_instance = MyStemlabDesign.run(host="rp", board="stemlab125_14")
    # read a register
    print(f"Rate of led0: {pypga_instance.led0to3.led0.rate}")
    # write a register
    pypga_instance.led0to3.led0.rate = 123
    print(f"Updated rate of led0: {pypga_instance.led0to3.led0.rate}")
    # tab expansion also works to find your way through the hierarchy of submodules
