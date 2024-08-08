
module sync_fifo#(
    parameter DSIZE = 8;
    parameter ASIZE = 4;
) (
    input clk,
    input rst_n,
    // Write Ports
    input [DSIZE-1:0] wdata,
    input winc,
    output wfull,

    // Read Ports
    output [DSIZE-1:0] rdata,
    output rempty,
    input rinc
);
    reg [DSIZE-1:0] mem [0:(1<<ASIZE)-1];


`ifdef DUMP_WAVE
    initial begin
        $dumpfile("sync_fifo.vcd");
        $dumpvars;
    end
`endif
endmodule


module sync_fifo_test_wrapper#(
    parameter DSIZE = 8,
    parameter ASIZE = 4
) (
    input clk,
    input reset,
    // Write Ports
    input [DSIZE-1:0] wdata,
    input wvalid,
    output wready,

    // Read Ports
    output [DSIZE-1:0] rdata,
    output rvalid,
    input rready
);
    wire wfull, rempty;

    sync_fifo #(
        .DSIZE(DSIZE),
        .ASIZE(ASIZE)
    ) fifo (
        .clk   (clk   ),
        .reset (reset ),
        .wdata (wdata ),
        .winc  (wvalid),
        .wfull (wfull ),
        .rdata (rdata ),
        .rempty(rempty),
        .rinc  (rready)
    );

    assign wready = !wfull;
    assign rvalid = !rempty;
    
endmodule