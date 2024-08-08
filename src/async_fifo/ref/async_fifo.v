
module fifomem#(
    parameter DWIDTH = 8,
    parameter AWIDTH = 4
) (
    // Write Ports
    input wclk,
    input wen,
    input [AWIDTH - 1 : 0] waddr,
    input [DWIDTH - 1 : 0] wdata,

    // Read Ports
    input [AWIDTH - 1 : 0] raddr,
    output [DWIDTH - 1 : 0] rdata
);

    localparam MDEPTH = 1 << AWIDTH;
    reg [DWIDTH - 1 : 0] mem [0 : MDEPTH - 1];

    always @(posedge wclk) begin
        if (wen) begin
            mem[waddr] <= wdata;
        end
    end

    assign rdata = mem[raddr];
endmodule

module async_sampling#(
    parameter WIDTH = 4
)(
    input clk,
    input reset,
    input [WIDTH - 1 : 0] din,
    output [WIDTH - 1 : 0] dout
);

    reg [WIDTH - 1 : 0] async_reg0, async_reg1;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            async_reg0 <= 0;
            async_reg1 <= 0;
        end 
        else begin
            async_reg0 <= din;
            async_reg1 <= async_reg0;
        end
    end

    assign dout = async_reg1;
endmodule

module read_logic#(
    parameter AWIDTH = 4
)(
    input rclk,
    input rreset,
    input rinc,

    input [AWIDTH - 1 : 0] gray_wptr,

    output rempty,
    output [AWIDTH - 1 : 0] gray_rptr,
    output [AWIDTH - 1 : 0] bin_rptr
);

    reg rempty;
    reg [AWIDTH - 1 : 0] gray_rptr;
    reg [AWIDTH - 1 : 0] bin_rptr;

    wire [AWIDTH - 1 : 0] nxt_bin_rptr;
    wire [AWIDTH - 1 : 0] nxt_gray_rptr;

    always @(posedge rclk or posedge rreset) begin
        if (rreset) begin
            rempty <= 1'b1;
            gray_rptr <= 0;
            bin_rptr <= 0;
        end
        else begin
            rempty <= nxt_gray_rptr == gray_wptr;
            gray_rptr <= nxt_gray_rptr;
            bin_rptr <= nxt_bin_rptr;
        end        
    end

    assign nxt_bin_rptr = (rinc && !rempty) ? bin_rptr + 1 : bin_rptr;
    assign nxt_gray_rptr = (nxt_bin_rptr >> 1) ^ nxt_bin_rptr;
endmodule

module write_logic#(
    parameter AWIDTH = 4
)(
    input wclk,
    input wreset,
    input winc,

    input [AWIDTH - 1 : 0] gray_rptr,

    output wfull,
    output mem_wen,
    output [AWIDTH - 1 : 0] bin_wptr,
    output [AWIDTH - 1 : 0] gray_wptr
);

    reg wfull, bin_wptr, gray_wptr;

    wire nxt_wfull;
    wire [AWIDTH - 1 : 0] nxt_bin_wptr, nxt_gray_wptr;

    wire nxt_gray_wptr_msb = nxt_gray_wptr[AWIDTH - 1 : AWIDTH - 2];
    wire nxt_gray_wptr_lsb = nxt_gray_wptr[AWIDTH - 2 : 0];
    wire gray_rptr_msb = gray_rptr[AWIDTH - 1 : AWIDTH - 2];
    wire gray_rptr_lsb = gray_rptr[AWIDTH - 2 : 0];


    always @(posedge wclk or posedge wreset) begin
        if (wreset) begin
            wfull <= 1'b0;
            bin_wptr <= 0;
            gray_wptr <= 0;
        end
        else begin
            wfull <= nxt_wfull;
            bin_wptr <= nxt_bin_wptr;
            gray_wptr <= nxt_gray_wptr;
        end
    end

    assign nxt_bin_wptr = mem_wen ? bin_wptr + 1 : bin_wptr;
    assign nxt_gray_wptr = (nxt_bin_wptr >> 1) ^ nxt_bin_wptr;
    assign nxt_wfull = &(nxt_gray_wptr_msb ^ gray_rptr_msb) && (gray_rptr_lsb == nxt_gray_wptr_lsb);
    assign mem_wen = !wfull & winc;
endmodule

module async_fifo#(
    parameter DWIDTH = 8,
    parameter AWIDTH = 4
) (
    // Write Ports
    input wclk,
    input wreset,
    input winc,
    output wfull,
    input [DWIDTH - 1 : 0] wdata,

    // Read Ports
    input rclk,
    input rreset,
    input rinc,
    output rempty,
    output [DWIDTH - 1 : 0] rdata
);

    wire mem_wen;
    wire [AWIDTH - 1 : 0] bin_wptr, bin_rptr;
    wire [AWIDTH - 1 : 0] gray_wptr, gray_rptr;
    wire [AWIDTH - 1 : 0] gray_wptr_rsync, gray_rptr_wsync;

    fifomem#(
        .DWIDTH(DWIDTH), 
        .AWIDTH(AWIDTH)
    ) fifomem_inst(
        .wclk (wclk    ),
        .wen  (mem_wen ),
        .waddr(bin_wptr),
        .wdata(wdata   ),

        .raddr(bin_rptr),
        .rdata(rdata   )
    );

    async_sampling#(AWIDTH) gray_wptr_rsync_inst(
        .clk  (rclk),
        .reset(rreset),
        .din  (gray_wptr),
        .dout (gray_wptr_rsync)
    );
    
    async_sampling#(AWIDTH) gray_rptr_wsync_inst(
        .clk  (wclk),
        .reset(wreset),
        .din  (gray_rptr),
        .dout (gray_rptr_wsync)
    );

    read_logic#(AWIDTH) read_logic_inst(
        .rclk  (rclk    ),
        .rreset(rreset  ),
        .rinc  (rinc    ),

        .gray_wptr (gray_wptr_rsync),

        .rempty   (rempty  ),
        .gray_rptr(gray_rptr),
        .bin_rptr (bin_rptr )
    );

    write_logic#(AWIDTH) write_logic_inst(
        .wclk  (wclk    ),
        .wreset(wreset  ),
        .winc  (winc    ),

        .gray_rptr(gray_rptr_wsync),

        .wfull    (wfull   ),
        .mem_wen  (mem_wen ),
        .bin_wptr (bin_wptr),
        .gray_wptr(gray_wptr)
    );
endmodule


module async_fifo_test_wrapper#(
    parameter DWIDTH = 8,
    parameter AWIDTH = 4
) (
    // Write Ports
    input wclk,
    input wreset,
    input [DWIDTH - 1:0] wdata,
    input wvalid,
    output wready,

    // Read Ports
    input rclk,
    input rreset,
    output [DWIDTH - 1:0] rdata,
    output rvalid,
    input rready
);
    wire wfull, rempty;

    async_fifo #(
        .DWIDTH(DWIDTH),
        .AWIDTH(AWIDTH)
    ) async_fifo (
        .wclk  (wclk  ),
        .wreset(wreset),
        .wdata (wdata ),
        .winc  (wvalid),
        .wfull (wfull ),

        .rclk  (rclk  ),
        .rreset(rreset),
        .rdata (rdata ),
        .rempty(rempty),
        .rinc  (rready)
    );

    assign wready = !wfull;
    assign rvalid = !rempty;

`ifdef DUMP_WAVE
    initial begin
        $dumpfile("ref_async_fifo.vcd");
        $dumpvars;
    end
`endif
endmodule