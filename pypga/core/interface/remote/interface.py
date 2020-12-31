from ..interface import BaseInterface
from .client import Client
from .server import Server


class RemoteInterface(BaseInterface):
    def __init__(self, build_result_path: str = None, host: str = "127.0.0.1"):
        super().__init__(build_result_path)
        self.host = host
        self.server = Server(
            host=host,
            bitstreamfile=self.build_result_path / Server._bitstreamname,
        )
        self.client = Client(host=host, token=self.server.token)

    def read_from_address(self, address: int) -> int:
        return int(self.client.reads(address, 1)[0])

    def write_to_address(self, address: int, value: int):
        self.client.writes(address, [int(value)])
