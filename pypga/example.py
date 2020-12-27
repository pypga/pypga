import io
import pyrtl

pyrtl.reset_working_block()

factor1 = pyrtl.Input(4, 'factor1')
factor2 = pyrtl.Input(3, 'factor2')
result = pyrtl.Output(7, 'result')
product = pyrtl.Register(7, 'product')

product.next <<= pyrtl.signed_mult(factor1, factor2)

result <<= product

with io.StringIO() as vfile:
    pyrtl.output_to_verilog(vfile)
    print(vfile.getvalue())

