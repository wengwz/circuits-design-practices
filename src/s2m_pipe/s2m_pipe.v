
module s2m_pipe #(
    parameter DATA_WIDTH = 256
)(
    input clk,
    input reset,

    // pipe_in
    input pipe_in_valid,
    input [DATA_WIDTH - 1 : 0] pipe_in_data,
    output pipe_in_ready,

    // pipe_out
    output pipe_out_valid,
    output [DATA_WIDTH - 1 : 0] pipe_out_data,
    input pipe_out_ready
);

`ifdef WAVE
    initial begin
        $dumpfile("wave.vcd");
        $dumpvars;
    end
`endif 
endmodule