from amaranth import *
from amaranth import Elaboratable, Module, Signal, unsigned, Const 
from amaranth.sim import Simulator
from amaranth.back import rtlil, verilog
from amaranth.lib.crc import Algorithm
import numpy as np


class node:
    def __init__(self, m, input_, output_, index=-1, class_=-1,  child_yes=None, child_no=None, isLeaf=False):
        self.m = m
        self.input = input_
        self.output = output_
        self.index = Const(index)
        self.index_num = index
        self.class_ = Const(class_)
        self.class_num = class_
        self.isLeaf = isLeaf
        self.child_yes = child_yes
        self.child_no = child_no

    def activate(self):
        if not self.isLeaf:
            with self.m.If(~self.input.bit_select(self.index, 1)):
                self.child_yes.activate()
            with self.m.Else():
                self.child_no.activate()
        else:
            self.m.d.comb+= self.output.eq(self.class_)
    
    def __repr__(self) -> str:
        return f"node{self.index_num}({self.class_num}) isLeaf: {self.isLeaf}"
    
    def print_tree(self, level=0):
        print("\t"*level, self)
        if not self.isLeaf:
            self.child_yes.print_tree(level+1)
            self.child_no.print_tree(level+1)
    
    def rec_set_m_i_o(self, m, i, o):
        self.m = m
        self.input = i
        self.output = o
        if not self.isLeaf:
            self.child_yes.rec_set_m_i_o(m, i, o)
            self.child_no.rec_set_m_i_o(m, i, o)

def test_Tree(x, y, root:node, test_name="test"):
    # set correct input output signals
    m = Module()
    s_image = Signal(unsigned(25))
    s_output = Signal(unsigned(8))
    # set the input output signals
    root.rec_set_m_i_o(m, s_image, s_output)
    root.activate()
    # convert x from booleqn array to int
    x_ = 0
    for i, bit in enumerate(x):
        x_ += bit*2**i
    # init the input
    m.d.sync+= s_image.eq(Const(int(x_)))
    async def test_bench(ctx):
        global res
        for _ in range(2):
            await ctx.tick()
        assert ctx.get(s_output) == y, "failed to classify the image"

    sim = Simulator(m)
    sim.add_clock(1e-6)
    sim.add_testbench(test_bench)

    with sim.write_vcd(test_name+".vcd"):
        sim.run()


class IO_Block:
    def __init__(self, m:Module, in_raw : Signal, in_image : Signal):

        # in_raw: system input, 8 bit bus, 
        #         in_raw [7:5]: indicate which row of the image the input belong to
        #         in_raw [4:0]: The value of each pixel on a row of a 5X5 image
        self.in_raw = in_raw

        # in_image: 25 bit bus representing the 5x5 image
        #           [4:0] -> 1st row, ... [24:20] -> last row 
        self.in_image = in_image
        self.m = m

    def activate(self):

        # create signal for in_raw[7:5]
        with self.m.Switch(self.in_raw[0:3]):
            with self.m.Case("000"):
                self.m.d.sync += self.in_image[0:5].eq(self.in_raw[3:8])
            with self.m.Case("001"):
                self.m.d.sync += self.in_image[5:10].eq(self.in_raw[3:8])
            with self.m.Case("010"):
                self.m.d.sync += self.in_image[10:15].eq(self.in_raw[3:8])
            with self.m.Case("011"):
                self.m.d.sync += self.in_image[15:20].eq(self.in_raw[3:8])
            with self.m.Case("100"):
                self.m.d.sync += self.in_image[20:25].eq(self.in_raw[3:8])

def test_IO_Block(x, test_name="test"):
    # create a module
    m = Module()
    s_input = Signal(unsigned(8))
    s_output = Signal(unsigned(25))
    block = IO_Block(m, s_input, s_output)
    block.activate()

    #fomat the input
    shape_data = np.array(x).reshape(5, -1).tolist()
    data =[]
    for i,d in enumerate(shape_data):
        x_ = 0
        for j, bit in enumerate(d):
            x_ += bit*2**j
        data.append((i,x_))

    async def test_bench(ctx):
        await ctx.tick()
        for p in data:
            ctx.set(s_input, p[1]*2**3 + p[0])
            await ctx.tick()
        final = f"{ctx.get(s_output):b}"
        res = []
        for i in final:
            res.append(bool(int(i)))
        while len(res) < 25:
            res.insert(0, False)
        res = np.array(res[::-1])
        assert np.all(res == np.array(x)), "failed to reconstruct the image"

    sim = Simulator(m)
    sim.add_clock(1e-6)
    sim.add_testbench(test_bench)
    with sim.write_vcd(test_name+".vcd"):
        sim.run()
    

def test_combined(x,y, root:node, test_name="test"):
    # create a module
    m = Module()
    s_input = Signal(unsigned(8))
    s_image = Signal(unsigned(25), reset_less=True)
    s_output = Signal(unsigned(8))
    # rst = Signal()
    io = IO_Block(m, s_input, s_image)
    io.activate()
    root.rec_set_m_i_o(m, s_image, s_output)
    root.activate()
    #format the input
    shape_data = np.array(x).reshape(5, -1).tolist()
    data =[]
    for i,d in enumerate(shape_data):
        x_ = 0
        for j, bit in enumerate(d):
            x_ += bit*2**j
        data.append((i,x_))

    async def test_bench(ctx):
        await ctx.tick()
        for p in data:
            # set the input
            ctx.set(s_input, p[1]*2**3 + p[0])
            await ctx.tick()
        assert ctx.get(s_output) == y, "failed to classify the image"

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    sim.add_testbench(test_bench)
    with sim.write_vcd(test_name+".vcd"):
        sim.run()


def generate_verilog(root:node, filename="tree.v"):
    # create the module and key signals
    m = Module()
    ui_in = Signal(unsigned(8))
    s_image = Signal(unsigned(25))
    uo_out = Signal(unsigned(8))

    uio_in = Signal(8)
    uio_out = Signal(8) # bidir, out
    uio_oe = Signal(8) # bidir, IOs: Enable path (active high: 0=input, 1=output)
    ena = Signal()
    clk = Signal()
    rst_n = Signal()
    # clock and reset
    cd_sync = ClockDomain("sync")
    m.domains += cd_sync
    m.d.comb += [
        ClockSignal("sync").eq(clk),
        ResetSignal("sync").eq(~rst_n),
    ]
    # create the IO block and the tree
    io = IO_Block(m, ui_in, s_image)
    io.activate()
    # set the tree signals
    root.rec_set_m_i_o(m, s_image, uo_out)
    root.activate()
    # convert the module to verilog
    with open(filename, "w") as f:
        f.write(verilog.convert(m, 
                                name="tt_um_COLVERTYETY_top",
                                emit_src=False, strip_internal_attrs=True,
                                ports=[ui_in, uo_out, uio_in,uio_out, uio_oe, ena, clk, rst_n]
                                ))

    print("Verilog file generated")
    print(f"File: {filename}")