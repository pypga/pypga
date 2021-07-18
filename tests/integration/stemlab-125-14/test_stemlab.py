from pypga.examples.ex02_stemlab125_14 import MyStemlabTest
from pypga.core.testsupport.integration import BaseIntegrationTest
import pytest


class TestStemlab(BaseIntegrationTest):
    DUT = MyStemlabTest

    @pytest.fixture
    def dac(self, dut):
        return dut._dac

    def test_out_range(self, dac):
        assert dac.out1 < 1        
        assert dac.out1 > -1
        assert dac.out2 < 1        
        assert dac.out2 > -1