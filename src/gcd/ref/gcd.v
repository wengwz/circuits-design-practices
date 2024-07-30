
module gcd#(
    parameter DATA_WIDTH = 16
)(
    input clk,
    input rst,

    input op_valid_i,
    output op_ready_o,
    input [DATA_WIDTH - 1 : 0] op0_i,
    input [DATA_WIDTH - 1 : 0] op1_i,

    output res_valid_o,
    input res_ready_i,
    output [DATA_WIDTH - 1 : 0] res_o
);

    reg has_data_reg;
    reg [DATA_WIDTH - 1 : 0] op0_reg, op1_reg;

    always@(posedge clk) begin
        if (rst) begin
            has_data_reg <= 1'b0;
        end
        else if (op_ready_o && op_valid_i) begin
            has_data_reg <= 1'b1;
        end
        else if (res_valid_o && res_ready_i) begin
            has_data_reg <= 1'b0;
        end
    end

    always@(posedge clk) begin
        if (rst) begin
            op0_reg <= 0;
        end
        else if (op_ready_o && op_valid_i) begin
            op0_reg <= op0_i;
            op1_reg <= op1_i;
        end
        else if (op0_reg != 0) begin
            op0_reg <= (op0_reg >= op1_reg) ? (op0_reg - op1_reg) : op1_reg;
            op1_reg <= (op0_reg >= op1_reg) ? op1_reg : op0_reg;
        end
    end

    assign res_valid_o = has_data_reg && (op0_reg == 0);
    assign res_o = op1_reg;
    assign op_ready_o = !has_data_reg;

`ifdef DUMP_WAVE
    initial begin
        $dumpfile("ref_gcd.vcd");
        $dumpvars;
    end
`endif
endmodule