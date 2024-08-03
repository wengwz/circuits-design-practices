

module seq_dect(
    input clk,
    input reset,

    input din,
    output dout
);
    parameter STATE_IDLE = 3'd0;
    parameter STATE_FIRST_BIT = 3'd1;
    parameter STATE_SECOND_BIT = 3'd2;
    parameter STATE_THIRD_BIT = 3'd3;
    parameter STATE_LAST_BIT = 3'd4;

    reg [2:0] state_reg, next_state;
    reg dout;

    always @(posedge clk) begin
        if (reset) begin
            state_reg <= STATE_IDLE;
            dout <= 1'b0;
        end
        else begin
            case (state_reg)
                STATE_IDLE: begin
                    if (din) begin
                        state_reg <= STATE_FIRST_BIT;
                    end
                end
                STATE_FIRST_BIT: begin
                    if (din) begin
                        state_reg <= STATE_SECOND_BIT;
                    end
                    else begin
                        state_reg <= STATE_IDLE;
                    end
                end
                STATE_SECOND_BIT: begin
                    if (!din) begin
                        state_reg <= STATE_THIRD_BIT;
                    end
                end
                STATE_THIRD_BIT: begin
                    if (din) begin
                        state_reg <= STATE_LAST_BIT;
                        dout <= 1'b1;
                    end
                    else begin
                        state_reg <= STATE_IDLE;
                    end
                end
                STATE_LAST_BIT: begin
                    if (din) begin
                        state_reg <= STATE_FIRST_BIT;
                    end
                    else begin
                        state_reg <= STATE_IDLE;
                    end
                    dout <= 1'b0;
                end
            endcase
        end
    end

`ifdef DUMP_WAVE
    initial begin
        $dumpfile("ref_seq_dect.vcd");
        $dumpvars;
    end
`endif

endmodule