

class Server:
    def __init__(self, host, delay=0.05):
        self._delay = delay
        self.shell = SshShell(hostname=host,
                              sshport=22,
                              user="root",
                              password="root",
                              scp=True)
        self.update_fpga()
        self.installserver()

    def update_fpga(self, filename):
        self.end()
        sleep(self.parameters['delay'])
        self.ssh.ask('rw')
        sleep(self.parameters['delay'])
        self.ssh.ask('mkdir ' + self.parameters['serverdirname'])
        sleep(self.parameters['delay'])
        if source is None or not os.path.isfile(source):
            if source is not None:
                self.logger.warning('Desired bitfile "%s" does not exist. Using default file.',
                                    source)
            source = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fpga', 'red_pitaya.bin')
        if not os.path.isfile(source):
            raise IOError("Wrong filename",
              "The fpga bitfile was not found at the expected location. Try passing the arguments "
              "dirname=\"c://github//pyrpl//pyrpl//\" adapted to your installation directory of pyrpl "
              "and filename=\"red_pitaya.bin\"! Current dirname: "
              + self.parameters['dirname'] +
              " current filename: "+self.parameters['filename'])
        for i in range(3):
            try:
                self.ssh.scp.put(source,
                             os.path.join(self.parameters['serverdirname'],
                                          self.parameters['serverbinfilename']))
            except (SCPException, SSHException):
                # try again before failing
                self.start_ssh()
                sleep(self.parameters['delay'])
            else:
                break
        # kill all other servers to prevent reading while fpga is flashed
        self.end()
        self.ssh.ask('killall nginx')
        self.ssh.ask('systemctl stop redpitaya_nginx') # for 0.94 and higher
        self.ssh.ask('cat '
                 + os.path.join(self.parameters['serverdirname'], self.parameters['serverbinfilename'])
                 + ' > //dev//xdevcfg')
        sleep(self.parameters['delay'])
        self.ssh.ask('rm -f '+ os.path.join(self.parameters['serverdirname'], self.parameters['serverbinfilename']))
        self.ssh.ask("nginx -p //opt//www//")
        self.ssh.ask('systemctl start redpitaya_nginx')  # for 0.94 and higher #needs test
        sleep(self.parameters['delay'])
        self.ssh.ask('ro')

    def fpgarecentlyflashed(self):
        self.ssh.ask()
        result =self.ssh.ask("echo $(($(date +%s) - $(date +%s -r \""
        + os.path.join(self.parameters['serverdirname'], self.parameters['serverbinfilename']) +"\")))")
        age = None
        for line in result.split('\n'):
            try:
                age = int(line.strip())
            except:
                pass
            else:
                break
        if not age:
            self.logger.debug("Could not retrieve bitfile age from: %s",
                            result)
            return False
        elif age > 10:
            self.logger.debug("Found expired bitfile. Age: %s", age)
            return False
        else:
            self.logger.debug("Found recent bitfile. Age: %s", age)
            return True

    def startserver(self):
        self.endserver()
        sleep(self.parameters['delay'])
        if self.fpgarecentlyflashed():
            self.logger.info("FPGA is being flashed. Please wait for 2 "
                             "seconds.")
            sleep(2.0)
        result = self.ssh.ask(self.parameters['serverdirname'] + "/" + self.parameters['monitor_server_name']
                              + " " + str(self.parameters['port']) + " " + self.newtoken())
        if not "sh" in result:  # sh in result means we tried the wrong binary version
            self.logger.debug("Server application started on port %d",
                              self.parameters['port'])
            self._serverrunning = True
            return self.parameters['port'], self.parameters['token']
        # something went wrong
        return self.installserver()

    def endserver(self):
        try:
            self.ssh.ask('\x03')  # exit running server application
        except:
            self.logger.exception("Server not responding...")
        if 'pitaya' in self.ssh.ask():
            self.logger.debug('>')  # formerly 'console ready'
        sleep(self.parameters['delay'])
        # make sure no other pyrpl_server blocks the port
        self.ssh.ask('killall ' + self.parameters['monitor_server_name'])
        self._serverrunning = False
