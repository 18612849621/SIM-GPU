# 阶段 0：最小 RTL、时钟与复位

本阶段尚未实现真正的 GPU。目标是建立一个可重复验证的硬件开发闭环：使用 SystemVerilog 描述一个最小硬件模块，以 Cocotb/Python 驱动它，并通过 `make test` 自动验证行为。

## 文件关系

```text
src/gpu_top.sv       SystemVerilog 硬件描述
        │
        ▼
Icarus Verilog       编译并模拟硬件
        │
        ▼
test/test_reset.py   Cocotb/Python 驱动输入并检查输出
        │
        ▼
Makefile             将上述流程统一为 make test
```

## 1. RTL 与 module

RTL（Register Transfer Level，寄存器传输级）用代码描述硬件电路，而不是从上到下执行的普通程序。

`src/gpu_top.sv` 中的 `gpu_top` 是当前最外层的硬件盒子：

```text
        ┌───────────────────────────────┐
clk ───►│                               │
rst ───►│            gpu_top            │───► initialized
        │                               │
        └───────────────────────────────┘
```

端口含义：

| 端口 | 方向 | 含义 |
| --- | --- | --- |
| `clk` | 输入 | 时钟；决定寄存器何时更新 |
| `rst` | 输入 | 复位；要求寄存器恢复初始状态 |
| `initialized` | 输出 | 当前唯一的可观测寄存器状态 |

以后完整 GPU 也会是一个 `module`，只会增加更多端口与内部模块，例如指令存储器、数据存储器、启动信号和完成信号。

## 2. 时钟与上升沿

硬件中的寄存器通常只在统一的节奏下更新，这个节奏是时钟：

```text
clk:  ──┐    ┌────┐    ┌────┐
        │    │    │    │    │
     ───┘    └────┘    └────┘
         ↑       ↑       ↑
       上升沿    上升沿    上升沿
```

从 `0` 变为 `1` 的瞬间叫上升沿（rising edge）。本项目的状态只在上升沿改变。

因此，两个上升沿之间即使输入信号变化，寄存器也会保持原值；它会在下一个上升沿统一读取输入并更新。

## 3. 寄存器与状态

当前的 `initialized` 是一个 1 bit 寄存器，只能保存：

```text
0：正在复位，或尚未完成初始化
1：复位已释放，初始化完成
```

寄存器会记住上一个时钟周期的值。未来 GPU 中的 PC、通用寄存器、线程是否活跃、GPU 是否完成等，都会是同类的时序状态。

## 4. always_ff 与同步复位

当前核心 RTL：

```systemverilog
always_ff @(posedge clk) begin
    if (rst) begin
        initialized <= 1'b0;
    end else begin
        initialized <= 1'b1;
    end
end
```

逐项解释：

- `always_ff`：这是时序寄存器逻辑。
- `@(posedge clk)`：只在时钟上升沿执行。
- `if (rst)`：在上升沿检查复位输入。
- `<=`：非阻塞赋值，用于在时钟周期结束时更新寄存器。

状态转换如下：

| 上升沿到来时 `rst` | 上升沿后 `initialized` |
| ---: | ---: |
| `1` | `0` |
| `0` | `1` |

这是**同步复位**：`rst` 改变不会立刻改变 `initialized`，必须等到下一个时钟上升沿。

与之相对的异步复位会写成：

```systemverilog
always_ff @(posedge clk or posedge rst)
```

异步复位在 `rst` 拉高时立即清零，不需要等待时钟。阶段 0 选择同步复位，因为它更容易理解和验证。

## 5. 为什么使用非阻塞赋值 `<=`

同一个上升沿上，多个寄存器应当并行更新。非阻塞赋值表示：

```text
先计算每个寄存器的新值
        ↓
当前时钟步骤结束时，所有寄存器一起更新
```

之后实现 PC、寄存器文件和控制状态机时，也应使用这种方式：

```systemverilog
pc <= pc + 1;
registers[rd] <= alu_result;
```

## 6. Cocotb 测试

`test/test_reset.py` 不是 GPU 本身，而是测试程序。它会：

1. 启动时钟；
2. 设置 `rst` 输入；
3. 等待时钟边沿；
4. 读取 `initialized` 输出；
5. 用断言确认结果。

时钟由下面代码创建：

```python
cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
```

它产生一个周期为 10 ns 的 `clk` 信号。

测试步骤：

```text
拉高 rst
  ↓
等待两个时钟上升沿
  ↓
确认 initialized == 0
  ↓
在下降沿释放 rst
  ↓
等待下一个上升沿
  ↓
确认 initialized == 1
  ↓
在下降沿再次拉高 rst
  ↓
等待下一个上升沿
  ↓
确认 initialized == 0
```

## 7. RisingEdge、FallingEdge 与 ReadOnly

Cocotb 中：

- `RisingEdge(dut.clk)`：等待时钟从 `0` 变为 `1`。
- `FallingEdge(dut.clk)`：等待时钟从 `1` 变为 `0`。
- `ReadOnly()`：等待当前时刻的 RTL 更新完成，再安全读取信号。

在上升沿附近，仿真顺序大致是：

```text
1. clk 从 0 变为 1
2. Cocotb 捕获 RisingEdge
3. RTL 的 always_ff 执行
4. <= 的非阻塞赋值提交新值
5. ReadOnly 阶段：读取稳定结果
```

因此，测试需要：

```python
await RisingEdge(dut.clk)
await ReadOnly()
assert dut.initialized.value == 1
```

如果在 `RisingEdge` 后立刻断言，可能会读到寄存器更新前的旧值。

测试选择在下降沿修改 `rst`：

```python
await FallingEdge(dut.clk)
dut.rst.value = 0
```

这样能保证 `rst` 在下一个上升沿前已经稳定，不会产生“这个上升沿到底读到旧输入还是新输入”的时序歧义。

## 8. Makefile 与 make test

`Makefile` 将仿真流程封装成一个命令：

```bash
source .venv/bin/activate
make test
```

执行链路：

```text
make test
   ↓
Icarus Verilog 编译 src/gpu_top.sv
   ↓
生成并运行硬件仿真
   ↓
Cocotb 加载 test/test_reset.py
   ↓
Python 驱动 clk 和 rst
   ↓
检查 initialized
   ↓
通过或失败
```

关键变量：

| Makefile 变量 | 含义 |
| --- | --- |
| `SIM` | 指定 Icarus Verilog 仿真器 |
| `TOPLEVEL` | 指定顶层硬件模块 `gpu_top` |
| `VERILOG_SOURCES` | 指定 RTL 源文件 |
| `COCOTB_TEST_MODULES` | 指定 Python 测试模块 |
| `PYTHONPATH` | 让 Python 能找到 `test/test_reset.py` |

## 9. 本阶段最重要的因果链

```text
Python 设置 rst
    ↓
等待时钟上升沿
    ↓
always_ff 根据 rst 更新寄存器
    ↓
等待非阻塞赋值完成
    ↓
Python 读取 initialized 并断言
```

掌握这条链路后，下一阶段只是在同一条链路中加入新的寄存器和计算逻辑：PC、通用寄存器、ALU 和指令译码。

## 阶段 0 完成

阶段 0 的时钟、同步复位、Cocotb 驱动和 `make test` 工作流已经完成。下一阶段从独立的 32 位 PC 模块开始，详见 [阶段 1.1：Program Counter](phase-1-pc.md)。
