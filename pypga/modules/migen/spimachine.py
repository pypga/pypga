from migen import Module, Signal, If, Cat, Mux
from migen.genlib.fsm import FSM, NextState, NextValue
from pypga.core.common import get_length


class ClockGen(Module):
    """
    Clock signal generator that controls the length of one half cycle
    of class SPIMachine.
    """
    def __init__(self, div):
        # High, if half cycle is done
        self.done = Signal()
        # Set to high to start counting
        self.start = Signal()
        # Current counter value
        self.counter = Signal(get_length(div))
        
        ###
        
        # Set done to True, when counter is zero, but only if the clock
        # is not being started.
        self.comb += [self.done.eq((self.counter == 0) & ~self.start)]
    
        fsm = FSM("IDLE")
        self.submodules += fsm

        fsm.act("IDLE",
            If(self.start,
                # Initialize counter to div-1, since counting to zero will
                # require a number of div system clock cycles.
                NextValue(self.counter, div - 1),
                NextState("COUNTING")
            )
        )
        fsm.act("COUNTING",
            If(self.done,
                NextState("IDLE")
            ).Else(
                # TODO: In case start is kept high, this will wrap around
                # counter and keep it counting forever. Currently, relies
                # on the caller respecting this feature.
                NextValue(self.counter, self.counter - 1)
            )
        )

                
class Register(Module):
    """
    Register that stores and manipulates the data sent over SPI.
    """
    def __init__(self, data_width):
        # Parallel data out (to serial)
        self.pdo = Signal(data_width)
        # Serial data out (from parallel)
        self.sdo = Signal(reset_less=True)
        # Transmit LSB first
        self.lsb_first = Signal()
        # Set to high to initialize the shift register and load the first bit into sdo
        self.init = Signal()
        # Set to high to shift the shift register and load next bit into sdo
        self.shift = Signal()

        ###

        # Two shift registers working together to shift pdo by one bit.
        sr_current = Signal(data_width, reset_less=True)
        sr_next = Signal(data_width, reset_less=True)

        # Define sr_next to always be a copy of sr_current shifted by one bit.
        self.comb += [
            sr_next.eq(Mux(self.lsb_first,
                Cat(sr_current[1:], 0),
                Cat(0, sr_current[:-1])))
        ]
        
        self.sync += [
            # Initialize sr_current to pdo and sdo to the LSB of pdo.
            If(self.init,
                sr_current.eq(self.pdo),
                self.sdo.eq(Mux(self.lsb_first, self.pdo[0], self.pdo[-1]))
            ),
            # Load shifted pattern from sr_next into sr_current and update sdo.
            If(self.shift,
                sr_current.eq(sr_next),
                self.sdo.eq(Mux(self.lsb_first, sr_next[0], sr_next[-1]))
            )
        ]


class SPIMachine(Module):
    """
    Finite state machine that steps through the different states of SPI transmission.
    """
    def __init__(self, data_width=32, clock_div=8, 
                 leading_halfcycles = 2, trailing_halfcycles = 2,
                 idle_halfcycles = 1):
        # High, if no transfer is in progress
        self.idle = Signal()
        # Set to high to start transfer, if idle is True.
        self.start = Signal()
        # Chip select
        self.cs = Signal()
        # SPI clock
        self.clk = Signal()
        # SPI clock phase
        self.clk_phase = Signal()
        
        # Counter to count number of (half) cycles
        self.counter = Signal(max(get_length(data_width),
                                  get_length(leading_halfcycles),
                                  get_length(trailing_halfcycles),
                                  get_length(idle_halfcycles)))

        self.submodules.cg = cg = ClockGen(clock_div)
        self.submodules.reg = reg = Register(data_width)
        
        ###
        
        fsm = FSM("IDLE")
        self.submodules += fsm
        # TODO: Transitions between the FSM states consume one system clock
        # cycle, such that actually one half cycle is not div but div+1 system
        # clock cycles long.
        # Transitions from/to leading, trailing and idle half cycles consume
        # even one system clock cycle more.
        # For now, this is not relevant, but for high-speed SPI transmissions
        # this may play a role.

        # Idle state. Start SPI transaction, when self.start is asserted.
        fsm.act("IDLE",
            self.idle.eq(1),
            If(self.start,
                If(self.clk_phase,
                    # If SPI clk phase is true, there must be at least one
                    # leading halfcycle. Start the clock generator and set
                    # counter to 1 in case leading_halfcycles is zero.
                    NextValue(cg.start, 1),
                    NextValue(self.counter, leading_halfcycles + (leading_halfcycles == 0))
                ).Else(
                    # Start the clock generator only, if there is at least one
                    # leading half cycle.
                    NextValue(cg.start, leading_halfcycles > 0),
                    NextValue(self.counter, leading_halfcycles)
                ),
                NextState("LEADING_HALFCYCLES")
            ).Else(
                NextValue(cg.start, 0)
            )
        )
        # Asserts CS for specified number of half cycles, while keeping SPI
        # clk and MOSI low.
        fsm.act("LEADING_HALFCYCLES",
            self.cs.eq(1),
            If(self.counter == 0,
                # Start data transmission on next half cycle
                NextValue(cg.start, 1),
                # Set counter to data width, since it will now only be
                # decremented every full cycle
                NextValue(self.counter, data_width),
                # Set sdo on the next system clock cycle
                reg.init.eq(1),
                NextState("1ST_HALFCYCLE")
            ).Else(
                If(cg.done,
                    # Restart clock generator only, if this is not the last
                    # leading half cycle.
                    NextValue(cg.start, self.counter > 1),
                    NextValue(self.counter, self.counter - 1),
                    NextState("LEADING_HALFCYCLES")
                ).Else(
                    # Continue current leading half cycle.
                    NextValue(cg.start, 0)
                )
            )
        )
        # First half cycle of a one-bit transmission
        fsm.act("1ST_HALFCYCLE",
            self.cs.eq(1),
            # Set SPI clk to high or low, depending on clock phase.
            # Only assert clock, if another full cycle is to come.
            self.clk.eq(self.clk_phase & (self.counter > 0)),
            If(self.counter == 0,
                # Data transmission is over, proceed to trailing half cycles.
                # Start clock generator only, if ther is at least one trailing half cycle
                NextValue(cg.start, trailing_halfcycles > 0),
                NextValue(self.counter, trailing_halfcycles),
                NextState("TRAILING_HALFCYCLES")
            ).Else(
                If(cg.done,
                    # Go over to 2nd half cycle.
                    NextValue(cg.start, 1),
                    NextState("2ND_HALFCYCLE")
                ).Else(
                    # Continue current 1st half cycle.
                    NextValue(cg.start, 0)
                )
            )
        )
        # Second half cycle of a one-bit transmission
        fsm.act("2ND_HALFCYCLE",
            self.cs.eq(1),
            # Set SPI clk to high or low, depending on clock phase.
            self.clk.eq(~self.clk_phase),
            
            If(cg.done,
                # Go back to 1st half cycle.
                # Shift next value into sdo on next system clock cycle
                reg.shift.eq(1),
                # Restart clock generator only, if there is another full cycle
                NextValue(cg.start, self.counter > 1),
                NextValue(self.counter, self.counter - 1),
                NextState("1ST_HALFCYCLE")
            ).Else(
                # Continue current 2nd half cycle.
                NextValue(cg.start, 0),
            )
        )
        # Asserts CS for specified number of half cycles, while keeping clock and
        # MOSI low.
        fsm.act("TRAILING_HALFCYCLES",
            self.cs.eq(1),
            If(self.counter == 0,
                # Proceed to idle half cycles.
                # Start clock generator only, if there is at least one idle half cycle
                NextValue(cg.start, idle_halfcycles > 0),
                NextValue(self.counter, idle_halfcycles),
                NextState("IDLE_HALFCYCLES")
            ).Else(
                If(cg.done,
                    # Restart clock generator only, if there is another trailing
                    # half cycle.
                    NextValue(cg.start, self.counter > 1),
                    NextValue(self.counter, self.counter - 1),
                    NextState("TRAILING_HALFCYCLES")
                ).Else(
                    # Continue current trailing half cycle.
                    NextValue(cg.start, 0)
                )
            )
        )
        # Holds CS low for the specified number of half cycles.
        fsm.act("IDLE_HALFCYCLES",
            If(self.counter == 0,
                # Proceed to idle state.
                NextValue(cg.start, 0),
                NextState("IDLE")
            ).Else(
                If(cg.done,
                    # Restart clock generator only, if there is another idle
                    # half cycle.
                    NextValue(cg.start, self.counter > 1),
                    NextValue(self.counter, self.counter - 1),
                    NextState("IDLE_HALFCYCLES")
                ).Else(
                    # Continue current idle half cycle.
                    NextValue(cg.start, 0)
                )
            )
        )


def sim_spimachine(num_steps, query):
    """
    Simulate signals of the SPI state machine.
    """
    from migen.sim import run_simulation
    module = SPIMachine(data_width=8,
                        clock_div=4,
                        leading_halfcycles=0)
    
    t = []
    results = {k: [] for k in query}
    
    def getattr_(obj, lst):
        """
        Equivalent for getattr() for nested objects
        """
        if len(lst) == 1:
            return getattr(obj, lst[0])
        else:
            return getattr_(getattr(obj, lst[0]), lst[1:])
        
    def sim():
        """
        Run simulation and store parameter values in global lists
        """
        for i in range(num_steps):
            t.extend([i, i+1])
            for k, v in query.items():
                if v is None:
                    val = (yield getattr_(module, k.split('.')))
                if isinstance(v, dict):
                    if i in v:
                        yield getattr_(module, k.split('.')).eq(v[i])
                    val = (yield getattr_(module, k.split('.')))
                results[k].extend([val]*2)
            yield
            
    run_simulation(module, sim())
    return t, results
    

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    query = {"cs": None,
             "clk": None,
             "counter": None,
             "cg.counter": None,
             "start": {1: 1, 2: 0},
             "reg.sdo": None,
             "reg.pdo": {0: 171},
             "clk_phase": {0:1}}

    t, results = sim_spimachine(120, query)
    
    fig, axs = plt.subplots(nrows = len(results), ncols = 1, sharex = True)
    plt.tight_layout()
    fig.supxlabel('Clock cycle')
    fig.supylabel('Value')
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']

    for i, p in enumerate(results.items()):
        k, v = p
        axs[i].title.set_text(k)
        axs[i].plot(t, v, color = colors[i % len(colors)])

