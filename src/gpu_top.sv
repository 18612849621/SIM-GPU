`default_nettype none

module gpu_top (
    input  logic        clk,
    input  logic        rst,
    output logic        initialized,
    output logic [31:0] pc,
    output logic        halted,
    output logic        illegal_instruction,
    output logic [15:0] instruction,
    output logic [1:0]  state,
    output logic        reg_write_enable,
    output logic [2:0]  reg_write_addr,
    output logic [31:0] reg_write_data,
    output logic [31:0] debug_reg2,
    output logic [31:0] debug_reg7
);
    localparam logic [1:0] STATE_FETCH   = 2'd0;
    localparam logic [1:0] STATE_EXECUTE = 2'd1;
    localparam logic [1:0] STATE_HALTED  = 2'd2;
    localparam logic [3:0] OPCODE_CONST  = 4'h1;
    localparam logic [3:0] OPCODE_HALT   = 4'hF;

    logic [31:0] pc_next;
    logic        pc_write_enable;
    logic [15:0] rom_instruction;
    logic [15:0] instruction_reg;
    logic [31:0] read_data_a;
    logic [31:0] read_data_b;
    logic [3:0]  opcode;
    logic [2:0]  destination;
    logic [31:0] immediate;

    assign opcode = instruction_reg[15:12];
    assign destination = instruction_reg[11:9];
    assign immediate = {{23{instruction_reg[8]}}, instruction_reg[8:0]};

    pc program_counter (
        .clk(clk),
        .rst(rst),
        .pc_write_enable(pc_write_enable),
        .pc_next(pc_next),
        .pc_value(pc)
    );

    instruction_rom program_memory (
        .address(pc),
        .instruction(rom_instruction)
    );

    regfile register_file (
        .clk(clk),
        .rst(rst),
        .write_enable(reg_write_enable),
        .write_addr(reg_write_addr),
        .write_data(reg_write_data),
        .read_addr_a(3'd2),
        .read_addr_b(3'd7),
        .read_data_a(read_data_a),
        .read_data_b(read_data_b)
    );

    always_comb begin
        pc_next = pc + 32'd1;
        pc_write_enable = 1'b0;
        reg_write_enable = 1'b0;
        reg_write_addr = destination;
        reg_write_data = immediate;

        if (state == STATE_EXECUTE && opcode == OPCODE_CONST) begin
            pc_write_enable = 1'b1;
            reg_write_enable = 1'b1;
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            initialized <= 1'b0;
            halted <= 1'b0;
            illegal_instruction <= 1'b0;
            instruction_reg <= 16'd0;
            state <= STATE_FETCH;
        end else begin
            initialized <= 1'b1;

            case (state)
                STATE_FETCH: begin
                    instruction_reg <= rom_instruction;
                    state <= STATE_EXECUTE;
                end
                STATE_EXECUTE: begin
                    case (opcode)
                        OPCODE_CONST: state <= STATE_FETCH;
                        OPCODE_HALT: begin
                            halted <= 1'b1;
                            state <= STATE_HALTED;
                        end
                        default: begin
                            halted <= 1'b1;
                            illegal_instruction <= 1'b1;
                            state <= STATE_HALTED;
                        end
                    endcase
                end
                default: state <= STATE_HALTED;
            endcase
        end
    end

    assign instruction = instruction_reg;
    assign debug_reg2 = read_data_a;
    assign debug_reg7 = read_data_b;
endmodule

`default_nettype wire
