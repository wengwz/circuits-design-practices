# Introduction
The `gcd` module is designed to compute the greatest common divisor([GCD](https://en.wikipedia.org/wiki/Greatest_common_divisor)) of two input opereands using Euclid's algorithm. The pseudo-code of Euclid's algorithm is as follows:
```python
def gcd(a, b):
    if a == 0:
        return b
    else if a >= b:
        return gcd(a-b, b)
    else:
        return gcd(b, a)
```
Basically, what Euclid's algorithm does is to subtract the smaller number from the greater number iteratively until the smaller one reaches zeros. Because the number of iterations depends on the values of input operands, the computation latency of `gcd` module is not fixed and varies with the input operands dynamically. So when implementing Euclid's algorithm as a hardware module, it's necessary to guard the operand and results ports with some control signals for the correct interations with other modules. And this practice requires *valid-ready* handshake-based control signals to guard the transactions of both input and output data. For details of `valid-ready` handshake protocol, you can refer to [s2m_pipe](../m2s_pipe/README.md) pratice or this [blog](https://zipcpu.com/blog/2021/08/28/axi-rules.html). 

# Specification
The interface definition of gcd module to be implemented in this practice is as follows:

<style>
.center 
{
  width: auto;
  display: table;
  margin-left: auto;
  margin-right: auto;
}
</style>

<div class="center">

| name | direction | width | description |
| :----: | :----:  | :----:  | :----:      |
| clk        | in  | 1-bit | clock signal|
| rst        | in  | 1-bit | synchronous and active high reset signal |
| op_valid_i | in  | 1-bit | indicate that signals on `op1_i` and `op2_i` are valid |
| op_ready_o | out | 1-bit | indicate that `gcd` module is ready to receive input data|
| op1_i      | in  | `DATA_WIDTH` | the first input operand |
| op2_i      | in  | `DATA_WIDTH` | the second input operand |
| res_valid_o| out | 1-bit | indicate that signals on `res_o` are valid|
| res_ready_i| in  | 1-bit | indicate that the downstream module is ready to receive result |
| res_o      | out | `DATA_WIDTH` | the computation result |

</div>

The timing diagram of input and output signals for an example computation task is shown as follows:
<div align=center><img src="../../doc/gcd.png" width="70%"></div>