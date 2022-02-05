from typing import List, Union

from migen import Constant, If

from pypga.core import (
    BoolRegister,
    MigenModule,
    Module,
    NumberRegister,
    Register,
    Signal,
    logic,
)
from pypga.core.common import get_length

from .migen.mux import MigenMux


def Mux(options: List[str], width: int = None) -> type:
    """
    A MUX whose input can be selected using a register.
    """

    class _Mux(Module):
        _select: Register(width=len(options).bit_length(), signed=False)
        _options = options

        @logic
        def _mux(self):
            self.out = Signal(width)
            # add one input signal per option
            for option in options:
                setattr(self, option, Signal(width))
            ###
            self.submodules.mux = MigenMux(
                select=self._select,
                options=[getattr(self, option) for option in options],
                default=0,
            )
            self.comb += self.out.eq(self.mux.out)

        @property
        def select(self):
            return self._options[self._select]

        @select.setter
        def select(self, option):
            self._select = self._options.index(option)

        # def __get__(self, instance, owner=None):
        #     # experimental feature
        #     return self.select

    return _Mux
