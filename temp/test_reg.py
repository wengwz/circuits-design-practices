import random
import logging
import queue

import cocotb
from cocotb.handle import SimHandleBase
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

import cocotb_test.simulator
        
        
@cocotb.test(timeout_time=1000000000, timeout_unit="ns")
async def run_reg_test(dut):
    await cocotb.start(Clock(dut.clk, 10, 'ns').start())
    await RisingEdge(dut.clk)

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    
    dut.rst.value = 0
    dut.op_i.value = 1
    await RisingEdge(dut.clk)
    
    dut.op_i.value = 2
    print(f"REG_O: {int(dut.op_o.value)}")
    print(f"REG_I: {int(dut.op_i.value)}")
    await RisingEdge(dut.clk)

    dut.op_i.value = 3
    print(f"REG_O: {int(dut.op_o.value)}")
    print(f"REG_I: {int(dut.op_i.value)}")
    await RisingEdge(dut.clk)

    dut.op_i.value = 4
    print(f"REG_O: {int(dut.op_o.value)}")
    print(f"REG_I: {int(dut.op_i.value)}")
    await RisingEdge(dut.clk)


if __name__ == "__main__":
    cocotb_test.simulator.run(
        toplevel="my_reg",
        module="test_reg",
        verilog_sources=["reg.v"],
        timescale="1ns/1ps"
    )