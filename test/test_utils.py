
import random
import queue
import logging

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

class ClockSetting:
    def __init__(self, name:str, period:int, unit:str="ns"):
        self.name = name
        self.period = period
        self.unit = unit
    
    def __str__(self) -> str:
        return f"{self.name}(period={self.period} unit={self.unit})"

class ResetSetting:
    def __init__(self, name:str, duration:int, level:bool, clk_name:str):
        self.name = name
        self.duration = duration
        self.level = level
        self.clk_name = clk_name
    
    def __str__(self) -> str:
        return f"rst={self.name}(level={self.level} duration={self.duration} clk={self.clk_name})"

class BasicTestbench:
    """
    A basic tester whichs wraps some shared operations related with clock and reset  
    """
    def __init__(self, log, dut, clks:dict[ClockSetting], rsts:dict[ResetSetting]):
        self.log = log
        self.dut = dut
        
        if not isinstance(clks, dict):
            assert isinstance(clks, ClockSetting)
            clks = {clks.name: clks}
            
        if not isinstance(rsts, dict):
            assert isinstance(rsts, ResetSetting)
            rsts = {rsts.name: rsts}
        
        self.clk_settings = clks
        self.clk_ports = {}
        self.is_clks_start = {}
        for clk_name in self.clk_settings.keys():
            assert hasattr(dut, clk_name)
            self.clk_ports[clk_name] = getattr(dut, clk_name)
            self.is_clks_start[clk_name] = False

        self.rst_settings = rsts
        self.rst_ports = {}
        for rst_name in self.rst_settings.keys():
            assert hasattr(dut, rst_name)
            self.rst_ports[rst_name] = getattr(dut, rst_name)
        
    async def start_gen_clk(self, clk_name:str=None):
        if clk_name == None:
            assert len(self.clk_settings) == 1, "The name of clock signal needs is unspecified"
            clk_name = list(self.clk_settings.keys())[0]
        else:
            assert clk_name in self.clk_settings, f"Invalid clock name: {clk_name}"
            
        clk_setting = self.clk_settings[clk_name]
        await cocotb.start(Clock(self.clk_ports[clk_name], clk_setting.period, clk_setting.unit).start())
        self.is_clks_start[clk_name] = True
        self.log.info(f"Start generating clock signal {clk_setting}")
    
    async def reset_dut(self, rst_name:str=None):
        if rst_name == None:
            assert len(self.rst_settings) == 1, "The name of reset signal is unspecified"
            rst_name = list(self.rst_settings.keys())[0]
        else:
            assert rst_name in self.rst_settings, f"Invalid reset name: {rst_name}"
        
        rst_setting = self.rst_settings[rst_name]
        clk_name = rst_setting.clk_name
        
        assert clk_name in self.is_clks_start, f"The clk port {clk_name} for rst {rst_name} is invalid"
        assert self.is_clks_start[clk_name], f"The clk port {clk_name} for rst {rst_name} is idle"
        
        self.rst_ports[rst_name].value = rst_setting.level
        for _ in range(rst_setting.duration + 1):
            await RisingEdge(self.clk_ports[clk_name])
        
        self.rst_ports[rst_name].value = not rst_setting.level
        await RisingEdge(self.clk_ports[clk_name])
        self.log.info(f"Complete resetting dut through port {rst_setting}")
    

class PipeInDriver:
    def __init__(self, dut, idle_ratio:float, clk_name:str, valid_port_name:str, ready_port_name:str, data_ports_name:list[str]):
        self.clk_port = getattr(dut, clk_name)
        self.valid_port = getattr(dut, valid_port_name)
        self.ready_port = getattr(dut, ready_port_name)
        if not isinstance(data_ports_name, list):
            assert isinstance(data_ports_name, str)
            data_ports_name = [data_ports_name]
        self.data_ports = [getattr(dut, data_port_name) for data_port_name in data_ports_name]
        self.idle_ratio = idle_ratio
        self.valid_port.value = False
        
        return
    
    async def drive_pipe_in(self, data_list:list):
        if not isinstance(data_list, list):
            data_list = [data_list]
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
        if not isinstance(data_ports_name, list):
            assert isinstance(data_ports_name, str)
            data_ports_name = [data_ports_name]
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
    def __init__(self, dut, 
                 data_width:int, cases_num:int, 
                 driver_idle_ratio:float, recv_idle_ratio:float,
                 pipe_in_ports:dict=None, pipe_out_ports:dict=None):
        self.log = logging.getLogger("TestPipe")
        self.log.setLevel(logging.DEBUG)

        if pipe_in_ports == None:
            pipe_in_ports = {
                "valid": "pipe_in_valid",
                "ready": "pipe_in_ready",
                "data" : "pipe_in_data",
                "clk"  : "clk",
                "rst"  : "reset"
            }
        
        if pipe_out_ports == None:
            pipe_out_ports = {
                "valid": "pipe_out_valid",
                "ready": "pipe_out_ready",
                "data" : "pipe_out_data",
                "clk"  : "clk",
                "rst"  : "reset"
            }

        self.pipe_in_ports = pipe_in_ports
        self.pipe_out_ports = pipe_out_ports
        
        self.clk_settings = dict()
        self.rst_settings = dict()
        
        for ports in [pipe_in_ports, pipe_out_ports]:
            clk_name = ports["clk"]
            if clk_name not in self.clk_settings:
                self.clk_settings[clk_name] = ClockSetting(name=clk_name, period=10)
            
            rst_name = ports["rst"]
            if rst_name not in self.rst_settings:
                self.rst_settings[rst_name] = ResetSetting(name=rst_name, duration=3, level=True, clk_name=clk_name)

        
        super().__init__(
            log = self.log,
            dut = dut,
            clks = self.clk_settings,
            rsts = self.rst_settings
        )
        
        self.pipe_in_driver = PipeInDriver(
            dut = dut,
            idle_ratio = driver_idle_ratio,
            clk_name = pipe_in_ports["clk"],
            valid_port_name = pipe_in_ports["valid"],
            ready_port_name = pipe_in_ports["ready"],
            data_ports_name = pipe_in_ports["data"]
        )
        
        self.pipe_out_recv = PipeOutReceiver(
            dut = dut,
            idle_ratio = recv_idle_ratio,
            clk_name = pipe_out_ports["clk"],
            valid_port_name = pipe_out_ports["valid"],
            ready_port_name = pipe_out_ports["ready"],
            data_ports_name = pipe_out_ports["data"]
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
        for clk_name in self.clk_settings.keys():
            await self.start_gen_clk(clk_name)
        
        for rst_name in self.rst_settings.keys():
            await self.reset_dut(rst_name)
        
        cocotb.start_soon(self.drive_pipe_in())
        check_thread = cocotb.start_soon(self.check_pipe_out())
        await check_thread
        self.log.info(f"Pass all {self.cases_num} testcases successfully")

