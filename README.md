Pypga
=====

This code use [migen](https://github.com/m-labs/migen) to express and implement the programmable logic running on a STEMlab125-14 board. 
For an introduction to the available migen commands, please refer to the [migen documentation](https://m-labs.hk/migen/manual/fhdl.html). 


Build the project
=================

It is required to have Vivado 2017.2 or a more recent version installed
and the Vivado folder in the environment variables. On Ubuntu, assuming 
default installation paths, this is achieved by running 

    source /opt/Xilinx/Vivado/2017.2/settings.sh


To install this package, run

    pip install -e .


To build the FPGA gateware, run

    make build


To prepare your redpitaya, run (insert the correct IP address of the redpitaya, and make sure you have an ssh key pair set up)

    ssh-copy-id root@192.168.1.100


To load your freshly built gateware onto the redpitaya, run

    make load REDPITAYA_HOSTNAME=192.168.1.100


