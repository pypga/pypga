from pypga.interface.server import Server
from pypga.interface.client import Client


class Board:
    def __init__(self, host="127.0.0.1"):
        self._server = Server(host=host)
        self._client = Client(host=host)
