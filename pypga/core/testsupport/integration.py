import pytest

from .. import TopModule


class BaseIntegrationTest:
    class DUT(TopModule):
        """Overwrite in subclass to create the design under test."""

    @pytest.fixture(scope="class")
    def dut(self, host, board):
        dut = self.DUT.run(host=host, board=board)
        yield dut
        dut.stop()
