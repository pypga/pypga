import hashlib
import logging

# only required for ADC clock PLL
import migen
from migen.fhdl.verilog import convert
from pypga.core.migen_axi.integration.soc_core import SoCCore
from functools import partial
# from migen.build.generic_platform import *
# from migen.genlib.cdc import AsyncResetSynchronizer
from .clock import create_stemlabs_clocks

logger = logging.getLogger(__name__)


class StemlabSoc(SoCCore):
    def __init__(self, platform):
        logger.debug("Creating Stemlab SoC.")

        super().__init__(platform=platform, csr_data_width=32, ident="Soc", create_sys_clock=partial(create_stemlabs_clocks, platform=platform))
        platform.add_platform_command(
            'create_clock -name clk_fpga_0 -period 8 [get_pins "PS7/FCLKCLK[0]"]'
        )
        platform.add_platform_command("set_input_jitter clk_fpga_0 0.24")

    def _attach_top(self, top):
        self.submodules.top = top
        self.csr_devices.append("top")

    def _hash(self):
        """
        Returns a hash to unambiguously identify a design.

        This is used to decide whether a design has been build or still needs to be.
        """
        verilog = convert(self)
        hash_ = hashlib.sha256()
        hash_.update(verilog.main_source.encode())
        for filename, content in verilog.data_files.items():
            hash_.update(filename.encode())
            hash_.update(content.encode())
        return hash_.hexdigest()
