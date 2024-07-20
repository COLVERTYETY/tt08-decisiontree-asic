# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
import os 
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


def get_dataset():
    abs_path = os.path.abspath(__file__)
    rel_path = "../src/amaranth/data.txt"
    path = os.path.join(os.path.dirname(abs_path), rel_path)
    with open(path, "r") as file:
        data = file.readlines()

    samples = []
    for i in range(0, len(data), 7):
        label = data[i].strip()
        values = data[i+1:i+6]
        samples.append((label, values))

    dataset = []
    for label, values in samples:
        if len(label)!=1 or len(values)<5:
            continue
        l = int(label)
        values = [[1 if c == 'x' else 0 for c in row.strip()] for row in values]
        dataset.append((l, values))
    return dataset

def boolarray_to_int(x):
    x_ = 0
    for i, bit in enumerate(x):
        x_ += bit*2**i
    return x_

def shape_input(x):
    shape_data = x
    data =[]
    for i,d in enumerate(shape_data):
        x_ = boolarray_to_int(d)
        data.append((i,x_))
    return data

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    # Set the input values you want to test
    dut.ui_in.value = 20
    dut.uio_in.value = 30

    # Wait for one clock cycle to see the output values
    await ClockCycles(dut.clk, 1)

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    assert dut.uo_out.value == 50

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
