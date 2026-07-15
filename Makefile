SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES := $(PWD)/src/pc.sv $(PWD)/src/gpu_top.sv
export PYTHONPATH := $(PWD)/test:$(PYTHONPATH)

.PHONY: test test_gpu_top test_pc

test: test_gpu_top test_pc

test_gpu_top:
	$(MAKE) sim TOPLEVEL=gpu_top COCOTB_TEST_MODULES=test_reset SIM_BUILD=sim_build/gpu_top

test_pc:
	$(MAKE) sim TOPLEVEL=pc COCOTB_TEST_MODULES=test_pc SIM_BUILD=sim_build/pc

include $(shell cocotb-config --makefiles)/Makefile.sim
