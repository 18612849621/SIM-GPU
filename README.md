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

- `gpu_top` 的同步复位与顶层 PC 接线测试；
- 独立 `pc` 模块的复位、保持和逐拍递增测试。

## 学习文档与时序图

- [阶段 0：最小 RTL、时钟与复位](docs/phase-0-basics.md)
- [阶段 1.1：Program Counter（PC）](docs/phase-1-pc.md)

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
├── CLAUDE.md              # 分阶段开发计划与协作约束
├── README.md              # 项目说明与本地环境配置
├── Makefile               # 构建与仿真入口
├── src/
│   ├── gpu_top.sv         # 顶层模块
│   └── pc.sv              # 32 位程序计数器
├── test/
│   ├── test_reset.py      # 顶层复位/接线测试
│   └── test_pc.py         # PC 模块测试
├── docs/                  # 学习笔记
└── .venv/                 # 本地 Python 虚拟环境，不提交到 Git
```

## 当前进度

阶段 0 的仿真骨架已经完成。当前处于阶段 1：实现最小单线程处理器的基础状态；第一个模块是 32 位 PC。下一小步是实现通用寄存器文件。
