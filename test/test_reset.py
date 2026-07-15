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

    await FallingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert dut.initialized.value == 1, "initialized must be set after reset is released"
    assert int(dut.pc.value) == 1, "PC must increment after reset is released"

    await FallingEdge(dut.clk)
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert dut.initialized.value == 0, "reset must clear initialized again"
    assert int(dut.pc.value) == 0, "reset must clear PC again"
