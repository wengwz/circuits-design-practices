


module seq_dect(
    input clk,
    input reset,

    input din,
    output dout
);

    reg [3:0] din_buf;

    always @(posedge clk) begin
        if (reset) begin
            din_buf <= 4'b0000;
        end
        else begin
            if (dout) begin
                din_buf <= {3'b000, din};
            end
            else begin
                din_buf <= {din_buf[2:0], din};
            end
        end
    end

    assign dout = (din_buf == 4'b1101);

`ifdef DUMP_WAVE
    initial begin
        $dumpfile("ref_seq_dect.vcd");
        $dumpvars;
    end
`endif

endmodule
