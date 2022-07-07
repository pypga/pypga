import logging

from migen_axi.platforms import redpitaya
from misoc.integration import cpu_interface

from pypga.boards.stemlab125_14.soc import StemlabSoc
from pypga.core.builder import BaseBuilder
from pypga.core.migen import AutoMigenModule

logger = logging.getLogger(__name__)


class Builder(BaseBuilder):
    board = "stemlab125_14"
    _build_results = ["bitstream.bin", "csr.csv"]

    def _create_platform(self):
        logger.debug("Creating platform")
        self._platform = redpitaya.Platform()
        self._platform.toolchain.bitstream_commands.extend(
            ["set_property BITSTREAM.GENERAL.COMPRESS True [current_design]"]
        )
        self._platform.toolchain.additional_commands.extend(
            [
                'write_cfgmem -force -format BIN -size 2 -interface SMAPx32 -disablebitswap -loadbit "up 0x0 ./top.bit" ./bitstream.bin',
            ]
        )

    def _create_soc(self):
        logger.debug("Creating SoC")
        self.soc = StemlabSoc(platform=self._platform)

    def _export_register_addresses(self):
        with (self.build_path / "csr.csv").open("w") as f:
            f.write(cpu_interface.get_csr_csv(self.soc.get_csr_regions()))

    def _get_hash(self):
        """Returns a hash for the design, without building the actual design or requiring a build folder."""
        self._create_platform()
        self._create_soc()
        self.top = AutoMigenModule(
            self.module_class, platform=self._platform, soc=self.soc
        )
        self.soc._attach_top(self.top)
        # TODO: include SOC in hash, for example by running `soc.build(run=False) and hashing build path`
        return self.top._hash()

    def _build(self):
        """The actual steps required for building this design."""
        self._create_platform()
        self._create_soc()
        self.top = AutoMigenModule(
            self.module_class, platform=self._platform, soc=self.soc
        )
        self.soc._attach_top(self.top)
        logger.debug("Running vivado build...")
        self.soc.build(build_dir=self.build_path, run=True)
        self._check_timing_constraints_are_met()
        self._export_register_addresses()
        logger.debug(f"Finished build for {self.__class__.__name__}.")
        self.copy_results()

    def _check_timing_constraints_are_met(self):
        """Raises an exception if there are timing violations."""
        with open(self.build_path / "vivado.log", "r") as file:
            lines = [line.strip() for line in file.readlines()]
            if "All user specified timing constraints are met." not in lines:
                raise RuntimeError(
                    "Timing constraints of this design could not be met. Please "
                    "check the build logs for hints on how to improve timing."
                )
