PyPGA
=====

Pypga (Python Programmable Gate Arrays) aims to make FPGA programming more efficient by allowing you to create 
reusable modules in Python that contain both the programmable logic (PL) running on the FPGA and the Python logic 
to control the PL behavior at runtime from Python. That way you can build complex hierarchies of modules and share 
these with others easily. Using class inheritance, it becomes straightforward to maintain multiple versions of a 
design which allows optimal use of FPGA resources based on the specific use-case. PyPGA automatically detects when 
you change the PL and triggers the gateware build process only when it encounters a design it has never built before. 
Furthermore, the boilerplate code required to run your logic on an FPGA board is kept separate from the application 
code, so migrating to another board can be as simple as changing a single argument.  

At present, only the STEMlab125-14 board is supported. PyPGA heavily uses `migen <https://github.com/m-labs/migen>`_
to express the programmable logic using Python. For an introduction to the available migen commands, please refer 
to the `migen documentation <https://m-labs.hk/migen/manual/fhdl.html>`_.


Installation
============

It is required to have Vivado 2017.2 or a more recent version installed and the Vivado folder in the environment 
variables. On Ubuntu, assuming default installation paths, this is achieved by running 

.. code-block:: bash

   source /opt/Xilinx/Vivado/2017.2/settings.sh


To install PyPGA, run


.. code-block:: bash

   git clone https://github.com/pypga/pypga.git
   cd pypga
   pip install -e .



Usage
=====


.. include:: python

   from migen import Signal
   from pypga.core import TopModule, Module, logic, Register

   # a Module is the basic building block in PyPGA. Often it is useful
   # to create the Module class from a factory function to allow for
   # parametrizations, such as the default_rate here
   def SingleLedBlinker(default_rate=2 ** 6):
       counter_width = 32
        class _SingleLedBlinker(Module):
           # define a register that is accessible from Python
           rate: Register.custom(size=counter_width, reset=default_rate)

           # programmable logic is marked by the @logic decorator
           @logic
           def _blink(self, platform):
               self.counter = Signal(counter_width)
               self.sync += [self.counter.eq(self.counter + self.rate.storage_full)]
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
       led0: SingleLedBlinker(default_rate=2 ** 4)
       led1: SingleLedBlinker(default_rate=2 ** 5)
       led2: SingleLedBlinker(default_rate=2 ** 6)
       led3: SingleLedBlinker(default_rate=2 ** 7)
       led4: SingleLedBlinker(default_rate=2 ** 8)
       led5: SingleLedBlinker(default_rate=2 ** 9)
       led6: SingleLedBlinker(default_rate=2 ** 10)
       led7: SingleLedBlinker(default_rate=2 ** 11)

   # now we can try to run the new design on a STEMLab125-14 board with hostname "rp"
   # at first execution, this line will trigger the gatebare build process
   myboard = EightLeds.run(host="rp", board="stemlab125_14")

   # read the value of some registers
   print(f"Rates: {myboard.led0.rate}, {myboard.led1.rate}, {myboard.led2.rate}")
   # change the value of some registers
   myboard.led0.rate = 0
   myboard.led1.rate = 2 ** 11
   myboard.led2.speed_up()
