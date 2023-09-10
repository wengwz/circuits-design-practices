# Intro
This repo provides a collection of practices of designing important but tricky digital circuits. These circuit components are commonly used in digital system designs or frequently involved in job interviews. For each practice, problem description, testbench and reference solution are all provided. Here is a list of all available practices:
- m2s_pipe: pipeline valid-ready based bus with registered valid and payload signals;
- s2m_pipe: pipeline valid-ready vased bus with registered ready signal;


# Get Started


## Environment Setup
It's recommended to set up development environment on Linux-based system. Here is a list of dependencies:
- Iverilog: open-source HDL simulator;
- Gtkwave: view the waves of circuit simulation;
- Cocotb: python-based verification framework for RTL designs;
- Cocotb-test: provide python unit testing capabilities for cocotb;

For instance, to install them on the Ubuntu distribution, you can follow commands below:
```sh
sudo apt-get update -y
sudo apt-get -y iverilog gtkwave pip
pip install cocotb cocotb-test
```
## Write Your Design
For each practice, there is an individual folder containing design specification, a starting template and reference solution under the directory [./src](./src/).

```sh
src
├── m2s_pipe # the directory for practice m2s_pipe
│   ├── m2s_pipe.v # the starting template for m2s_pipe
│   ├── README.md  # design specification of m2s_pipe
│   └── ref
│       └── m2s_pipe.v # reference solution of m2s_pipe
└── ...
```
You need to complete the start template based on requirements in the design specification without modifying the module interfaces. It's not recommended to refer to given solution before finishing your own design.

## Verify Your Solution
For each practice, there is a python-based testbench using cocotb package under the directory [./test](./test/). Taking the practice m2s_pipe as an example, after finishing your implementation, you can launch the testbench by:
```sh
cd ./test
make sim TOP=m2s_pipe # specify the component to be test by TOP variable
```
The reault of simulation will be displayed on the terminal and the waveform is located in ./test/build/m2s_pipe/wave.vcd.

# Contributing
You are welcome to contribute to this repo by offering circuit design problems that you have ever encountered in the job interviews or some important subcompnents frequently used in digital system design. You can commit either an issue only containg specification of the circuit design problem or a pull request involving both problem description and codes of the starting template and testbench. And for any questions about existing practices, you can also commit issues or pull requests.



