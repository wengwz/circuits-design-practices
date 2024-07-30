
import random
import queue
import logging

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

class BasicTestbench:
    """
    A basic tester whichs wraps some shared operations related with clock and reset  
    """
    def __init__(self, log, dut, clk_name:str, rst_name:str, clk_period:int, rst_duration:int, rst_level:bool):
        self.log = log
        self.dut = dut
        assert hasattr(dut, clk_name)
        self.clk_port = getattr(dut, clk_name)
        assert hasattr(dut, rst_name)
        self.rst_port = getattr(dut, rst_name)
        
        self.clk_period = clk_period
        self.rst_duration = rst_duration
        self.rst_level = rst_level
        
    async def start_gen_clk(self):
        await cocotb.start(Clock(self.clk_port, self.clk_period, 'ns').start())
        self.clock_start = True
        self.log.info(f"Start generating clock signal on port {dir(self.clk_port)} with period={self.clk_period} ns")
    
    async def reset_dut(self):
        assert self.clock_start
        self.rst_port.value = self.rst_level
        for _ in range(self.rst_duration + 1):
            await RisingEdge(self.clk_port)
        
        self.rst_port.value = not self.rst_level
        await RisingEdge(self.clk_port)
        self.log.info(f"Reset DUT through port {dir(self.rst_port)} with level={self.rst_level} cycle_count={self.rst_duration}")
    

class PipeInDriver:
    def __init__(self, dut, idle_ratio:float, clk_name:str, valid_port_name:str, ready_port_name:str, data_ports_name:list[str]):
        self.clk_port = getattr(dut, clk_name)
        self.valid_port = getattr(dut, valid_port_name)
        self.ready_port = getattr(dut, ready_port_name)
        self.data_ports = [getattr(dut, data_port_name) for data_port_name in data_ports_name]
        self.idle_ratio = idle_ratio
        self.valid_port.value = False
        
        return
    
    async def drive_pipe_in(self, data_list:list):
        assert len(data_list) == len(self.data_ports)
        
        while random.random() < self.idle_ratio:
            await RisingEdge(self.clk_port)
        
        self.valid_port.value = True
        for data_port, data in zip(self.data_ports, data_list):
            data_port.value = data
        
        while True:
            await RisingEdge(self.clk_port)
            if (self.valid_port.value and self.ready_port.value):
                break
        
        self.valid_port.value = False
        return


class PipeOutReceiver:
    def __init__(self, dut, idle_ratio:float, clk_name:str, valid_port_name:str, ready_port_name:str, data_ports_name):
        self.clk_port = getattr(dut, clk_name)
        self.valid_port = getattr(dut, valid_port_name)
        self.ready_port = getattr(dut, ready_port_name)
        self.data_ports = [getattr(dut, data_port_name) for data_port_name in data_ports_name]
        self.idle_ratio = idle_ratio
        self.ready_port.value = False
        return
    
    async def recv_pipe_out(self)->list:
        data_list = []
        while True:
            self.ready_port.value = not (random.random() < self.idle_ratio)
            await RisingEdge(self.clk_port)
            if self.valid_port.value and self.ready_port.value:
                break
        
        for data_port in self.data_ports:
            data_list.append(data_port.value)
        
        self.ready_port.value = False
        return data_list


class TestPipe(BasicTestbench):
    def __init__(self, dut, data_width, cases_num:int, driver_idle_ratio:float, recv_idle_ratio:float):
        self.log = logging.getLogger("TestPipe")
        self.log.setLevel(logging.DEBUG)
        super().__init__(
            log = self.log,
            dut = dut,
            clk_name = "clk",
            rst_name = "reset",
            clk_period = 10,
            rst_duration = 3,
            rst_level = True
        )
        
        self.pipe_in_driver = PipeInDriver(
            dut = dut,
            idle_ratio = driver_idle_ratio,
            clk_name = "clk",
            valid_port_name = "pipe_in_valid",
            ready_port_name = "pipe_in_ready",
            data_ports_name = ["pipe_in_data"]
        )
        
        self.pipe_out_recv = PipeOutReceiver(
            dut = dut,
            idle_ratio = recv_idle_ratio,
            clk_name = "clk",
            valid_port_name = "pipe_out_valid",
            ready_port_name = "pipe_out_ready",
            data_ports_name = ["pipe_out_data"]
        )
        
        self.cases_num = cases_num
        self.data_width = data_width
        self.ref_buffer = queue.Queue(maxsize=cases_num)


    async def drive_pipe_in(self):
        for i in range(self.cases_num):
            random_data = random.randint(0, pow(2, self.data_width) - 1)
            self.ref_buffer.put(random_data)
            await self.pipe_in_driver.drive_pipe_in([random_data])
            self.log.info(f"Drive {i} testcase: data={random_data}")
            
    async def check_pipe_out(self):
        for i in range(self.cases_num):
            dut_data = await self.pipe_out_recv.recv_pipe_out()
            dut_data = dut_data[0].integer
            ref_data = self.ref_buffer.get()
            assert dut_data == ref_data, f"Fail {i} testcase: ref={ref_data} dut_data={dut_data}"
            self.log.info(f"Pass {i} testcase: data={ref_data}")
    
    async def run_test(self):
        await self.start_gen_clk()
        await self.reset_dut()
        cocotb.start_soon(self.drive_pipe_in())
        check_thread = cocotb.start_soon(self.check_pipe_out())
        await check_thread
        self.log.info(f"Pass all {self.cases_num} testcases successfully")
            

