import logging
import uuid
from pathlib import Path, PosixPath
from time import sleep

from paramiko import SSHException
from scp import SCPException

from .sshshell import SshShell


class Server:
    _servername = "server"
    _bitstreamname = "bitstream.bin"
    _srcfiles = list(
        (Path(__file__).parent.resolve() / "server").glob(f"{_servername}_*.*")
    )
    _destpath = PosixPath("/root/pypga")

    def run(self, command=""):
        return self.shell.ask(command)

    def put(self, src, dst):
        self.shell.scp.put(src, dst)

    def __init__(self, host, port=2222, delay=0.05, bitstreamfile=None, start=True):
        self._delay = delay
        self.port = port
        self.shell = SshShell(
            hostname=host,
            sshport=22,
            user="root",
            password="root",
            delay=delay,
        )
        self.stop()
        self.run(f"mkdir {self.destpath}")
        self.run(f"cd {self.destpath}")
        if bitstreamfile is not None:
            self.flash_bitstream(bitstreamfile)
        if start:
            self.start()

    def stop(self):
        self.token = None
        self.run("\x03")  # exit running server application
        self.run("killall server")  # make sure no other server blocks the port

    @property
    def bitstream_flashed_recently(self) -> bool:
        self.run("")  # flush output
        result = self.run(
            f'echo $(($(date +%s) - $(date +%s -r "{self._destpath / self._bitstreamname}")))'
        )
        for line in result.split("\n"):
            try:
                age = int(line.strip())
            except ValueError:
                pass
            else:
                break
        else:
            logging.debug(f"Could not retrieve bitstream file age from: {result}")
            return False
        if age > 10:
            logging.debug(f"Found expired bitstream file with an age of {age} seconds.")
            return False
        else:
            logging.debug(
                f"Found a recent bitstream file with an age of {age} seconds."
            )
            return True

    def flash_bitstream(self, filename: str):
        destpath = str(self._destpath / self._bitstreamname).replace("\\","/")
        self.put(filename, destpath)
        self.stop()
        self.run("killall nginx")
        self.run("systemctl stop redpitaya_nginx")
        self.run(f"cat {destpath} > //dev//xdevcfg")
        self.shell.ask(f"rm -f {destpath}")  # clean up the bitstream

    def generate_new_token(self) -> str:
        self.token = str(uuid.uuid4().hex)
        return self.token

    def start(self) -> str:
        if self.bitstream_flashed_recently:
            logging.info("FPGA is being flashed. Waiting for 2 seconds.")
            sleep(2.0)
        destpath = str(self._destpath / "server").replace("\\","/")
        for serverfile in self._srcfiles:
            try:
                self.shell.scp.put(serverfile, destpath)
            except (SCPException, SSHException):
                logging.warning("Upload error.", exc_info=True)
            self.run(f"chmod 755 {destpath}")
            result = self.run(f"{destpath} {self.port} {self.generate_new_token()}")
            print("RESULT",result)
            sleep(self._delay)
            result += self.run()
            if not "sh" in result:
                logging.debug(f"Server application started on port {self.port}")
                break
            else:  # we tried the wrong binary version. make sure server is not running and try again with next file
                self.stop()
        else:
            raise RuntimeError(
                f"Server application could not be started with any of {[f for f in self._srcfiles]}."
            )
        return self.token
