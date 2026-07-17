`default_nettype none

module instruction_rom #(
    parameter INIT_FILE = "test/programs/const_halt.hex",
    parameter DEPTH = 16,
    parameter PROGRAM_WORDS = 3
) (
    input  logic [31:0] address,
    output logic [15:0] instruction
);
    logic [15:0] memory [0:DEPTH-1];
    integer i;

    initial begin
        for (i = 0; i < DEPTH; i = i + 1) begin
            memory[i] = 16'h0000;
        end
        $readmemh(INIT_FILE, memory, 0, PROGRAM_WORDS - 1);
    end

    assign instruction = address < DEPTH ? memory[address] : 16'h0000;
endmodule

`default_nettype wire
