
import os
import sys
import cocotb
import cocotb_test.simulator
from test_utils import TestPipe


DATA_WIDTH = 64
ADDR_WIDTH = 4
CASES_NUM = 2048


@cocotb.test(timeout_time=1000000000, timeout_unit="ns")
async def run_cocotb_test(dut):
    pipe_in_ports = {
        "valid": "wvalid",
        "ready": "wready",
        "data": "wdata",
        "clk" : "clk",
        "rst" : "reset"
    }
    
    pipe_out_ports = {
        "valid": "rvalid",
        "ready": "rready",
        "data" : "rdata",
        "clk"  : "clk",
        "rst"  : "reset"
    }
    
    basic_tester = TestPipe(dut, DATA_WIDTH, CASES_NUM, 0.5, 0.5, pipe_in_ports, pipe_out_ports)
    wfull_tester = TestPipe(dut, DATA_WIDTH, CASES_NUM, 0, 0.9, pipe_in_ports, pipe_out_ports)
    rempty_tester = TestPipe(dut, DATA_WIDTH, CASES_NUM, 0.9, 0, pipe_in_ports, pipe_out_ports)
    
    await basic_tester.run_test()
    await wfull_tester.run_test()
    await rempty_tester.run_test()

def test_sync_fifo(is_ref, is_wave):
    root_dir = os.path.abspath("..")
    toplevel = "sync_fifo"
    src_dir = os.path.join(root_dir, "src", toplevel)
    sim_build = os.path.join("build", toplevel)
    module = os.path.splitext(os.path.basename(__file__))[0]
    
    parameters = {"DSIZE":DATA_WIDTH, "ASIZE":ADDR_WIDTH}
    defines = []
    if is_wave:
        defines.append("DUMP_WAVE")
    
    if is_ref:
        vlog_file = os.path.join(src_dir, "ref", toplevel + ".v")
    else:
        vlog_file = os.path.join(src_dir, toplevel + ".v")

    cocotb_test.simulator.run(
        toplevel = toplevel + "_test_wrapper",
        module = module,
        verilog_sources = [vlog_file],
        sim_build = sim_build,
        timescale = "1ns/1ps",
        parameters = parameters,
        defines = defines
    )

if __name__ == "__main__":
    is_ref = False
    is_wave = False
    for opt in sys.argv:
        if opt == '--ref':
            is_ref = True
        if opt == '--wave':
            is_wave = True
    test_sync_fifo(is_ref, is_wave)
