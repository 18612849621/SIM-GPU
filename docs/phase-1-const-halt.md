# 阶段 1.3：第一个程序执行闭环

现在硬件不再只是独立的 PC 和寄存器文件。`gpu_top` 可以从指令 ROM 取出一条指令、译码、写寄存器、推进 PC，并在 `HALT` 后停止。

本阶段只支持两条 16 位指令：

| 指令 | 编码 | 行为 |
| --- | --- | --- |
| `CONST rd, imm9` | `{4'h1, rd[2:0], imm9[8:0]}` | 将 9 位有符号立即数扩展为 32 位，写入 `r[rd]` |
| `HALT` | `16'hF000` | 停机，保持 PC 与寄存器 |

PC 以**指令编号**计数：`pc=0` 读取第 0 条 16 位指令，不是字节地址。

## 1. 固定测试程序

`test/programs/const_halt.hex` 是最小程序的机器码：

```text
14A5  # CONST r2, 165
1FFF  # CONST r7, -1
F000  # HALT
```

这是手写的十六进制机器码，不是汇编器。先稳定 ISA 和执行模型，之后才需要做汇编器。

## 2. 取指与执行

每条指令用两个上升沿：

1. `FETCH`：根据当前 PC 从组合读取的 ROM 取得指令，并锁存到 `instruction_reg`；PC 保持。
2. `EXECUTE`：执行已锁存的指令。`CONST` 写回寄存器并使 PC 加一；`HALT` 置 `halted=1` 并保持 PC。

```text
时间 →              t0              t1              t2              t3

clk = 1                         ┌────┐         ┌────┐         ┌────┐
clk = 0  ───────────────────────┘    └─────────┘    └─────────┘    └──
                                      ↑              ↑
state                 FETCH        EXECUTE         FETCH
pc                      0              1             1
instruction          14A5           14A5           1FFF
r2                      0           0x000000A5    0x000000A5
```

`t1` 前是 `FETCH`，上升沿后锁存 `14A5` 并进入 `EXECUTE`。`t2` 前是 `EXECUTE`，所以上升沿后寄存器文件把 `165` 写入 `r2`，PC 从 `0` 变为 `1`，控制器回到 `FETCH`。

## 3. 新组件与职责

```text
PC ──地址──► instruction_rom ──指令──► 控制器/指令寄存器
 ▲                                            │
 └──────────── 控制器决定是否推进 PC ──────────┤
                                              ▼
                                         regfile 写回
```

- `pc`：不再自动递增；只在 `pc_write_enable=1` 的上升沿加载 `pc_next`。
- `instruction_rom`：只读、组合输出当前 PC 对应的 16 位指令。
- `gpu_top`：保存控制状态 `FETCH`、`EXECUTE`、`HALTED`，并生成 PC 与寄存器文件的控制信号。
- `regfile`：仍只负责保存和读写数据；它不知道 `CONST` 或 `HALT` 的含义。

## 4. 停机与非法指令

执行 `HALT` 时，`halted` 变为 `1`，状态进入 `HALTED`。之后时钟继续跳变，但 PC 和寄存器均保持不变。

本阶段遇到未定义 opcode 也会停机，并置 `illegal_instruction=1`；不会悄悄继续执行未知指令。

## 5. 运行

```bash
source .venv/bin/activate
make test_const_halt
```

该测试逐拍验证：两次 `CONST` 的取指、写回与符号扩展，随后 `HALT` 后的 PC 和寄存器保持。

## 6. 下一步

闭环已经证明控制器能协调 PC、ROM 与寄存器文件。下一步先独立实现 32 位 `ADD` ALU 并测试它；之后扩展指令格式，执行 `CONST; CONST; ADD; HALT`。
