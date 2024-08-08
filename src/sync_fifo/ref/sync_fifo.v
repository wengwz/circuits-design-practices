
module fifo_mem#(
    parameter DSIZE = 8,
    parameter ASIZE = 4
)(
    input clk,
    input wen,
    input [ASIZE - 1 : 0] waddr,
    input [DSIZE - 1 : 0] wdata,
    output [DSIZE - 1 : 0] rdata,
    input [ASIZE - 1 : 0] raddr
);
    reg [DSIZE - 1 : 0] rdata;
    reg [DSIZE - 1 : 0] mem [0 : (1 << ASIZE) - 1];

    always @(posedge clk) begin
        if (wen) begin
            mem[waddr] <= wdata;
        end
    end

    // registered memory output
    always@(posedge clk) begin
        rdata <= mem[raddr];
    end

    // direct memory output
    // always@(*) begin
    //     rdata = mem[raddr];
    // end
endmodule

////////
// synchronous fifo with registered output control full/empty signal
///////
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
    reg wfull, rempty;
    reg [ASIZE : 0] rptr_r, wptr_r;

    wire [ASIZE - 1 : 0] rptr_addr = rptr_r[ASIZE - 1 : 0];
    wire [ASIZE - 1 : 0] wptr_addr = wptr_r[ASIZE - 1 : 0];

    wire mem_wen = winc && !wfull;
    wire mem_ren = rinc && !rempty;
    wire[ASIZE : 0] nxt_rptr = mem_ren ? rptr_r + 1 : rptr_r;
    wire[ASIZE : 0] nxt_wptr = mem_wen ? wptr_r + 1 : wptr_r;

    
    wire nxt_rptr_tag = nxt_rptr[ASIZE];
    wire nxt_wptr_tag = nxt_wptr[ASIZE];
    wire [ASIZE - 1 : 0] nxt_rptr_addr = nxt_rptr[ASIZE - 1 : 0];
    wire [ASIZE - 1 : 0] nxt_wptr_addr = nxt_wptr[ASIZE - 1 : 0];

    // wire nxt_rempty = (nxt_rptr_tag == nxt_wptr_tag) && (nxt_rptr_addr == nxt_wptr_addr);
    wire nxt_rempty = (nxt_rptr_tag == wptr_r[ASIZE]) && (nxt_rptr_addr == wptr_r[ASIZE - 1 : 0]);
    wire nxt_wfull = (nxt_rptr_tag != nxt_wptr_tag) && (nxt_rptr_addr == nxt_wptr_addr);

    fifo_mem#(
        .DSIZE(DSIZE),
        .ASIZE(ASIZE)
    ) fifo_mem_inst(
        .clk  (clk       ),

        .wen  (mem_wen   ),
        .waddr(wptr_addr ),
        .wdata(wdata     ),

        .rdata(rdata     ),
        //.raddr(rptr_addr)
        .raddr(nxt_rptr_addr )
    );

    // Read Logic
    always@(posedge clk) begin
        if (reset) begin
            rptr_r <= 0;
            rempty <= 1'b1;
        end
        else begin
            rptr_r <= nxt_rptr;
            rempty <= nxt_rempty;
        end
    end

    // Write Logic
    always@(posedge clk) begin
        if (reset) begin
            wptr_r <= 0;
            wfull <= 1'b0;
        end
        else begin
            wptr_r <= nxt_wptr;
            wfull <= nxt_wfull;
        end
    end

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
