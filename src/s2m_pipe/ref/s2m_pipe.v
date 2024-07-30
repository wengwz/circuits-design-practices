
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
    reg pipe_valid_r;
    reg pipe_ready_r;
    reg [DATA_WIDTH - 1 : 0] pipe_data_r;

    always @(posedge clk) begin
        if (reset) begin
            pipe_ready_r <= 1'b0;
        end
        else begin
            pipe_ready_r <= pipe_out_ready;
        end
    end

    always @(posedge clk) begin
        if (reset) begin
            pipe_valid_r <= 1'b0;
        end
        else if (pipe_in_ready && !pipe_out_ready) begin
            pipe_valid_r <= pipe_in_valid;
        end
        else if (pipe_out_ready) begin
            pipe_valid_r <= 1'b0;
        end
    end

    always@(posedge clk) begin
        if (pipe_in_ready && !pipe_out_ready) begin
            pipe_data_r <= pipe_in_data;
        end
    end

    assign pipe_out_valid = pipe_valid_r || pipe_in_valid;
    assign pipe_out_data = pipe_valid_r ? pipe_data_r : pipe_in_data;
    assign pipe_in_ready = !pipe_valid_r;

`ifdef DUMP_WAVE
    initial begin
        $dumpfile("s2m_pipe.vcd");
        $dumpvars;
    end
`endif 
endmodule