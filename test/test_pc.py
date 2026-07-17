import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge


@cocotb.test()
async def test_reset_hold_and_load(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.pc_write_enable.value = 1
    dut.pc_next.value = 0x12345678
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.pc_value.value) == 0, "reset must clear PC"

    await FallingEdge(dut.clk)
    dut.rst.value = 0
    dut.pc_write_enable.value = 0
    dut.pc_next.value = 0xFFFFFFFF
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.pc_value.value) == 0, "PC must hold when write enable is zero"

    await FallingEdge(dut.clk)
    dut.pc_write_enable.value = 1
    dut.pc_next.value = 0x00000025
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.pc_value.value) == 0x25, "PC must load pc_next when write enabled"

    await FallingEdge(dut.clk)
    dut.pc_write_enable.value = 0
    dut.pc_next.value = 0x00000099
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.pc_value.value) == 0x25, "PC must retain a loaded value when disabled"

    await FallingEdge(dut.clk)
    dut.rst.value = 1
    dut.pc_write_enable.value = 1
    dut.pc_next.value = 0xFFFFFFFF
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.pc_value.value) == 0, "reset must override a simultaneous PC load"
