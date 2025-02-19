"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.reg = [0] * 8
        self.pc = 0 # program counter, address of the currently executing instruction
        self.sp = 7 # stack pointer location R7 
        self.fl = [0] * 8 # flags bits: 00000LGE
        self.branchtable = {
            1:   self.handle_HLT,
            130: self.handle_LDI,
            71:  self.handle_PRN,
            160: self.handle_ADD,
            162: self.handle_MUL,
            69:  self.handle_PUSH,
            70:  self.handle_POP,
            80:  self.handle_CALL,
            17:  self.handle_RET,
            167: self.handle_CMP,
            84:  self.handle_JMP,
            85:  self.handle_JEQ,
            86:  self.handle_JNE


        }

    def load(self, file):
        """Load a program into memory."""

        address = 0

        with open(file) as f:
            for line in f:
                comments = line.split("#")
                num = comments[0].strip()

                try: 
                    val = int(f'{num}',2)
                except ValueError:
                    continue

                self.ram[address] = val
                address += 1 

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        regValueA = self.reg[reg_a]
        regValueB = self.reg[reg_b]

        if op == "ADD":
            self.reg[reg_a] += regValueB
        elif op == "SUB": 
            self.reg[reg_a] -= regValueB
        elif op == "MUL":
            self.reg[reg_a] *= regValueB
        elif op == "DIV":
            self.reg[reg_a] /= regValueB
        elif op == "CMP":
            if regValueA == regValueB:
                self.fl[7] = 1
            elif regValueA < regValueB:
                self.fl[5] = 1
            elif regValueA > regValueB:
                self.fl[6] = 1
        else:
            raise Exception("Unsupported ALU operation")

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

    # halt
    def handle_HLT(self):
        self.pc +=1
        sys.exit(1)

    # load to register
    def handle_LDI(self):
        regAddress = self.ram_read(self.pc+1)
        integer = self.ram_read(self.pc+2)
        self.reg[regAddress] = integer
        self.pc +=3

    # print
    def handle_PRN(self):
        print(self.reg[self.ram_read(self.pc+1)])
        self.pc +=2

    def handle_ADD(self):
        regAddressA = self.ram_read(self.pc+1)
        regAddressB = self.ram_read(self.pc+2)
        self.alu('ADD', regAddressA, regAddressB)
        self.pc +=3

    def handle_MUL(self):
        regAddressA = self.ram_read(self.pc+1)
        regAddressB = self.ram_read(self.pc+2)
        self.alu('MUL', regAddressA, regAddressB)
        self.pc +=3

    # handles stack addition
    def handle_PUSH(self):
        regAddress = self.ram[self.pc + 1]
        value = self.reg[regAddress]
        self.reg[self.sp] -= 1 # decrement the pointer address
        self.ram[self.reg[self.sp]] = value
        self.pc += 2

    # handles stack removal
    def handle_POP(self):
        regAddress = self.ram[self.pc + 1]
        value = self.ram[self.reg[self.sp]]
        self.reg[regAddress] = value
        self.reg[self.sp] += 1
        self.pc += 2

    # handles functions calls
    def handle_CALL(self):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc+2
        regAddress = self.ram[self.pc+1]
        self.reg[6] = self.pc+2
        self.pc = self.reg[regAddress]

    # handles function returns
    def handle_RET(self):
        pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        self.pc = self.reg[6]

    # compares register values and adjusts flag respectivly
    def handle_CMP(self):
        regAddressA = self.ram[self.pc+1]
        regAddressB = self.ram[self.pc+2]
        self.alu("CMP", regAddressA, regAddressB)
        self.pc += 3

    # jump to the address stored in given register
    def handle_JMP(self):
        regAddress = self.ram[self.pc+1]
        self.pc = self.reg[regAddress]

    # if equal(E) flag is true(1), jump to address stored in given register 
    def handle_JEQ(self):
        if self.fl[7] == 1:
            regAddress = self.ram[self.pc+1]
            self.pc = self.reg[regAddress]
        else:
            self.pc += 2

    # if equal(E) flag is false(0), jump to address stored in given register
    def handle_JNE(self):
        if self.fl[7] == 0:
            regAddress = self.ram[self.pc+1]
            self.pc = self.reg[regAddress]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        while True:
            ir = self.ram_read(self.pc) # Instruction Register, currently executing instruction
            # print(f'ir: {ir}')
            self.branchtable[ir]()

    # accepts the address to read and return the value stored there.
    # MAR = Memory Address Register, address that is being read or written to
    def ram_read(self, MAR):
        return self.ram[MAR]

    # accepts a value to write, and the address to write it to.
    # MAR = Memory Address Register, address that is being read or written to
    # MDR = Memory Data Register, address that is being read or written to
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR