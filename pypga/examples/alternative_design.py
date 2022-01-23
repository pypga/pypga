"""This file proposes an alternative pattern to type hinting to define the submodule hierarchy."""



class BaseModule:
    def __init__(self, _parent=None, **kwargs):
        self._parent = _parent
        self._infer_fpga_design = _parent is None or _parent._infer_fpga_design
        self._init_submodules(**kwargs)
        if not self._infer_fpga_design:
            self._init_client()

    def _init_submodules(self, **kwargs):
        """Insert any submodule instantiation here."""

    def _init_client(self):
        """Insert any code to run when the client is instantiated here."""

class ExampleSineAwg:
    """
    Trigger 
    -> reset counter
    -> start PulseGen sequence of pulses sampling_period apart 
       -> pulsegen busy
       -> Counter counts pulses 
          -> count looks up value from table to output 
          -> count reaching max stops the pulsegen
    """

    def _init_submodules(self, sampling_period=None, trigger=None, bits=14):
        self.pulsegen = ...
        self.counter = Counter()
        self.table = ...

        if sampling_period is None:
            self.sampling_period = FloatRegister(bits=14)
        else:
            self.sampling_period = sampling_period
        self.data = RamTable()
        self.pulsegen = PulseGen(trigger=trigger, sampling_period=self.sampling_period)
        self.out = 



class ExampleTop1(BaseClass):
    """Would this pattern be nicer???"""
    def _init_instance(self):
        """called when the instance is created at runtime"""
        self.awg1.start(data=data)

    def _init_submodules(self):
        self.awg1 = ExampeAwg(parent=self)
        self.awg2 = ExampeAwg(parent=self)


class ExampleTop2(BaseClass):
    """Current implementation"""
    def __init__(self):
        self.awg1.start(data=data)

    awg1: ExampeAwg()
    awg2: ExampeAwg()
