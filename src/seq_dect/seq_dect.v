

module seq_dect(
    input clk,
    input reset,

    input din,
    output dout
);

`ifdef DUMP_WAVE
    initial begin
        $dumpfile("seq_dect.vcd");
        $dumpvars;
    end
`endif

endmodule