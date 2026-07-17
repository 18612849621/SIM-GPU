`default_nettype none

module regfile (
    input  logic        clk,
    input  logic        rst,
    input  logic        write_enable,
    input  logic [2:0]  write_addr,
    input  logic [31:0] write_data,
    input  logic [2:0]  read_addr_a,
    input  logic [2:0]  read_addr_b,
    output logic [31:0] read_data_a,
    output logic [31:0] read_data_b
);
    logic [31:0] registers [0:7];
    integer i;

    always_ff @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 8; i = i + 1) begin
                registers[i] <= 32'd0;
            end
        end else if (write_enable) begin
            registers[write_addr] <= write_data;
        end
    end

    assign read_data_a = registers[read_addr_a];
    assign read_data_b = registers[read_addr_b];
endmodule

`default_nettype wire
