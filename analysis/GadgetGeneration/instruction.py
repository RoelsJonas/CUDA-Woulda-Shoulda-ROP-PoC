class Instruction:
    def __init__(self, address, opcode1, opcode2, decoded):
        self.address = address
        self.opcode1 = opcode1
        self.opcode2 = opcode2
        self.decoded = decoded

    def print(self):
        print("[" + hex(self.address) + "] 0x" + self.opcode1, "0x" + self.opcode2, self.decoded)

    def getOperands(self):
        startPoint = 1
        if("@P" in self.decoded):
            startPoint = 2
        return self.decoded.split(" ")[startPoint:]
