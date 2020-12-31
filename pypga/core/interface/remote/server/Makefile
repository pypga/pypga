.PHONY: all
SHELL:=/bin/bash
VIVADO_PATH:=/opt/Xilinx/Vivado/2017.2/settings64.sh

	
all: clean server_0.92 server_0.95

server_0.92:
	source $(VIVADO_PATH) && arm-xilinx-linux-gnueabi-gcc -o server_0.92 server.c

server_0.95:
	source $(VIVADO_PATH) && arm-linux-gnueabihf-gcc -o server_0.95 server.c

clean: 
	rm -f server_0.92 server_0.95
