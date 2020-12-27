import logging
import numpy as np
import threading
from time import time
import socket
import uuid


class Client:
    def __init__(self, host="192.168.1.0", port=2222, timeout=1.0):
        self.logger = logging.getLogger(name=f"{__name__}/Client({self})")
        # add a lock for read/write access to the socket to make it threadsafe
        self._socket_lock = threading.Lock()
        # start setting up interface
        self._timeout = timeout
        self._hostname = hostname
        self._port = port
        self._token = str(uuid.uuid4().hex)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        self._socket.connect((self._hostname, self._port))
        # send authentification token
        assert len(self._token) == 32
        self._socket.sendall(str(self._token).encode('ascii'))
        # receive a confirmation token
        data = self._socket.recv(32)
        while (len(data) < 32):
            data += self._socket.recv(32 - len(data))
        data = data.decode("ascii")
        if data != '1'*32:
            raise RuntimeError(f"Wrong authentification token: {self._token} != {data}. This may mean "
                               f"that another client has connected to your redpitaya. Try restarting.")
        else:
            self.logger.debug(f"Correct authentification token: {self._token} / {data}")

    def close(self):
        try:
            self._socket.send(b"c" + b"\x00"*7)
            self._socket.close()
        except socket.error:
            self.logger.debug("Error upon closing socket: ", exc_info=True)

    def __del__(self):
        self.close()
        
    def reads(self, addr, length):
        if length > 65535:
            length = 65535
            self.logger.warning("Maximum read-length is %d", length)
        header = b'r' + bytes(bytearray([0,
                                         length & 0xFF, (length >> 8) & 0xFF,
                                         addr & 0xFF, (addr >> 8) & 0xFF, (addr >> 16) & 0xFF, (addr >> 24) & 0xFF]))
        with self._socket_lock:
            self._socket.sendall(header)
            timeout_time = time() + self._timeout
            data = self._socket.recv(length * 4 + 8)
            while len(data) < length * 4 + 8:
                result = self._socket.recv(length * 4 - len(data) + 8)
                data += result
                if len(result) == 0 and time() > timeout_time:
                    try:
                        self._clear_socket()
                    finally:
                        raise TimeoutError(f"Read timeout - incomplete data transmission: {data}")
            self._check_acknowledgement(header, ack=data[:8])

    def writes(self, addr, values):
        values = values[:65535 - 2]
        length = len(values)
        header = b'w' + bytes(bytearray([0,
                                         length & 0xFF,
                                         (length >> 8) & 0xFF,
                                         addr & 0xFF,
                                         (addr >> 8) & 0xFF,
                                         (addr >> 16) & 0xFF,
                                         (addr >> 24) & 0xFF]))
        with self._socket_lock:
            # send header+body
            self._socket.sendall(header + np.array(values, dtype=np.uint32).tobytes())
            self._check_acknowledgement(header)

    def _check_acknowledgement(self, header, ack=None):
        if ack is None:
            ack = self._socket.recv(8)
        if ack != header:  # check for transmission acknowledgement
            try:
                self._clear_socket()
            finally:
                raise RuntimeError(f"Error: wrong control sequence from server: {ack}")

    def _clear_socket(self):
        total_bytes_cleared = 0
        for i in range(100):
            bytes_cleared = len(self._socket.recv(16384))
            total_bytes_cleared += bytes_cleared
            if bytes_cleared <= 0:
                break
        self.logger.debug(f"Cleared {total_bytes_cleared} bytes from socket.")
