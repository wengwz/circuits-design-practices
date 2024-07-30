
module gcd#(
    parameter DATA_WIDTH = 16
)(
    input clk,
    input rst,

    input op_valid_i,
    output op_ready_o,
    input [DATA_WIDTH - 1 : 0] op0_i,
    input [DATA_WIDTH - 1 : 0] op1_i,

    output res_valid_o,
    input res_ready_i,
    output [DATA_WIDTH - 1 : 0] res_o
);

`ifdef DUMP_WAVE
    initial begin
        $dumpfile("gcd.vcd");
        $dumpvars;
    end
`endif
endmodule