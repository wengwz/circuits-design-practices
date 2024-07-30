
module my_reg(
    input clk,
    input rst,
    input [7:0] op_i,
    output [7:0] op_o
);
    reg [7:0] op_reg;
    always @(posedge clk) begin
        if (rst) begin
            op_reg <= 8'h00;
        end 
        else begin
            op_reg <= op_i;
        end 
    end

    assign op_o = op_reg;

    initial begin
        $dumpfile("reg.vcd");
        $dumpvars;
    end
endmodule