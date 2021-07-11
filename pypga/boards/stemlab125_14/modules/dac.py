from migen import Signal, Instance, ClockSignal, Cat
from pypga.core import Module, logic
from pypga.core.register import FixedPointRegister


def Dac(bits=14):
    class _Dac(Module):
        out1: FixedPointRegister(width=bits, signed=True, decimals=bits-1, readonly=True, default=0)
        out2: FixedPointRegister(width=bits, signed=True, decimals=bits-1, readonly=True, default=0)

        @logic
        def _dac_settings(self, platform):
            dac = platform.request("dac")
            dac_dat_a = Signal(bits, reset=0)
            dac_dat_b = Signal(bits, reset=0)
            dac_rst = Signal()

            # convert output registers + signed to unsigned and to negative slope
            self.sync += [
                dac_dat_a.eq(Cat(~self.out1[:-1], self.out1[-1])),
                dac_dat_b.eq(Cat(~self.out2[:-1], self.out2[-1])),
            ]
            self.specials += [
                Instance("ODDR", o_Q=dac.clk, i_D1=0, i_D2=1, i_C=ClockSignal("clk_dac_2p"), i_CE=1, i_R=0, i_S=0),
                Instance("ODDR", o_Q=dac.wrt, i_D1=0, i_D2=1, i_C=ClockSignal("clk_dac_2x"), i_CE=1, i_R=0, i_S=0),
                Instance("ODDR", o_Q=dac.sel, i_D1=1, i_D2=0, i_C=ClockSignal("clk_dac_1p"), i_CE=1, i_R=dac_rst, i_S=0),
                Instance("ODDR", o_Q=dac.rst, i_D1=dac_rst, i_D2=dac_rst, i_C=ClockSignal("clk_dac_1p"), i_CE=1, i_R=0, i_S=0),
            ]
            self.specials += [
                Instance("ODDR", o_Q=dac.data[i], i_D1=dac_dat_b[i], i_D2=dac_dat_a[i], i_C=ClockSignal("clk_dac_1p"),  i_CE=1, i_R=dac_rst, i_S=0)
                for i in range(len(dac.data))
            ]
    return _Dac


def ExampleDac(bits=14):
    class _ExampleDac(Dac(bits=bits)):
        out1_setting: FixedPointRegister(width=bits, signed=True, decimals=bits-1, default=0)
        out2_setting: FixedPointRegister(width=bits, signed=True, decimals=bits-1, default=0)

        @logic
        def _example_connectivity(self):
            self.sync += [
                self.out1.eq(self.out1_setting),
                self.out2.eq(self.out2_setting),
            ]
    return ExampleDac
