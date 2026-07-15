`default_nettype none

module gpu_top (
    input  logic        clk,
    input  logic        rst,
    output logic        initialized,
    output logic [31:0] pc
);
    pc program_counter (
        .clk(clk),
        .rst(rst),
        .pc_value(pc)
    );

    always_ff @(posedge clk) begin
        if (rst) begin
            initialized <= 1'b0;
        end else begin
            initialized <= 1'b1;
        end
    end
endmodule

`default_nettype wire
