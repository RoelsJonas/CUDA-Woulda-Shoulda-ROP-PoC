class Gadget:
    def __init__(self, instructions = [], POPR20 = False, POPR21 = False, length = 0, startAddress = 0xffffffffffffffff, retReg = None):
        self.instructions = instructions
        self.POPR20 = POPR20
        self.POPR21 = POPR21
        self.startAddress = startAddress
        self.length = length
        self.retReg = retReg
        self.loadedRegs = []
        self.loadsRetReg = True
        self.genericStoresFromTo = {}
        self.genericLoadsToFrom = {}

    def addInstruction(self, instruction):
        self.instructions.append(instruction)
        if self.retReg == None and ("RET" in instruction.decoded or "JMX " in instruction.decoded or "BRX " in instruction.decoded) and "@P" not in instruction.decoded:
            # print(instruction.decoded)
            self.retReg = int(instruction.decoded.split(",")[0].split(" R")[-1].split(" ")[0], 10)
        
        elif(self.retReg == None and ("JMXU " in instruction.decoded or "BRXU " in instruction.decoded)):
            # print(instruction.decoded)
            self.retReg = int(instruction.decoded.split(" UR")[1].split(" ")[0].split(",")[0], 10)

        elif "LDL" in instruction.decoded:
            loadedReg = int(instruction.decoded.split(" R")[1].split(",")[0], 10)
            if(loadedReg not in self.loadedRegs):
                self.loadedRegs.append(loadedReg)
            if(".64" in instruction.decoded):
                self.loadedRegs.append(loadedReg + 1)
        
        elif ("R" + str(self.retReg)) in instruction.decoded:
            self.loadsRetReg = False

        self.length += 1
        
        if(self.startAddress > instruction.address):
            self.startAddress = instruction.address

    def isGadgetable(self):
        return (self.retReg in self.loadedRegs) and ((self.retReg + 1) in self.loadedRegs) and self.loadsRetReg
    
    def getVirtualAddress(self):
        addr = 0x7fffd8f63000
        addr = addr >> 21
        addr = addr << 21

        gadgetPhyAddr = self.startAddress
        gadgetPhyPageAddr = gadgetPhyAddr >> 21
        gadgetPhyPageAddr = gadgetPhyPageAddr << 21
        pageOffset = gadgetPhyAddr - gadgetPhyPageAddr
        gadgetVirtAddr = addr + pageOffset 
        return gadgetVirtAddr
    
    def getHash(self):
        string = ""
        i = 0
        for instruction in self.instructions:
            if(i == 0):
                i += 1
                continue
            string += instruction.decoded
        # print(string)
        return string
