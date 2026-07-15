`default_nettype none

module pc (
    input  logic        clk,
    input  logic        rst,
    output logic [31:0] pc_value
);
    always_ff @(posedge clk) begin
        if (rst) begin
            pc_value <= 32'd0;
        end else begin
            pc_value <= pc_value + 32'd1;
        end
    end
endmodule

`default_nettype wire
