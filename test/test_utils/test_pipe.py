import random
import logging
import queue

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


class TestPipe:
    def __init__(self, dut, data_width, cases_num, valid_ratio, ready_ratio):
        self.dut = dut
        
        self.log = logging.getLogger("TestPipe")
        self.log.setLevel(logging.DEBUG)
        
        self.reset_level = True
        self.cases_num = cases_num
        self.data_width = data_width
        self.valid_ratio = valid_ratio
        self.ready_ratio = ready_ratio
        self.ref_buffer = queue.Queue(maxsize = self.cases_num)
        
        self.clock = dut.clk
        self.reset = dut.reset
        self.pipe_in_valid = dut.pipe_in_valid
        self.pipe_in_ready = dut.pipe_in_ready
        self.pipe_in_data = dut.pipe_in_data
        self.pipe_out_valid = dut.pipe_out_valid
        self.pipe_out_ready = dut.pipe_out_ready
        self.pipe_out_data = dut.pipe_out_data

        # set initial value
        self.pipe_in_valid.setimmediatevalue(False)
        self.pipe_out_ready.setimmediatevalue(False)
    
    async def gen_clock(self):
        await cocotb.start(Clock(self.clock, 10, 'ns').start())
        self.log.debug("Start generating clock signal")
        
    async def gen_reset(self):
        self.reset.setimmediatevalue(self.reset_level) 
        await RisingEdge(self.clock)
        await RisingEdge(self.clock)
        await RisingEdge(self.clock)
        self.reset.value = not self.reset_level
        await RisingEdge(self.clock)
        await RisingEdge(self.clock)
        self.log.debug("Reset DUT successfully")

    async def drive_up_stream(self):
        for i in range(self.cases_num):
            while not (self.pipe_in_valid.value & self.pipe_in_ready.value):
                if not self.pipe_in_valid.value:
                    rand_valid = random.random() < self.valid_ratio
                    random_data = random.randint(0, pow(2, self.data_width) - 1)
                    self.pipe_in_valid.value = rand_valid
                    self.pipe_in_data.value = random_data
                await RisingEdge(self.clock)

            self.ref_buffer.put(self.pipe_in_data.value)
            self.log.debug(f"Drive {i} testcase: {int(self.pipe_in_data.value)}")
            self.pipe_in_valid.value = random.random() < self.valid_ratio
            self.pipe_in_data.value = random.randint(0, pow(2, self.data_width) - 1)
            await RisingEdge(self.clock)

    async def check_down_stream(self):
        for i in range(self.cases_num):
            while not (self.pipe_out_valid.value & self.pipe_out_ready.value):
                rand_ready = random.random() < self.ready_ratio
                self.pipe_out_ready.value = rand_ready
                await RisingEdge(self.clock)
            
            dut_data = self.pipe_out_data.value
            assert not self.ref_buffer.empty(), "Redundant data is generated"
            ref_data = self.ref_buffer.get()

            self.log.debug(f"Receive {i} testcase: DUT={int(dut_data)} REF={int(ref_data)}")
            assert dut_data == ref_data, "Data received from DUT is incorrect"
            
            self.pipe_out_ready.value = random.random() < self.ready_ratio
            await RisingEdge(self.clock)

    async def run_test(self):
        await self.gen_clock()
        await self.gen_reset()
        drive_thread = cocotb.start_soon(self.drive_up_stream())
        check_thread = cocotb.start_soon(self.check_down_stream())
        await check_thread
        self.log.debug(f"Pass all {self.cases_num} testcases successfully")


