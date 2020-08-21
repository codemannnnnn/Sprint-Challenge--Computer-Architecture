"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.flag = 0b00000000

    def load(self):
        """Load a program into memory."""

        address = 0
        file = sys.argv[1]

        with open(file) as f:
            for line in f:
                value = line.split("#")[0].strip()
                if value == '':
                    continue
                i = int(value, 2)
                self.ram_write(address, i)
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        LESS = 0b00000100
        GREATER = 0b00000010
        EQUAL = 0b00000001

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = EQUAL
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = LESS
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = GREATER
        else:
            raise Exception("ALU Operation not available.")



    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        LDI = 0b10000010
        PRN = 0b01000111
        ADD = 0b10100000
        MUL = 0b10100010
        CMP = 0b10100111
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        HLT = 0b00000001
        JEQ = 0b01010101
        JNE = 0b01010110
        JMP = 0b01010100

        rules = self.ram[self.pc]

        running = True

        while running:
            rules = self.ram[self.pc]
            op_one = self.ram_read(self.pc + 1)
            op_two = self.ram_read(self.pc + 2)

            if rules == HLT:
                running = False

            elif rules == LDI:
                self.reg[op_one] = op_two
                self.pc += 3

            elif rules == PRN:
                print(self.reg[op_one])
                self.pc += 2

            elif rules == ADD:
                reg_a = self.ram[self.pc+1]
                reg_b = self.ram[self.pc+2]
                self.alu("ADD", reg_a, reg_b)
                self.pc += 3

            elif rules == MUL:
                reg_a = self.ram[self.pc+1]
                reg_b = self.ram[self.pc+2]
                self.alu("MUL", reg_a, reg_b)
                self.pc += 3

            elif rules == PUSH:
                self.reg[self.sp] -= 1
                reg_num = op_one
                value = self.reg[reg_num]
                top_stack = self.reg[self.sp]
                self.ram[top_stack] = value
                self.pc += 2

            elif rules == POP:
                top_stack = self.reg[self.sp]
                value = self.ram[top_stack]
                reg_num = op_one
                self.reg[reg_num] = value

                self.reg[self.sp] += 1
                self.pc += 2

            elif rules == CALL:
                return_addr = self.pc + 2
                self.reg[self.sp] -= 1
                top_stack = self.reg[self.sp]
                self.ram[top_stack] = return_addr
                reg_num = op_one
                subroutine_addr = self.reg[reg_num]
                self.pc = subroutine_addr

            elif rules == RET:
                top_stack = self.reg[self.sp]
                return_addr = self.ram[top_stack]
                self.reg[self.sp] += 1
                self.pc = return_addr

            elif rules == CMP:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu("CMP", reg_a, reg_b)
                self.pc += 3

            elif rules == JMP:
                self.pc = self.reg[op_one]

            elif rules == JEQ:
                if self.flag == HLT:
                    self.pc = self.reg[op_one]
                else:
                    self.pc += 2

            elif rules == JNE:
                if self.flag != HLT:
                    self.pc = self.reg[op_one]
                else:
                    self.pc += 2

            else:
                print(f"I don't know what that means.")
                sys.exit(1)


    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
