.PHONY: build clean load read on off
SHELL:=/bin/bash
REDPITAYA_HOSTNAME:=rp
PYTHON:=python 
VIVADO_PATH:=/opt/Xilinx/Vivado/2017.2/settings64.sh 
ADDR:=0x80000808


build: clean build-server build-noclean

build-noclean: 
	source $(VIVADO_PATH) && $(PYTHON) -m pypga.example.build && cat build/csr.csv

build-server:
	source $(VIVADO_PATH) && $(MAKE) -C pypga/interface/server

load:
	scp build/redpitaya.bin root@$(REDPITAYA_HOSTNAME):/root/redpitaya.bin && \
	ssh root@$(REDPITAYA_HOSTNAME) "cat /root/redpitaya.bin > /dev/xdevcfg"

read:
	ssh root@$(REDPITAYA_HOSTNAME) "/opt/redpitaya/bin/monitor $(ADDR)"

on:
	ssh root@$(REDPITAYA_HOSTNAME) "/opt/redpitaya/bin/monitor $(ADDR) 0x0000000F"

off:
	ssh root@$(REDPITAYA_HOSTNAME) "/opt/redpitaya/bin/monitor $(ADDR)  0x00000000"

clean:
	rm -rf build/
