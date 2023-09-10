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
    reg valid_r;
    reg [DATA_WIDTH - 1 : 0] data_r;

    always @(posedge clk) begin
        if (reset) begin
            valid_r <= 1'b0;
        end
        else if (pipe_in_ready ^ pipe_out_ready) begin
            valid_r <= pipe_in_valid & pipe_in_ready;
            data_r <= pipe_in_data;
        end
    end
    
    assign pipe_in_ready = !valid_r;
    assign pipe_out_valid = valid_r || pipe_in_valid;
    assign pipe_out_data = valid_r ? data_r : pipe_in_data;
`ifdef WAVE
    initial begin
        $dumpfile("wave.vcd");
        $dumpvars;
    end
`endif
endmodule