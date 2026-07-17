# SIM-GPU

从零实现、可仿真的教学型 GPU。项目按 [`CLAUDE.md`](CLAUDE.md) 中的阶段计划推进：先完成单线程多周期处理器，再逐步扩展到多线程 SIMD、block 调度与多 core GPU。

## 开发环境

目标平台为 macOS，使用 SystemVerilog 和 Python 测试环境：

| 工具 | 版本/用途 |
| --- | --- |
| Python | 3.11 或更高版本；用于 Cocotb 测试与辅助脚本 |
| Icarus Verilog | SystemVerilog RTL 编译与仿真 |
| Cocotb | Python 驱动的硬件测试框架 |
| GNU Make | 统一的构建与测试入口 |

当前机器已配置 Python `3.11.2`、GNU Make 和 Icarus Verilog `13.0`。

## 首次配置

### 1. 安装 Icarus Verilog

macOS 使用 Homebrew：

```bash
brew install icarus-verilog
```

验证安装：

```bash
iverilog -V
```

### 2. 创建 Python 虚拟环境

所有 Python 依赖安装在项目根目录下的 `.venv/`，不使用系统 Python 安装第三方包：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install cocotb pytest
```

验证 Python 依赖：

```bash
python -c "import cocotb; print(cocotb.__version__)"
pytest --version
```

每次开始开发时激活虚拟环境：

```bash
source .venv/bin/activate
```

结束时退出：

```bash
deactivate
```

## 运行测试

激活虚拟环境后，运行全部硬件测试：

```bash
source .venv/bin/activate
make test
```

当前测试包括：

- `gpu_top` 的同步复位与最小控制器状态测试；
- 独立 `pc` 模块的复位、保持与受控加载测试；
- 独立 `regfile` 模块的同步复位、禁写保持、单地址写入、双端口读取与读写同址测试；
- `CONST; CONST; HALT` 程序的取指、写回、符号扩展与停机测试。

## 学习文档与时序图

- [阶段 0：最小 RTL、时钟与复位](docs/phase-0-basics.md)
- [阶段 1.1：Program Counter（PC）](docs/phase-1-pc.md)
- [阶段 1.2：8×32 位通用寄存器文件](docs/phase-1-register-file.md)
- [阶段 1.3：第一个程序执行闭环](docs/phase-1-const-halt.md)

文档中的时序图统一将逻辑高、低电平画在不同高度；同一列的竖线代表同一时刻，时钟上升沿与寄存器状态变化按列对齐。

```text
clk = 1          ┌────┐     ┌────┐
clk = 0  ────────┘    └─────┘    └──
                    ↑          ↑
                  上升沿       上升沿
```

## 当前目录

```text
SIM-GPU/
├── CLAUDE.md                      # 分阶段开发计划与协作约束
├── README.md                      # 项目说明与本地环境配置
├── Makefile                       # 构建与仿真入口
├── src/
│   ├── gpu_top.sv                 # 顶层模块
│   ├── pc.sv                      # 受控加载的 32 位程序计数器
│   ├── regfile.sv                 # 8×32 位通用寄存器文件
│   └── instruction_rom.sv         # 只读 16 位指令存储器
├── test/
│   ├── programs/const_halt.hex    # 首个测试程序的机器码
│   ├── test_reset.py              # 顶层复位/控制器测试
│   ├── test_pc.py                 # PC 模块测试
│   ├── test_regfile.py            # 寄存器文件模块测试
│   └── test_const_halt.py         # CONST/HALT 程序测试
├── docs/                          # 学习笔记
└── .venv/                         # 本地 Python 虚拟环境，不提交到 Git
```

## 当前进度

阶段 0 的仿真骨架已经完成。当前处于阶段 1：PC、寄存器文件，以及 `CONST`/`HALT` 的取指、译码和写回闭环均已完成并测试。下一小步是独立定义并实现 32 位 ADD ALU。
