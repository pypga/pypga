import io
import pyrtl
    

class ReadWriteRegister(pyrtl.Register):
    def __init__(self, bitwidth=None, read_only=False):
        super().__init__(bitwidth=bitwidth)
        self.read_only = read_only
        
    def __get__(self, instance, cls):
        if instance is None:
            return self
        print(f"Reading of register {self.name} would happen here.")
        return 123
    
    def __set__(self, instance, value):
        if self.read_only:
            raise ValueError(f"{self.name} is a read-only register.")
        print(f"Setting register {self.name} to value {value} would happen here.")
        
    def __set_name__(self, cls, name):
        self.name = name
        cls._read_write_registers.add(name)
        
        
class FpgaBaseClass:
    pyrtl.reset_working_block()
    
    _read_write_registers = set()
    
    fpga_revision = ReadWriteRegister(8, read_only=True)

    def __init__(self):
        print("Connecting to board and loading of the bitstream would happen here.")
    
    @classmethod
    def _programmable_logic(cls):
        cls.fpga_revision.next <<= 12  # some constant that can be read from the FPGA
        read_write_bus_i = pyrtl.Input(16, 'read_write_bus_i')
        read_write_bus_o = pyrtl.Output(16, 'read_write_bus_o')
        for i, name in enumerate(sorted(cls._read_write_registers)):
            print(f"Adding read-write logic for register {name} at address {i} would happen here.")
        cls._custom_programmable_logic()
        
    @classmethod
    def _custom_programmable_logic(cls):
        """
        Placeholder for custom PL.
        """ 
    
    @classmethod
    def generate_verilog_code(cls):
        print("\nGenerating verilog output\n=========================")
        cls._programmable_logic()
        with io.StringIO() as vfile:
            pyrtl.output_to_verilog(vfile)
            print(vfile.getvalue())

            
# this is the only code required for a custom board implementation
class MyFpgaBoard(FpgaBaseClass):
    counter_value = ReadWriteRegister(8, read_only=True)
    some_setting = ReadWriteRegister(10)
    
    @classmethod
    def _custom_programmable_logic(cls):
        cls.counter_value.next <<= cls.counter_value + 1
        

if __name__ == "__main__":
    MyFpgaBoard.generate_verilog_code()  # prints the verilog code to the screen

    print()
    print("Showing usage once a bitstream is generated from Verilog, e.g. using Vivado")
    print("===========================================================================")
    board = MyFpgaBoard()
    print(f"Counter value: {board.counter_value}")
    board.some_setting = 10
    print(f"Some setting: {board.some_setting}")
    print(f"FPGA revision: {board.fpga_revision}")
    board.fpga_revision = 10  # this will fail, as this is a read-only register

