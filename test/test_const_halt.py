import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge


async def next_rising_edge(dut):
    await RisingEdge(dut.clk)
    await ReadOnly()


@cocotb.test()
async def test_const_halt_program(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await next_rising_edge(dut)

    await FallingEdge(dut.clk)
    dut.rst.value = 0

    await next_rising_edge(dut)
    assert int(dut.state.value) == 1, "first edge must enter EXECUTE"
    assert int(dut.pc.value) == 0, "FETCH must keep PC at zero"
    assert int(dut.instruction.value) == 0x14A5, "first instruction must be CONST r2, 165"

    await next_rising_edge(dut)
    assert int(dut.state.value) == 0, "CONST execution must return to FETCH"
    assert int(dut.pc.value) == 1, "CONST execution must advance PC"
    assert int(dut.debug_reg2.value) == 0x000000A5, "CONST must write 165 to r2"
    assert int(dut.debug_reg7.value) == 0, "writing r2 must not change r7"

    await next_rising_edge(dut)
    assert int(dut.state.value) == 1, "second fetch must enter EXECUTE"
    assert int(dut.pc.value) == 1, "second FETCH must keep PC at one"
    assert int(dut.instruction.value) == 0x1FFF, "second instruction must be CONST r7, -1"

    await next_rising_edge(dut)
    assert int(dut.state.value) == 0, "second CONST execution must return to FETCH"
    assert int(dut.pc.value) == 2, "second CONST execution must advance PC"
    assert int(dut.debug_reg2.value) == 0x000000A5, "r2 must retain its value"
    assert int(dut.debug_reg7.value) == 0xFFFFFFFF, "CONST must sign extend -1 into r7"

    await next_rising_edge(dut)
    assert int(dut.state.value) == 1, "HALT fetch must enter EXECUTE"
    assert int(dut.pc.value) == 2, "HALT fetch must keep PC at two"
    assert int(dut.instruction.value) == 0xF000, "third instruction must be HALT"

    await next_rising_edge(dut)
    assert dut.halted.value == 1, "HALT execution must assert halted"
    assert int(dut.state.value) == 2, "HALT execution must enter HALTED"
    assert int(dut.pc.value) == 2, "HALT must keep PC at its own address"
    assert dut.reg_write_enable.value == 0, "HALT must not write a register"

    await next_rising_edge(dut)
    assert dut.halted.value == 1, "halted must remain asserted"
    assert int(dut.state.value) == 2, "controller must remain HALTED"
    assert int(dut.pc.value) == 2, "PC must remain stopped"
    assert int(dut.debug_reg2.value) == 0x000000A5, "HALT must preserve r2"
    assert int(dut.debug_reg7.value) == 0xFFFFFFFF, "HALT must preserve r7"
