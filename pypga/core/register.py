import functools
import logging

from misoc.interconnect.csr import CSRStatus, CSRStorage

from migen import If, Memory, Signal

from .common import CustomizableMixin

logger = logging.getLogger(__name__)


class _Register(CustomizableMixin):
    def _add_migen_commands(self, name, module):
        name_csr = f"{name}_csr"
        if self.ram_offset is not None:
            # nothing to do, the register is simply an area in RAM
            pass
        if self.depth == 1:
            if self.readonly:
                csr_instance = CSRStatus(
                    size=self.width, reset=self.default, name=name_csr
                )
                setattr(module, name_csr, csr_instance)
                setattr(module, name, csr_instance.status)
            else:
                csr_instance = CSRStorage(
                    size=self.width, reset=self.default, name=name_csr
                )
                setattr(module, name_csr, csr_instance)
                setattr(module, name, csr_instance.storage)
                setattr(module, f"{name}_re", csr_instance.re)
        else:  # register has nontrivial depth, implement as a memory
            if self.default is None:
                initial_data = [0] * self.depth
            else:
                initial_data = [
                    self.from_python(self.before_from_python(v)) for v in self.default
                ]
            if self.reverse:
                initial_data = reversed(initial_data)
            memory = Memory(width=self.width, depth=self.depth, init=initial_data)
            setattr(module.specials, f"{name}_memory", memory)
            ps_port = memory.get_port(
                write_capable=not self.readonly, we_granularity=False
            )
            setattr(module.specials, f"{name}_memory_ps_port", ps_port)
            # add a port for the PL to write to the memory, otherwise having a this memory would be pointless
            pl_port = memory.get_port(write_capable=self.readonly, we_granularity=False)
            setattr(module.specials, f"{name}_memory_pl_port", pl_port)
            # one extra bit of width for controlling the index of the memory (LSB high = modify index)
            csr_instance = CSRStorage(
                size=self.width + 1, reset=0, name=name_csr, write_from_dev=True
            )
            setattr(module, name_csr, csr_instance)
            # PS writing the value ``(index << 1) + 1`` to the register triggers updates the index of the memory
            update_index = Signal()
            module.comb += update_index.eq(csr_instance.re & csr_instance.storage[0])
            # update index as requested by the PS (LSB is control bit, so ignored for the address)
            module.sync += If(
                update_index == 1, ps_port.adr.eq(csr_instance.storage[1:])
            )
            # PL writes the data at the new index to the register so it can be read by the PS, with ``delay`` cycles delay
            delay = 2
            we_pipeline = Signal(delay)
            module.sync += we_pipeline[0].eq(update_index)
            module.sync += we_pipeline[1:].eq(we_pipeline[:-1])
            module.sync += csr_instance.we.eq(we_pipeline[-1])
            module.comb += csr_instance.dat_w.eq(ps_port.dat_r)
            if self.readonly:
                # add signals to the migen module to write to the memory from the PL
                setattr(module, name, pl_port.dat_w)
                setattr(module, f"{name}_index", pl_port.adr)
                setattr(module, f"{name}_we", pl_port.we)
            else:
                # write to the memory when new values are sent by the PS, indicated by LSB being low
                update_value = Signal()
                module.comb += update_value.eq(
                    csr_instance.re & ~csr_instance.storage[0]
                )
                # the index has already been set by the PS at this point, so we only have to update the memory
                module.sync += ps_port.dat_w.eq(csr_instance.storage[1:])
                module.sync += ps_port.we.eq(update_value)
                # add signals to the migen module to read from the memory from the PL
                setattr(module, name, pl_port.dat_r)
                setattr(module, f"{name}_index", pl_port.adr)

    name: str = None
    width: int = 1
    default: int = 0
    readonly: bool = False
    offset_from_python: int = 0  # fpga value = Python value + offset_from_python
    depth: int = 1
    reverse: bool = False  # set True to invert the order of Python arrays.
    doc: str = ""
    ram_offset: int = None  # if True, data is read from RAM rather than from FPGA bus

    _SEP = "_"

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name

    def _get_full_name(self, instance):
        parents = instance._get_parents()
        return f"{parents[0]}.{'_'.join(parents[1:] + [self.name])}_csr"

    def to_python(self, value):
        value -= self.offset_from_python
        return value

    def from_python(self, value):
        value = int(value)
        value += self.offset_from_python
        if value < 0:
            value = 0
            logger.warning(f"Negative saturation of register {self.name}")
        elif value >= (1 << self.width):
            value = 1 << self.width
            logger.warning(f"Positive saturation of register {self.name}")
        return value

    def before_from_python(self, value):
        return value

    def __get__(self, instance, owner=None):
        logger.debug(f"Reading {self.name} with {instance}/{owner}")
        if instance is None:
            return self
        if self.depth == 1 and self.ram_offset is None:
            value = instance._interface.read(self._get_full_name(instance))
            return self.to_python(value)
        else:
            if self.ram_offset is None:
                value = instance._interface.read_array(
                    self._get_full_name(instance), length=self.depth
                )
            else:
                value = instance._interface.read_from_ram(self.ram_offset, self.depth*2)[::2]
            if self.reverse:
                value = reversed(value)
            return [self.to_python(v) for v in value]

    def __set__(self, instance, value):
        if self.readonly or self.ram_offset is not None:
            raise ValueError(
                f"The register {self.instance.name}.{self.name} is read-only."
            )
        if self.depth == 1:
            value = self.from_python(self.before_from_python(value))
            instance._interface.write(self._get_full_name(instance), value)
        else:
            if self.reverse:
                value = reversed(value)
            value = [self.from_python(self.before_from_python(v)) for v in value]
            instance._interface.write_array(self._get_full_name(instance), value)


class _BoolRegister(_Register):
    invert: bool = False
    bit: int = 0

    def to_python(self, value):
        value = _Register.to_python(self, value)
        value = bool((value >> self.bit) & 0x1)
        if self.invert:
            value = not value
        return value

    def from_python(self, value):
        if self.invert:
            value = not bool(value)
        value = int(bool(value)) << self.bit
        value = _Register.from_python(self, value)
        return value


class _TriggerRegister(_Register):
    """A register that returns a function which can be used to send a software trigger."""

    width = 1
    default = 0
    readonly = False
    offset_from_python = 0

    def __get__(self, instance, owner=None):
        send_trigger = functools.partial(
            instance._interface.write, self._get_full_name(instance), 0
        )
        return send_trigger

    def __set__(self, instance, value):
        raise AttributeError(
            "Trigger register cannot be set - try calling instead to generate a soft trigger."
        )

    def _add_migen_commands(self, name, module):
        name_csr = f"{name}_csr"
        csr_instance = CSRStorage(size=self.width, reset=self.default, name=name_csr)
        setattr(module, name_csr, csr_instance)
        setattr(module, name, csr_instance.re)


class _NumberRegister(_Register):
    signed: bool = False
    min: int = None
    max: int = None

    @property
    def _int_max(self):
        if self.signed:
            return int((1 << (self.width - 1)) - 1)
        else:
            return int((1 << self.width) - 1)

    @property
    def _int_min(self):
        if self.signed:
            return -int(1 << (self.width - 1))
        else:
            return 0

    def to_python(self, value):
        value = _Register.to_python(self, value)
        if self.signed and value >= (1 << (self.width - 1)):
            value -= 1 << self.width
        return int(value)

    def before_from_python(self, value):
        if self.max is not None and value > self.max:
            value = self.max
            logger.warning(f"Positive saturation for {self.name}")
        elif self.min is not None and value < self.min:
            value = self.min
            logger.warning(f"Negative saturation for {self.name}")
        return value

    def from_python(self, value):
        # saturate at the integer level
        if value < self._int_min:
            value = self._int_min
            logger.warning(f"Negative saturation for {self.name}")
        elif value > self._int_max:
            value = self._int_max
            logger.warning(f"Positive saturation for {self.name}")
        if self.signed and value < 0:
            value += 1 << self.width
        value = _Register.from_python(self, value)
        return value


class _FixedPointRegister(_NumberRegister):
    decimals: int = 0
    min: float = None
    max: float = None

    def to_python(self, value):
        value = _NumberRegister.to_python(self, value)
        value = float(value) / (2**self.decimals - 1)
        return value

    def from_python(self, value):
        value = int(round(float(value) * (2**self.decimals - 1)))
        value = _NumberRegister.from_python(self, value)
        return value


Register = _Register.custom
BoolRegister = _BoolRegister.custom
TriggerRegister = _TriggerRegister.custom
NumberRegister = _NumberRegister.custom
FixedPointRegister = _FixedPointRegister.custom
# TODO: add CallableBoolRegister
# TODO: add explicit arguments to custom for type completion
