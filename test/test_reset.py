import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge


@cocotb.test()
async def test_reset_and_initialization(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert dut.initialized.value == 0, "reset must clear initialized"
    assert int(dut.pc.value) == 0, "reset must clear PC"
    assert int(dut.state.value) == 0, "reset must return the controller to FETCH"
    assert dut.halted.value == 0, "reset must clear halted"
    assert int(dut.debug_reg2.value) == 0, "reset must clear r2"
    assert int(dut.debug_reg7.value) == 0, "reset must clear r7"

    await FallingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert dut.initialized.value == 1, "initialized must be set after reset is released"
    assert int(dut.pc.value) == 0, "FETCH must keep PC at the current instruction"
    assert int(dut.state.value) == 1, "the first non-reset edge must fetch an instruction"
    assert int(dut.instruction.value) == 0x14A5, "FETCH must latch the first ROM instruction"

    await FallingEdge(dut.clk)
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert dut.initialized.value == 0, "reset must clear initialized again"
    assert int(dut.pc.value) == 0, "reset must clear PC again"
    assert int(dut.state.value) == 0, "reset must return to FETCH again"
    assert dut.halted.value == 0, "reset must clear halted again"
