
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

module async_fifo#(
    parameter DWIDTH = 8;
    parameter AWIDTH = 4;
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

    
    
endmodule
