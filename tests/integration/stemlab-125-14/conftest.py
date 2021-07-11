import pytest


@pytest.fixture(scope="session")
def host():
    return "rp"


@pytest.fixture(scope="session")
def board():
    return "stemlab125_14"
