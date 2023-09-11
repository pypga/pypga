from typing import List, Union

from migen import Case, Cat, Constant

from pypga.core import If, MigenModule, Signal
from pypga.core.common import get_length


class MigenPid(MigenModule):
    def __init__(
        self,
        input,
        setpoint,
        k_p,
        k_i,
        width: int = 16,
        gainbits: int=24
    ):
        """
        PI controller with saturation.

        Args:
            input: the input signal to the controller.
            setpoint: the setpoint of the controller.
            k_p: proportional gain.
            k_i: integral gain.

        Output signals:
            out: the control output.
        """
        self.out = Signal(bits_sign=(width, True), reset=0)
        self.error = Signal(bits_sign=(width+1, True), reset=0)
        ###

        # need to figure out the width of all these signals - probably should be more "tunable", in the sense that gains can have different width than signals
        self.input_signal = Signal(bits_sign=(width, True), reset=0)
        self.k_p_signal = Signal(bits_sign=(gainbits, True), reset=0)
        self.k_i_signal = Signal(bits_sign=(gainbits, True), reset=0)
        self.setpoint_signal = Signal(bits_sign=(width, True), reset=0)
        self.prop = Signal(bits_sign=(width, True), reset=0)
        self.int = Signal(bits_sign=(30+width, True), reset=0)
        self.int_sum = Signal(bits_sign=(30+width, True), reset=0)
        #self.sum = Signal(bits_sign=(30+width, True), reset=0)

        # make sure all signals have correct width and signedness
        self.comb += [
            self.input_signal.eq(input),
            self.setpoint_signal.eq(setpoint),
            self.k_p_signal.eq(k_p),
            self.k_i_signal.eq(k_i),
        ]
        # nur sum+int_sum need 30+16bit
        
        self.sync += [
            self.error.eq(self.input_signal - self.setpoint_signal),
            self.prop.eq(self.error * self.k_p_signal),
            self.int.eq(self.error * self.k_i_signal),
            self.int_sum.eq(self.int_sum + self.int),
            #self.sum.eq( + self.int_sum),
            #self.out.eq(self.sum[0:width]), #take the 16 # need to add saturation and bitshift to find a good dynamic range
            #self.out.eq(self.sum),
            self.out.eq(self.prop+self.int_sum[width:-1]),
            #self.out.eq(self.sum>>16),
        ]

