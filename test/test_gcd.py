import os
import sys
import math
import queue
import logging
import random

import cocotb
import cocotb_test.simulator

from test_utils import BasicTestbench, PipeInDriver, PipeOutReceiver

DATA_WIDTH = 32
CASES_NUM = 128
DRIVER_IDLE_RATIO = 0.6
MONITOR_IDLE_RATIO = 0.4

class TestSimpleGCD(BasicTestbench):
    def __init__(self, dut, data_width:int, cases_num:int, driver_idle_ratio:float, monitor_idle_ratio:float):
        self.log = logging.getLogger("TestSimpleGCD")
        self.dut = dut
        super().__init__(
            log = self.log,
            dut = dut,
            clk_name = "clk",
            rst_name = "rst",
            clk_period = 10,
            rst_duration = 3,
            rst_level = True
        )
        
        self.pipeDriver = PipeInDriver(
            dut = dut,
            idle_ratio = driver_idle_ratio,
            clk_name = "clk",
            valid_port_name = "op_valid_i",
            ready_port_name = "op_ready_o",
            data_ports_name = ["op0_i", "op1_i"]
        )

        self.pipeReceiver = PipeOutReceiver(
            dut = dut,
            idle_ratio = monitor_idle_ratio,
            clk_name = "clk",
            valid_port_name = "res_valid_o",
            ready_port_name = "res_ready_i",
            data_ports_name = ["res_o"]
        )
        
        self.data_width = data_width
        self.cases_num = cases_num
        self.ref_buffer = queue.Queue(maxsize = cases_num)
    
    def ref_model(self, op0:int, op1:int):
        return math.gcd(op0, op1)
    
    async def drive_op_input(self):
        for i in range(self.cases_num):
            random_op0 = random.randint(0, pow(2, self.data_width) - 1)
            random_op1 = random.randint(0, pow(2, self.data_width) - 1)
            ref_result = self.ref_model(random_op0, random_op1)
            self.ref_buffer.put((random_op0, random_op1, [ref_result]))
            await self.pipeDriver.drive_pipe_in([random_op0, random_op1])
            self.log.info(f"Drive {i} testcase: op0={random_op0} op1={random_op1}")

    async def check_res_output(self):
        for i in range(self.cases_num):
            op0, op1, ref_res = self.ref_buffer.get()
            dut_res = await self.pipeReceiver.recv_pipe_out()
            assert dut_res == ref_res, f"Fail {i} testcase: op0={op0} op1={op1} dut_res={dut_res} ref_res={ref_res}"
            self.log.info(f"Pass {i} testcase: op0={op0} op1={op1} result={ref_res}")
        return
    
    async def run_test(self):
        await self.start_gen_clk()
        await self.reset_dut()
        cocotb.start_soon(self.drive_op_input())
        check_thread = cocotb.start_soon(self.check_res_output())
        await check_thread
        self.log.info(f"Pass all {self.cases_num} testcases successfully")
        


@cocotb.test(timeout_time=1000000000, timeout_unit="ns")
async def run_cocotb_test(dut):
    tester = TestSimpleGCD(dut, DATA_WIDTH, CASES_NUM, DRIVER_IDLE_RATIO, MONITOR_IDLE_RATIO)
    await tester.run_test()


def test_gcd(is_ref, is_wave):
    toplevel = "gcd"
    root_dir = os.path.abspath("..")
    src_dir = os.path.join(root_dir, "src", toplevel)
    build_dir = os.path.join("build", toplevel)
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
        toplevel=toplevel,
        module=module,
        verilog_sources=[vlog_file],
        sim_build=build_dir,
        timescale="1ns/1ps",
        parameters=parameters,
        defines=defines
    )

if __name__ == "__main__":
    is_ref = False
    is_wave = False
    for opt in sys.argv:
        if opt == '--ref':
            is_ref = True
        if opt == '--wave':
            is_wave = True
    test_gcd(is_ref, is_wave)
