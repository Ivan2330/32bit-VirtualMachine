from enum import Enum


MEMORY_SIZE = 256 * 1024  
memory = bytearray(MEMORY_SIZE)

# Розподіл регістрів
class Registers(Enum):
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    R8 = 8
    R9 = 9
    R10 = 10
    R11 = 11
    R12 = 12
    R13 = 13
    R14 = 14
    R15 = 15
    PC = 16      # Програмний лічильник
    REM = 17     # Регістр залишку для ділення
    COND = 18    # Прапорець для умов
    COMP = 19    # Прапор порівняння

registers = [0] * len(Registers)  


class OpCodes(Enum):
    ADD = 0x01
    SUB = 0x02 
    MUL = 0x03
    DIV = 0x04
    AND = 0x05
    OR = 0x06
    XOR = 0x07
    NOT = 0x08
    SHL = 0x09
    SHR = 0x0A
    CMP_EQ = 0x0B
    CMP_NEQ = 0x0C
    CMP_GT = 0x0D
    CMP_LT = 0x0E
    LOAD = 0x0F
    STORE = 0x10
    LDI = 0x11
    STI = 0x12
    LEA = 0x13
    JMP_ABS = 0x14
    JMP_REL = 0x15
    INPUT = 0x16
    OUTPUT = 0x17
    TRAP = 0x18
    HALT = 0x1F


def load_memory(address, size=4):
    return int.from_bytes(memory[address:address + size], byteorder='little')

def store_memory(address, value, size=4):
    memory[address:address + size] = value.to_bytes(size, byteorder='little')


def update_flags(reg):
    if registers[reg] == 0:
        registers[Registers.COND.value] = 0b010  
    elif registers[reg] > 0:
        registers[Registers.COND.value] = 0b001  # Positive 
    else:
        registers[Registers.COND.value] = 0b100  # Negative

def ldi(dest, offset):
    address = registers[Registers.PC.value] + offset
    registers[dest] = load_memory(load_memory(address))
    update_flags(dest)

def sti(src, offset):
    address = registers[Registers.PC.value] + offset
    store_memory(load_memory(address), registers[src])

def lea(dest, offset):
    registers[dest] = registers[Registers.PC.value] + offset
    update_flags(dest)
    

def add_reg(dest, src1, src2=None, immediate=None):
    registers[dest] = registers[src1] + (immediate if immediate is not None else registers[src2])
    update_flags(dest)

def sub_reg(dest, src1, src2=None, immediate=None):
    registers[dest] = registers[src1] - (immediate if immediate is not None else registers[src2])
    update_flags(dest)

def mul_reg(dest, src1, src2=None, immediate=None):
    registers[dest] = registers[src1] * (immediate if immediate is not None else registers[src2])
    update_flags(dest)

def div_reg(dest, src1, src2=None, immediate=None):
    divisor = immediate if immediate is not None else registers[src2]
    if divisor != 0:
        registers[dest] = registers[src1] // divisor
        registers[Registers.REM.value] = registers[src1] % divisor
        update_flags(dest)
    else:
        print("Division by zero")
        halt()


def and_op(dest, src1, src2=None, immediate=None):
    registers[dest] = registers[src1] & (immediate if immediate is not None else registers[src2])
    update_flags(dest)

def or_op(dest, src1, src2=None, immediate=None):
    registers[dest] = registers[src1] | (immediate if immediate is not None else registers[src2])
    update_flags(dest)

def xor_op(dest, src1, src2=None, immediate=None):
    registers[dest] = registers[src1] ^ (immediate if immediate is not None else registers[src2])
    update_flags(dest)

def not_op(dest, src):
    registers[dest] = ~registers[src]
    update_flags(dest)

def shl(dest, src, amount):
    registers[dest] = registers[src] << amount
    update_flags(dest)

def shr(dest, src, amount):
    registers[dest] = registers[src] >> amount
    update_flags(dest)

# Операції порівняння
def cmp_eq(reg1, reg2):
    registers[Registers.COND.value] = int(registers[reg1] == registers[reg2])

def cmp_neq(reg1, reg2):
    registers[Registers.COND.value] = int(registers[reg1] != registers[reg2])

def cmp_gt(reg1, reg2):
    registers[Registers.COND.value] = int(registers[reg1] > registers[reg2])

def cmp_lt(reg1, reg2):
    registers[Registers.COND.value] = int(registers[reg1] < registers[reg2])


def jump_absolute(address):
    registers[Registers.PC.value] = address

def jump_relative(offset):
    registers[Registers.PC.value] += offset


def do_input(reg):
    value = int(input("Enter a value: "))
    registers[reg] = value
    update_flags(reg)

def do_output(reg):
    print(f"Output from R{reg}: {registers[reg]}")


def trap_getc():
    registers[Registers.R0.value] = ord(input("Enter a character: ")[0])

def trap_out():
    print(chr(registers[Registers.R0.value] & 0xFF), end='')

def trap_halt():
    global running
    running = False
    print("Program halted.")

trap_table = {
    0x20: trap_getc,
    0x21: trap_out,
    0x25: trap_halt,
}

def trap(instruction):
    trap_vector = instruction & 0xFF
    if trap_vector in trap_table:
        trap_table[trap_vector]()
    else:
        print(f"Unknown TRAP vector: {trap_vector}")


def halt():
    global running
    running = False


def execute_instruction(instruction):
    global running
    opcode = (instruction >> 27) & 0x1F  # 5-бітний опкод
    reg1 = (instruction >> 22) & 0x1F    # 5 біт для першого регістра
    reg2 = (instruction >> 17) & 0x1F    # 5 біт для другого регістра
    immediate = instruction & 0xFFFF     # 16-бітний безпосередній операнд

    if opcode == OpCodes.ADD.value:
        add_reg(reg1, reg2, immediate=immediate)
    elif opcode == OpCodes.SUB.value:
        sub_reg(reg1, reg2, immediate=immediate)
    elif opcode == OpCodes.MUL.value:
        mul_reg(reg1, reg2, immediate=immediate)
    elif opcode == OpCodes.DIV.value:
        div_reg(reg1, reg2, immediate=immediate)
    elif opcode == OpCodes.AND.value:
        and_op(reg1, reg2, immediate=immediate)
    elif opcode == OpCodes.OR.value:
        or_op(reg1, reg2, immediate=immediate)
    elif opcode == OpCodes.XOR.value:
        xor_op(reg1, reg2, immediate=immediate)
    elif opcode == OpCodes.NOT.value:
        not_op(reg1, reg2)
    elif opcode == OpCodes.SHL.value:
        shl(reg1, reg2, immediate)
    elif opcode == OpCodes.SHR.value:
        shr(reg1, reg2, immediate)
    elif opcode == OpCodes.CMP_EQ.value:
        cmp_eq(reg1, reg2)
    elif opcode == OpCodes.CMP_NEQ.value:
        cmp_neq(reg1, reg2)
    elif opcode == OpCodes.CMP_GT.value:
        cmp_gt(reg1, reg2)
    elif opcode == OpCodes.CMP_LT.value:
        cmp_lt(reg1, reg2)
    elif opcode == OpCodes.LOAD.value:
        registers[reg1] = immediate
        update_flags(reg1)
    elif opcode == OpCodes.STORE.value:
        store_memory(immediate, registers[reg1])
    elif opcode == OpCodes.LDI.value:
        ldi(reg1, immediate)
    elif opcode == OpCodes.STI.value:
        sti(reg1, immediate)
    elif opcode == OpCodes.LEA.value:
        lea(reg1, immediate)
    elif opcode == OpCodes.JMP_ABS.value:
        jump_absolute(immediate)
    elif opcode == OpCodes.JMP_REL.value:
        jump_relative(immediate)
    elif opcode == OpCodes.INPUT.value:
        do_input(reg1)
    elif opcode == OpCodes.OUTPUT.value:
        do_output(reg1)
    elif opcode == OpCodes.TRAP.value:
        trap(instruction)
    elif opcode == OpCodes.HALT.value:
        halt()
    else:
        print(f"Unknown opcode: {opcode}")
        halt()



def load_and_execute_instructions():
    instructions = [
        (OpCodes.LOAD.value << 27) | (Registers.R1.value << 22) | 0x02,   # LOAD R1, #2
        (OpCodes.ADD.value << 27) | (Registers.R0.value << 22) | (Registers.R1.value << 17) | 0x05,  # ADD R0, R1, #5
        (OpCodes.SUB.value << 27) | (Registers.R1.value << 22) | (Registers.R0.value << 17) | 0x03,  # SUB R1, R0, #3
        (OpCodes.MUL.value << 27) | (Registers.R2.value << 22) | (Registers.R1.value << 17) | 0x02,  # MUL R2, R1, #2
        (OpCodes.DIV.value << 27) | (Registers.R3.value << 22) | (Registers.R2.value << 17) | 0x01,  # DIV R3, R2, #1
        (OpCodes.AND.value << 27) | (Registers.R4.value << 22) | (Registers.R2.value << 17) | 0x01,  # AND R4, R2, #1
        (OpCodes.OR.value << 27) | (Registers.R5.value << 22) | (Registers.R4.value << 17) | 0x01,   # OR R5, R4, #1
        (OpCodes.XOR.value << 27) | (Registers.R6.value << 22) | (Registers.R5.value << 17) | 0x01,  # XOR R6, R5, #1
        (OpCodes.NOT.value << 27) | (Registers.R7.value << 22) | (Registers.R6.value << 17),         # NOT R7, R6
        (OpCodes.SHL.value << 27) | (Registers.R8.value << 22) | (Registers.R1.value << 17) | 0x01,  # SHL R8, R1, #1
        (OpCodes.SHR.value << 27) | (Registers.R9.value << 22) | (Registers.R8.value << 17) | 0x01,  # SHR R9, R8, #1
        (OpCodes.HALT.value << 27)                                                                  # HALT
    ]
    for i, instr in enumerate(instructions):
        store_memory(i * 4, instr)

    global running
    running = True
    registers[Registers.PC.value] = 0
    while running:
        pc = registers[Registers.PC.value]
        if pc >= MEMORY_SIZE:
            print("PC out of bounds")
            break
        instruction = load_memory(pc)
        registers[Registers.PC.value] += 4
        execute_instruction(instruction)
    print_registers()


def print_registers():
    print("Registers state:")
    for reg in Registers:
        print(f"{reg.name}: {registers[reg.value]}")


if __name__ == "__main__":
    load_and_execute_instructions()


