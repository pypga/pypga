import logging

# only required for ADC clock PLL
import migen
from migen_axi.integration.soc_core import SoCCore

# from migen.build.generic_platform import *
# from migen.genlib.cdc import AsyncResetSynchronizer


logger = logging.getLogger(__name__)


class StemlabSoc(SoCCore):
    def __init__(self, platform):
        logger.debug("Creating Stemlab SoC.")
        super().__init__(platform=platform, csr_data_width=32, ident="Soc")
        platform.add_platform_command(
            'create_clock -name clk_fpga_0 -period 8 [get_pins "PS7/FCLKCLK[0]"]'
        )
        platform.add_platform_command("set_input_jitter clk_fpga_0 0.24")

        # TODO: ADC clock PLL, and possibly ADC clock output (not required)
        # generating ADC clock disabled (top.v 350)
        # self.specials += [AsyncResetSynchronizer(self.cd_adc, ResetSignal())]
        # self.clock_domains.cd_adc = ClockDomain()
        # self.specials += [
        #     Instance("ODDR", o_Q=adc_pads.clk[0], i_D1=1, i_D2=0, i_CE=1, i_C=self.cd_adc.clk),
        #     Instance("ODDR", o_Q=adc_pads.clk[1], i_D1=0, i_D2=1, i_CE=1, i_C=self.cd_adc.clk),
        # ]
        # self.comb += adc_pads.cdcs.eq(1)

    def _attach_top(self, top):
        self.submodules.top = top
        self.csr_devices.append("top")
        # TODO: do a better job here, e.g. create "top" after having instantiated the SOC
        if hasattr(top, "_connect_to_soc"):
            top._connect_to_soc(top, self)
        else:
            print("no connect")
