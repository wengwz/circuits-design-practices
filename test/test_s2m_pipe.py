import os
import cocotb
import cocotb_test.simulator
from test_utils.test_pipe import TestPipe


DATA_WIDTH = 64
CASES_NUM = 2048
VALID_RATIO = 0.3
READY_RATIO = 0.5

@cocotb.test(timeout_time=1000000000, timeout_unit="ns")
async def run_cocotb_test(dut):
    tester = TestPipe(dut, DATA_WIDTH, CASES_NUM, VALID_RATIO, READY_RATIO)
    await tester.run_test()

def test_s2m_pipe(is_ref, is_wave):
    proj_path = os.path.abspath("..")
    toplevel = "s2m_pipe"
    sim_build = os.path.join("build", toplevel)
    module = os.path.splitext(os.path.basename(__file__))[0]
    v_top_file = os.path.join(proj_path, "src", toplevel)
    parameters = {"DATA_WIDTH":DATA_WIDTH}
    defines = []
    if is_wave:
        defines.append("WAVE")
    
    if is_ref:
        v_top_file = os.path.join(v_top_file, "ref", toplevel + ".v")
    else:
        v_top_file = os.path.join(v_top_file, toplevel + ".v")
    verilog_sources = [v_top_file]

    cocotb_test.simulator.run(
        toplevel=toplevel,
        module=module,
        verilog_sources=verilog_sources,
        sim_build=sim_build,
        timescale="1ns/1ps",
        parameters=parameters,
        defines=defines
    )

if __name__ == "__main__":
    test_s2m_pipe(True, True)