import inspect
import io
import pytest
from pypga.interface.csrmap import CsrMap


CSR_CSV = inspect.cleandoc(
    """
    identifier.address,0x80000000,8,rw
    identifier.data,0x80000004,8,ro
    top.state0,0x80000800,1,rw
    top.state1,0x80000804,32,rw
    top.led0to3_led3_on,0x80000808,1,rw
    top.led0to3_led0_rate,0x8000080c,32,rw
    top.led0to3_led1_rate,0x80000810,32,rw
    top.led0to3_led2_rate,0x80000814,32,rw
    top.led4to7_led3_on,0x80000818,1,rw
    top.led4to7_led0_rate,0x8000081c,32,rw
    top.led4to7_led1_rate,0x80000820,32,rw
    top.led4to7_led2_rate,0x80000824,32,rw
    """
)


@pytest.fixture
def csrmap(tmp_path):
    filename = tmp_path / "csr.csv"
    with filename.open("w") as f:
        f.write(CSR_CSV)
    yield CsrMap(filename)


class TestNameToAddr:
    def test_name_to_addr(self, csrmap):
        assert csrmap.address["top.led0to3_led1_rate"] == 0x80000810

    def test_getitem(self, csrmap):
        assert csrmap["top.led4to7_led1_rate"] == (0x80000820, 32, "rw")
