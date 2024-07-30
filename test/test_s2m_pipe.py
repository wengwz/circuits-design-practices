import os
import sys
import cocotb
import cocotb_test.simulator
from test_utils import TestPipe


DATA_WIDTH = 64
CASES_NUM = 4096
SEND_IDLE_RATIO = 0.5
RECV_IDLE_RATIO = 0.5


@cocotb.test(timeout_time=1000000000, timeout_unit="ns")
async def run_cocotb_test(dut):
    tester = TestPipe(dut, DATA_WIDTH, CASES_NUM, SEND_IDLE_RATIO, RECV_IDLE_RATIO)
    await tester.run_test()

def test_s2m_pipe(is_ref, is_wave):
    root_dir = os.path.abspath("..")
    toplevel = "s2m_pipe"
    src_dir = os.path.join(root_dir, "src", toplevel)
    sim_build = os.path.join("build", toplevel)
    module = os.path.splitext(os.path.basename(__file__))[0]
    
    parameters = {"DATA_WIDTH":DATA_WIDTH}
    defines = []
    if is_wave:
        defines.append("DUMP_WAVE")
    
    if is_ref:
        vlog_file = os.path.join(src_dir, "ref", toplevel + ".v")
    else:
        vlog_file = os.path.join(src_dir, toplevel + ".v")

    cocotb_test.simulator.run(
        toplevel = toplevel,
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
    test_s2m_pipe(is_ref, is_wave)