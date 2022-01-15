"""This file proposes an alternative patter to type hinting to define the submodule hierarchy."""


class ExampleTopTop(BaseClass):
    def _init_submodules(self):
        self.sub1 = ExampleTop(self)
   
    # 1. infer FPGA design
    # 2. create instance with interface to registers
    
    # defined in BaseClass, with the following content
    def __init__(self, parent):
        self._infer_fpga_design = parent._infer_fpga_design
        self._init_submodules()
        if not self._infer_fpga_design:
            self._init_instance()


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