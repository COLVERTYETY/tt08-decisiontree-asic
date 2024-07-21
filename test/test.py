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
    """Test the project."""

    dataset = get_dataset()
    fails = []
    # print(dataset)


    # Initialize the dut
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
    correct = 0
    for i, (l,v) in enumerate(dataset):
        test = shape_input(v)
        dut._log.info(f"Test {i} with label {l} and values {v}")
        dut._log.info("Reset")
        dut.ena.value = 1
        dut.ui_in.value = 0
        dut.uio_in.value = 0
        dut.rst_n.value = 0
        await ClockCycles(dut.clk, 3)
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 3)
        for x, j in test:
            dut.ui_in.value = j*2**3 + x
            await ClockCycles(dut.clk, 1)
        await ClockCycles(dut.clk, 5)
        correct += 1 if int(dut.uo_out.value) == l else 0
        # dut._log.info(f"Output: {int(dut.uo_out.value)} Expected: {l}")
        if int(dut.uo_out.value) != l:
            dut._log.error(f"Output: {int(dut.uo_out.value)} Expected: {l} at {i}")
            fails.append(i)
    dut._log.info(f"Correct: {correct}/{len(dataset)}")
    assert correct >= len(dataset)*0.6, "too many errors"

    # Wait for one clock cycle to see the output values
    await ClockCycles(dut.clk, 1)
    dut._log.info("End")
    # save the fails
    print(fails)
