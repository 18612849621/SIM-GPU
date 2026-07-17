SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES := $(PWD)/src/pc.sv $(PWD)/src/regfile.sv $(PWD)/src/instruction_rom.sv $(PWD)/src/gpu_top.sv
export PYTHONPATH := $(PWD)/test:$(PYTHONPATH)

.PHONY: test test_gpu_top test_pc test_regfile test_const_halt

test: test_gpu_top test_pc test_regfile test_const_halt

test_gpu_top:
	$(MAKE) sim TOPLEVEL=gpu_top COCOTB_TEST_MODULES=test_reset SIM_BUILD=sim_build/gpu_top

test_pc:
	$(MAKE) sim TOPLEVEL=pc COCOTB_TEST_MODULES=test_pc SIM_BUILD=sim_build/pc

test_regfile:
	$(MAKE) sim TOPLEVEL=regfile COCOTB_TEST_MODULES=test_regfile SIM_BUILD=sim_build/regfile

test_const_halt:
	$(MAKE) sim TOPLEVEL=gpu_top COCOTB_TEST_MODULES=test_const_halt SIM_BUILD=sim_build/const_halt

include $(shell cocotb-config --makefiles)/Makefile.sim
