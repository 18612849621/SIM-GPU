import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge


@cocotb.test()
async def test_reset_write_and_read(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr_a.value = 0
    dut.read_addr_b.value = 1

    await RisingEdge(dut.clk)
    await ReadOnly()

    for first_addr in range(0, 8, 2):
        await FallingEdge(dut.clk)
        dut.read_addr_a.value = first_addr
        dut.read_addr_b.value = first_addr + 1
        await ReadOnly()
        assert int(dut.read_data_a.value) == 0, f"r{first_addr} must reset to zero"
        assert int(dut.read_data_b.value) == 0, f"r{first_addr + 1} must reset to zero"

    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.read_data_a.value) == 0, "registers must remain zero while reset is asserted"
    assert int(dut.read_data_b.value) == 0, "registers must remain zero while reset is asserted"

    await FallingEdge(dut.clk)
    dut.rst.value = 0
    dut.write_enable.value = 0
    dut.write_addr.value = 3
    dut.write_data.value = 0xFFFFFFFF
    dut.read_addr_a.value = 3
    dut.read_addr_b.value = 0
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.read_data_a.value) == 0, "write must be ignored when write_enable is zero"

    await FallingEdge(dut.clk)
    dut.write_enable.value = 1
    dut.write_addr.value = 2
    dut.write_data.value = 0x12345678
    dut.read_addr_a.value = 2
    dut.read_addr_b.value = 6
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.read_data_a.value) == 0x12345678, "r2 must contain its written value"
    assert int(dut.read_data_b.value) == 0, "writing r2 must not change r6"

    await FallingEdge(dut.clk)
    dut.write_addr.value = 6
    dut.write_data.value = 0xA5A5A5A5
    dut.read_addr_a.value = 2
    dut.read_addr_b.value = 6
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.read_data_a.value) == 0x12345678, "r2 must retain its prior value"
    assert int(dut.read_data_b.value) == 0xA5A5A5A5, "r6 must contain its written value"

    await FallingEdge(dut.clk)
    dut.write_addr.value = 2
    dut.write_data.value = 0xCAFEBABE
    dut.read_addr_a.value = 2
    dut.read_addr_b.value = 6
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.read_data_a.value) == 0xCAFEBABE, "same-address read must see the new value after the write edge"
    assert int(dut.read_data_b.value) == 0xA5A5A5A5, "writing r2 must preserve r6"

    await FallingEdge(dut.clk)
    dut.rst.value = 1
    dut.write_enable.value = 1
    dut.write_addr.value = 2
    dut.write_data.value = 0xFFFFFFFF
    dut.read_addr_a.value = 2
    dut.read_addr_b.value = 6
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.read_data_a.value) == 0, "reset must override a simultaneous write to r2"
    assert int(dut.read_data_b.value) == 0, "reset must clear r6"
