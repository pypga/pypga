"""
Sketch of a new Pypga API and class structure
"""
#from dataclasses import dataclass
from functools import partial, wraps
from migen import Signal

#@dataclass
class Register:
    def __init__(self, bits: int = 1, signed: bool = False, value: int = 0, __inmigen__=False):     
        self.value=42
        if __inmigen__:
            self.__migen_init__()
            self.signal=Signal()
        else:
            self.__python_init__()
            
    def __python_init__(self):
        pass
        
    def __migen_init__(self):
        pass
    
    def eq(self, other):
        #take care of float and bit width, ...
        return self.signal.eq(other)
        
    def like(self,other):
        ...
    
    @property
    def v(self):
        return self.value
        
    #def __set__():

#@dataclass
class NumberRegister(Register):
    max: int = 1000
    
    @wraps(Register.__init__)   
    def __init__(self,value: int = 0,**kwargs):     
        super().__init__(self, **kwargs)
        
#%%
n=NumberRegister()
    
#my current register
#@dataclass
#class VoltageRegister(NumberRegister):
#    bits:int = 16
#%%    
VoltageRegister = partial(NumberRegister, bits = 16)
#%%


v=VoltageRegister()
#%%
v.bits
#%%
v.v
#%%


from migen import Module

class PypgaModule():
    
    __is_in_migen__=False
    
    def __init__(self, parent):
        self._parent=parent
        self.migen=Module()
        #super().__init__()
        self.__shared_init__()
        
        if self.__is_in_migen__:
            self.__migen_init__()
        else:
            self.__python_init__()
    
    @property
    def sync(self):
        if self.__is_in_migen__:
            raise
        return self.migen.sync()
            
    def __python_init__(self):
        pass
        
    def __migen_init__(self):
        #migen = migen.Module()
        for func in self.get_logic_funcs(self):
            func(self, self.migen)
            
    def set_attr(self,name,value):#
        #### enable self.bla=...
        # if is_sinatance(getattr(self,name),Register):
            getattr(self,name).eq(value,)
            
def logic(func):
    #@wraps(func)
    def migen_function(self,migen:Module):
        return migen_function(self,migen)
    return migen_function
    


class MyModule(PypgaModule):
    #nonono
    #def __init__(self):
    #    self.bla = Register(bits=3)
     
    constant = 34
    
    def __shared_init__(self):
        self.bla = Register(bits=3)
        
    # def __python_init__(self):
    #     pass
        
    
    # def __migen_init__(self,migen):
    #     #migen = super().__migen_init__()
    #     migen.sync +=[
    #         self.register.eq(self.register2)
    #     ]
    #     self._migen_func2(migen)
        
    # def _migen_func2(self,migen):
    #     
        
    @logic
    def _logic(self,migen:Module):        
        #add these
        
        
        
        self.migen
        
        migen.soc
        migen.platform
        
        #normal migen access
        migen.sync+=[]
        migen.comb+=[]
        migen.submodules.comb+=[]
        migen.cd.comb+=[]
        
        #example usage
        migen.sync +=[
            self.register.eq(self.register2),
            self.register2.eq(self.constant)
        ]
        def logic2():
            migen.comb+=[]
        for i in range(10):
            logic2()

        
    @logic
    def _more_logic(self,migen):        
        #add these
        ...
    
    def python_stuff(self):
        self.bla.eq(12) 
        #self.bal=12 #???
        #self.bal.value=12
        #self.bal.v=12

mod=MyModule()

#%%
mod._logic()

class MyModule2(MyModule):
    
     
    
    @logic
    def __shared_init__(self):
        super().__shared_init__()
        self.bla2 = Register(bits=3)


        
    @logic
    def _logic2(self):
        self.bla.eq()
    
#input(bla=1)        




class RegisterMemory(Signal):
    
    def __init__(self,__inmigen__=False,*args):
        #self.current_register=Register()
        ...
        
    def __getitem__(self, index):
        return 
        
        
class RegisterArray(Signal):
    
    def __init__(self,__inmigen__=False,*args):
        #self.current_register=Register()
        ...
        
    def __getitem__(self, index):
        return 
        
    
class RegisterMemoryDMA(Signal):
    #can only write every second clock cycle
    write_queue=...  
    
    def __init__(self,__inmigen__=False,*args):
        #self.current_register=Register()
        ...
        
    def __getitem__(self, index):
        return 
    
    def item_eq(self,data_to_write):
        write_queue.append(data_to_write)
        
    def now_write():
        pass
        #for self.write_queue.pop():
        #    ...
            #send to channels -->channels=...
            #on fail set error flag
            

arr = RegisterArray(...,bits=3,length=20)

self.sync+= [
    arr[22].eq(5),
]

#arr.we



#%%
class Register:
    def __set_name__(self, instance, name):
        self.name = name
        
    def __set__(self, instance, owner):
        print(f"{self.name=}, {self=}, {instance=}, {owner=}")
        
class Module:
    def __init__(self):
        self.a = Register()
    
    b = Register()
    
m0 = Module()

m0.a = 3
m0.b = 4


