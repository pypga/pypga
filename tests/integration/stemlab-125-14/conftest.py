import pytest
import os


@pytest.fixture(scope="session")
def host():
    return os.getenv("REDPITAYA_HOSTNAME", "rp")


@pytest.fixture(scope="session")
def board():
    return "stemlab125_14"
