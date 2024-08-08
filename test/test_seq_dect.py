
import os
import sys
import re
import logging
import random

import cocotb
import cocotb_test.simulator
from cocotb.triggers import RisingEdge

from test_utils import BasicTestbench, ClockSetting, ResetSetting


TOTAL_SEQ_LEN = 2048

class TestSeqDect(BasicTestbench):
    def __init__(self, dut, total_seq_len:int):
        self.log = logging.getLogger("TestSeqDect")
        self.log.setLevel(logging.INFO)
        self.dut = dut

        clk_setting = ClockSetting(name="clk", period=10)
        rst_setting = ResetSetting(name="reset", duration=3, level=True, clk_name="clk")
        super().__init__(
            log = self.log,
            dut = dut,
            clks = clk_setting,
            rsts = rst_setting
        )
        
        self.bit_pattern = "1101"
        self.data_in_seq = [random.randint(0, 1) for _ in range(total_seq_len)]
        self.data_out_seq = self.ref_model(self.bit_pattern, self.data_in_seq)
        
        self.log.info(f"Input Seq: " + "".join([str(bit) for bit in self.data_in_seq]))
        self.log.info(f"Output Seq: " + "".join([str(bit) for bit in self.data_out_seq]))
        
        self.input_port = self.dut.din
        self.output_port = self.dut.dout
        self.clock_port = self.dut.clk                    
    
    def ref_model(self, bit_pattern:str, data_in_seq:list)->list:
        data_in_seq_str = "".join([str(bit) for bit in data_in_seq])
        matches = re.finditer(bit_pattern, data_in_seq_str)
        
        data_out_seq = []
        
        for match in matches:
            end_idx = match.end()
            seq_len = len(data_out_seq)
            ext_len = end_idx - seq_len
            data_out_seq.extend([0] * ext_len)
            data_out_seq[-1] = 1

        if len(data_out_seq) < len(data_in_seq):
            ext_len = len(data_in_seq) - len(data_out_seq)
            data_out_seq.extend([0] * ext_len)
            
        data_out_seq.insert(0, 0) # Add one cycle delay
        return data_out_seq
    
    async def drive_input(self):
        for idx, bit in enumerate(self.data_in_seq):
            self.input_port.value = bit
            await RisingEdge(self.clock_port)
            self.log.info(f"drive {idx} input bit: {bit}")
        self.log.info("Drive input sequence done")
        return
            

    async def check_output(self):
        for idx, bit in enumerate(self.data_out_seq):
            await RisingEdge(self.clock_port)
            
            output_equal = self.output_port.value == bit
            if not output_equal:
                start = max(0, idx - 6)
                former_bits_str = "".join([str(bit) for bit in self.data_in_seq[start:idx]])
                self.log.error(f"Former 6-bit input sequence:" + former_bits_str)
            assert output_equal, f"Fail {idx} output bit: {bit}"
            
            self.log.info(f"Pass {idx} output bit: {bit}")
        return
    
    async def run_test(self):
        await self.start_gen_clk()
        await self.reset_dut()
        cocotb.start_soon(self.drive_input())
        check_thread = cocotb.start_soon(self.check_output())
        await check_thread
        self.log.info(f"Pass input sequence of {len(self.data_in_seq)}-bit successfully")


@cocotb.test(timeout_time=1000000000, timeout_unit="ns")
async def run_cocotb_test(dut):
    tester = TestSeqDect(dut, TOTAL_SEQ_LEN)
    await tester.run_test()


def test_seq_dect(is_ref, is_wave):
    toplevel = "seq_dect"
    root_dir = os.path.abspath("..")
    src_dir = os.path.join(root_dir, "src", toplevel)
    build_dir = os.path.join("build", toplevel)
    module = os.path.splitext(os.path.basename(__file__))[0]
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
    test_seq_dect(is_ref, is_wave)
