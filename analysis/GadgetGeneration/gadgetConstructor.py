from GadgetGeneration.gadget import Gadget
from GadgetGeneration.instruction import Instruction

class GadgetConstructor:
    def __init__(self, instructions):
        self.instructions = instructions
        self.ROPGadgets = []
        self.subGadgetableRegs = []
        self.subROPGadgets = []
        self.JOPGadgets = []
        self.subJOPGadgets = []
        self.COPGadgets = []
        self.subCOPGadgets = []
        self.nonGadgetableInstructions = [
                                    "PADDING",
                                    "CALL", 
                                    "BRA", 
                                    "EXIT",
                                    "RET",
                                    "JMX",
                                    "BRX"
                                   ]

    def analyze(self):
        self.generateROPGadgets()
        self.eliminateSubROPGadgets()
        self.generateJOPGadgets()
        self.printStats()
        self.inspectGadgets()

    def printStats(self):
        print("Number of traditional ROP gadgets:", len(self.ROPGadgets))
        self.printGadgets(self.ROPGadgets)
        print("Number of sub ROP gadgets:", len(self.subROPGadgets))
        self.printGadgets(self.subROPGadgets)      
        print("Number of JOP gadgets:", len(self.JOPGadgets))
        self.printGadgets(self.JOPGadgets)
        print("Number of sub JOP gadgets:", len(self.subJOPGadgets))
        self.printGadgets(self.subJOPGadgets)
        print("Number of COP gadgets:", len(self.COPGadgets))
        # # self.printGadgets(self.COPGadgets)
        # print("Number of sub COP gadgets:", len(self.subCOPGadgets))
        # # self.printGadgets(self.subCOPGadgets)

        print("Number of traditional ROP gadgets:", len(self.ROPGadgets))
        print("Number of sub ROP gadgets:", len(self.subROPGadgets))   
        print("Number of JOP gadgets:", len(self.JOPGadgets))
        print("Number of sub JOP gadgets:", len(self.subJOPGadgets))
        print("Number of COP gadgets:", len(self.COPGadgets))
        
    def generateROPGadgets(self):
        invalidations = {}

        gadget = Gadget([])
        for i in reversed(range(0, len(self.instructions))):
            # if the gadget
            if(len(gadget.instructions) == 0): 
                if("RET" in self.instructions[i].decoded and "@P" not in self.instructions[i].decoded):
                    gadget.addInstruction(self.instructions[i])
                continue

            # check if instruction is non gadgetable
            for ngi in self.nonGadgetableInstructions:
                if(ngi in self.instructions[i].decoded):
                    if ngi not in invalidations:
                        invalidations[ngi] = 0
                    invalidations[ngi] += 1

                    # check if gadget is valid
                    if(gadget.isGadgetable()):
                        gadget.addInstruction(self.instructions[i])
                        instructionsRev = []
                        for j in reversed(range(0, len(gadget.instructions))):
                            instructionsRev.append(gadget.instructions[j])                        
                        self.ROPGadgets.append(Gadget(instructionsRev, gadget.POPR20, gadget.POPR21, gadget.length, gadget.startAddress + 0x10, gadget.retReg))

                    elif(len(gadget.instructions) > 1):
                        gadget.addInstruction(self.instructions[i])
                        instructionsRev = []
                        for j in reversed(range(0, len(gadget.instructions))):
                            instructionsRev.append(gadget.instructions[j])                        
                        self.subROPGadgets.append(Gadget(instructionsRev, gadget.POPR20, gadget.POPR21, gadget.length, gadget.startAddress + 0x10, gadget.retReg))

                    # add new loaded regs to subGadgetableRegs
                    for reg in gadget.loadedRegs:
                        if (reg not in self.subGadgetableRegs) and (reg != gadget.retReg) and (reg != (gadget.retReg + 1)):
                            self.subGadgetableRegs.append(reg)

                    gadget = Gadget([])
                    break

            if(len(gadget.instructions) != 0):
                gadget.addInstruction(self.instructions[i])

        for key in invalidations:
            print(key, invalidations[key])
        
    def eliminateSubROPGadgets(self):
        # eliminate all subgadgets that are not in subgadgetableRegs
        for sg in range(len(self.subROPGadgets)):
            if(self.subROPGadgets[sg].retReg in self.subGadgetableRegs and (self.subROPGadgets[sg].retReg + 1) in self.subGadgetableRegs):
                continue
            else:
                self.subROPGadgets[sg] = None
        
        # remove all nones from subGadgets
        self.subROPGadgets = [x for x in self.subROPGadgets if x is not None]

    
    def generateJOPGadgets(self):
        invalidations = {}

        gadget = Gadget([])
        for i in reversed(range(0, len(self.instructions))):
            # if the gadget
            if(len(gadget.instructions) == 0): 
                if("JMX" in self.instructions[i].decoded or "BRX" in self.instructions[i].decoded) and "@P" not in self.instructions[i].decoded:
                    gadget.addInstruction(self.instructions[i])
                continue

            # check if instruction is non gadgetable
            if("@P" not in self.instructions[i].decoded):
                for ngi in self.nonGadgetableInstructions:
                    if(ngi in self.instructions[i].decoded or ("LDC R" + str(gadget.retReg) in self.instructions[i].decoded)):
                        if ngi not in invalidations:
                            invalidations[ngi] = 0
                        invalidations[ngi] += 1
        
                    if(ngi in self.instructions[i].decoded or ("LDC R" + str(gadget.retReg) in self.instructions[i].decoded)):
                        # check if gadget is valid
                        if(gadget.isGadgetable()):
                            gadget.addInstruction(self.instructions[i])
                            instructionsRev = []
                            for j in reversed(range(0, len(gadget.instructions))):
                                instructionsRev.append(gadget.instructions[j])                        
                            self.JOPGadgets.append(Gadget(instructionsRev, gadget.POPR20, gadget.POPR21, gadget.length, gadget.startAddress + 0x10, gadget.retReg))

                            # add new loaded regs to subGadgetableRegs
                            for reg in gadget.loadedRegs:
                                if (reg not in self.subGadgetableRegs) and (reg != gadget.retReg) and (reg != (gadget.retReg + 1)):
                                    self.subGadgetableRegs.append(reg)

                        elif(len(gadget.instructions) > 1):
                            gadget.addInstruction(self.instructions[i])
                            instructionsRev = []
                            for j in reversed(range(0, len(gadget.instructions))):
                                instructionsRev.append(gadget.instructions[j])                        
                            self.subJOPGadgets.append(Gadget(instructionsRev, gadget.POPR20, gadget.POPR21, gadget.length, gadget.startAddress + 0x10, gadget.retReg))

                        gadget = Gadget([])
                        break

            if(len(gadget.instructions) != 0):
                gadget.addInstruction(self.instructions[i])

        for key in invalidations:
            print(key, invalidations[key])

    def inspectGadgets(self):
        for gadget in self.ROPGadgets:
            for instruction in gadget.instructions:
                if("LD." in instruction.decoded or "LD " in instruction.decoded):
                    operands = instruction.getOperands()
                    destReg = "NONE"
                    addressReg = "NONE"
                    if(len(operands) > 0):
                        destReg = operands[0]
                    if(len(operands) > 1):
                        addressReg = operands[1]
                    # print(instruction.decoded, "Dest:", destReg, "Address:", addressReg)
                    # print("")

    def printGadgets(self, gadgets):
        gadgets.sort(key=lambda x: x.length, reverse=False)
        for gadget in gadgets:
            print("Virtual address: ", hex(gadget.getVirtualAddress()), "Length: ", gadget.length)
            for instruction in gadget.instructions:
                instruction.print()
            print("")


