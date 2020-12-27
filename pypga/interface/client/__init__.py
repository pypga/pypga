from .. import BaseInterface
from .client import Client
from .server import Server


class ClientInterface(BaseInterface):
    def __init__(self, host: str = "127.0.0.1"):
        self.server = Server(host=host)
        self.client = Client(host=host)

    def read(self, name: str) -> int:
        if isinstance(name, int):
            address = name
        else:
            address = self.name_to_address(name)

    def write(self, name: str, value: int):
        if isinstance(name, int):
            address = name
        else:
            address = self.name_to_address(name)
