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

当前机器已检测到 Python `3.11.2` 和 GNU Make；尚未安装 `iverilog`。

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

## 验证环境

完成阶段 0 后，项目会提供统一的测试命令：

```bash
make test
```

当前仓库处于项目骨架阶段，`Makefile` 和测试尚未创建；在此之前，可用下面命令确认基础工具：

```bash
python3 --version
iverilog -V
make --version
```

## 目录规划

```text
SIM-GPU/
├── CLAUDE.md        # 分阶段开发计划与协作约束
├── README.md        # 项目说明与本地环境配置
├── src/             # SystemVerilog RTL（阶段 0 创建）
├── test/            # Cocotb/Python 测试（阶段 0 创建）
├── Makefile         # 构建与仿真入口（阶段 0 创建）
└── .venv/           # 本地 Python 虚拟环境，不提交到 Git
```

## 下一步

按 [`CLAUDE.md`](CLAUDE.md) 的阶段 0 创建最小顶层模块、时钟/复位测试和 `Makefile`，使 `make test` 成为第一个可重复通过的检查。
