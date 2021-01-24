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


.. literalinclude:: usage.py


.. include:: usage.py
