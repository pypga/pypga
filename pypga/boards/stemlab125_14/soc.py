import logging
from migen_axi.integration.soc_core import SoCCore
# only required for ADC clock PLL
#from migen import *
#from migen.build.generic_platform import *
#from migen.genlib.cdc import AsyncResetSynchronizer


logger = logging.getLogger(__name__)


class StemlabSoc(SoCCore):
    def __init__(self, platform, top):
        logger.debug("Creating Stemlab SoC.")
        super().__init__(platform=platform, csr_data_width=32, ident="Soc")
        platform.add_platform_command("create_clock -name clk_fpga_0 -period 8 [get_pins \"PS7/FCLKCLK[0]\"]")
        platform.add_platform_command("set_input_jitter clk_fpga_0 0.24")
        # ADC clock input (main clock input)
        clk125_pads = platform.request("clk125")  # xdc 57
        platform.add_platform_command("create_clock -name clk_adc -period 8 [get_ports {port}]", port=clk125_pads.p)  # xdc 208
        adc_pads = platform.request("adc")
        for port in adc_pads.data_a, adc_pads.data_b:
            platform.add_platform_command("set_input_delay -max 3.400 -clock clk_adc [get_ports {port}[*]]", port=port)  # xdc 210
        # TODO: ADC clock PLL, and possibly ADC clock output (not required)
        # self.specials += [Instance("IBUFGDS", i_I=clk125_pads.p, i_IB=clk125_pads.n, o_O=self.cd_adc.clk)]  # top.v 310
        # generating ADC clock disabled (top.v 350)
        # self.specials += [AsyncResetSynchronizer(self.cd_adc, ResetSignal())]
        # self.clock_domains.cd_adc = ClockDomain()
        # self.specials += [
        #     Instance("ODDR", o_Q=adc_pads.clk[0], i_D1=1, i_D2=0, i_CE=1, i_C=self.cd_adc.clk),
        #     Instance("ODDR", o_Q=adc_pads.clk[1], i_D1=0, i_D2=1, i_CE=1, i_C=self.cd_adc.clk),
        # ]
        # self.comb += adc_pads.cdcs.eq(1)
        self.submodules.top = top
        self.csr_devices.append("top")
