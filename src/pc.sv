`default_nettype none

module pc (
    input  logic        clk,
    input  logic        rst,
    input  logic        pc_write_enable,
    input  logic [31:0] pc_next,
    output logic [31:0] pc_value
);
    always_ff @(posedge clk) begin
        if (rst) begin
            pc_value <= 32'd0;
        end else if (pc_write_enable) begin
            pc_value <= pc_next;
        end
    end
endmodule

`default_nettype wire
