from GadgetGeneration.gadget import Gadget
from GadgetGeneration.instruction import Instruction

class BinaryAnalyzer:
    def __init__(self, fn: str):
        self.fileName = fn
        self.instructionSequence = []
        with open(self.fileName, "r") as f:
            self.objdump = f.read()

    def createInstructionSequence(self):
        lines = self.objdump.split("\n")
        decoded = ""
        opcode1 = ""
        opcode2 = ""
        for line in lines:
            if ";" in line:
                decoded = line.split(";")[0].split("*/")[1].strip()
                opcode1 = line.split(";")[1].split("*/")[0].split("/*")[1].strip()
            elif opcode1 != "":
                opcode2 = line.split("*/")[0].split("/*")[1].strip()
                self.instructionSequence.append(Instruction(0, opcode1, opcode2, decoded))
                decoded = ""
                opcode1 = ""
                opcode2 = ""
            
