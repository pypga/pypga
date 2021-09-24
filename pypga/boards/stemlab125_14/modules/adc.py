from pypga.core import Module, logic, Register, Signal, Cat
from pypga.core.register import FixedPointRegister


def Adc(bits=14):
    class _Adc(Module):
        in1: FixedPointRegister(width=bits, signed=True, decimals=bits-1, readonly=True, default=0)
        in2: FixedPointRegister(width=bits, signed=True, decimals=bits-1, readonly=True, default=0)

        @logic
        def _adc_settings(self, platform):
            adc = platform.request("adc")
            for port in adc.data_a, adc.data_b:
                platform.add_platform_command("set_input_delay -max 3.400 -clock clk_adc [get_ports {port}[*]]", port=port)  # xdc 210
            adc_dat_a = Signal(bits, reset=0)
            adc_dat_b = Signal(bits, reset=0)
            self.sync += [
                adc_dat_a.eq(adc.data_a[2:]),  # lowest 2 bits reserved for 16 bit ADCs
                adc_dat_b.eq(adc.data_b[2:]),  # lowest 2 bits reserved for 16 bit ADCs
                self.in1.eq(Cat(~adc_dat_a[:-1], adc_dat_a[-1])),
                self.in2.eq(Cat(~adc_dat_b[:-1], adc_dat_b[-1])),
            ]
    return _Adc
