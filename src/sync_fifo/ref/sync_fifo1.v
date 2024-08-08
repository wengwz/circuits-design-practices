
module sync_fifo#(
    parameter DSIZE = 8,
    parameter ASIZE = 4
) (
    input clk,
    input reset,
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

    // Address Pointers
    reg [ASIZE:0] raddr_counter, waddr_counter;
    wire [ASIZE - 1 : 0] raddr = raddr_counter[ASIZE - 1 : 0];
    wire [ASIZE - 1 : 0] waddr = waddr_counter[ASIZE - 1 : 0];
    
    wire tag_equal = raddr_counter[ASIZE] == waddr_counter[ASIZE];
    wire addr_equal = raddr == waddr;

    //
    always @(posedge clk) begin
        if (reset) begin
            raddr_counter <= 0;
        end
        else if (rinc && !rempty) begin
            raddr_counter <= raddr_counter + 1;
        end
    end


    always@(posedge clk) begin
        if (reset) begin
            waddr_counter <= 0;
        end
        else if (winc && !wfull) begin
            waddr_counter <= waddr_counter + 1;
            mem[waddr] <= wdata;
        end
    end

    assign wfull = !tag_equal && addr_equal;
    assign rempty = tag_equal && addr_equal;
    assign rdata = mem[raddr];
    
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

`ifdef DUMP_WAVE
    initial begin
        $dumpfile("ref_sync_fifo.vcd");
        $dumpvars;
    end
`endif
endmodule
