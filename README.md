# 32bit-VirtualMachine
This project implements a simple CPU emulator in Python, with support for a 256KB(max possible 4 GB) memory and a set of registers. It includes basic arithmetic, logical, and memory operations, and it can execute instructions loaded into memory. 

## Overview

This project implements a simple CPU emulator in Python, with support for a 64KB memory and a set of registers. It includes basic arithmetic, logical, and memory operations, and it can execute instructions loaded into memory. 

### Features

1. **Registers**:
   - A set of 20 registers, including general-purpose registers (`R0-R15`), special registers (`PC`, `REM`, `COND`, `COMP`).
   - `PC` (Program Counter) tracks the next instruction to execute.
   - `COND` stores the condition flags (negative, zero, positive) after arithmetic operations.
   - `REM` stores the remainder from division operations.

2. **Memory**:
   - 256KB of memory (256 x 1024 bytes) (possible to change the amount).
   - Supports loading and storing data.

3. **Operations**:
   - Arithmetic: Addition, subtraction, multiplication, division.
   - Logical: AND, OR, XOR, NOT, SHL (shift left), SHR (shift right).
   - Comparison: Equal, not equal, greater than, less than.
   - Memory: Load, store, load indirect (LDI), store indirect (STI).
   - Control flow: Absolute jump (JMP_ABS), relative jump (JMP_REL).
   - Input/Output: Supports reading/writing via registers.
   - Trap routines for special operations, such as `GETC`, `OUT`, and `HALT`.

4. **Instruction Set**:
   - Uses a 32-bit instruction format with:
     - **5-bit opcode** for the operation type.
     - **5-bit register fields** for operands.
     - **16-bit immediate values** for constants or offsets.

---

## Usage

### Running the Emulator

To run the emulator, execute the following command:
```bash

