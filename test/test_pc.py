import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge


@cocotb.test()
async def test_reset_and_increment(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.pc_value.value) == 0, "reset must set PC to zero"

    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.pc_value.value) == 0, "PC must remain zero while reset is asserted"

    await FallingEdge(dut.clk)
    dut.rst.value = 0

    for expected_pc in range(1, 4):
        await RisingEdge(dut.clk)
        await ReadOnly()
        assert int(dut.pc_value.value) == expected_pc, f"expected PC {expected_pc}"

    await FallingEdge(dut.clk)
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.pc_value.value) == 0, "reset must clear PC again"
