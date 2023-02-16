from migen import Signal
from pypga.core import TopModule, Module, logic, Register


class BlinkLED(TopModule):
   # register accessible from Python
   rate: Register.custom(width=8)

   # FPGA Code
   @logic
   def _blink(self, platform):
       self.counter = Signal(8)
       self.sync += [self.counter.eq(self.counter + self.rate)]
       self.sync += [platform.request("user_led").eq(self.counter[-1])]

   # on PC
   def speed_up(self):
       self.rate *= 2

board = BlinkLED.run(host="10.153.153.255", board="stemlab125_14")

print(board.rate)

board.rate = 5
board.speed_up()
