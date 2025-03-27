from GadgetGeneration.gadget import Gadget
from GadgetGeneration.instruction import Instruction


class rawDumpAnalyzer:
    def __init__(self, fn: str, startByte: int, endByte: int):
        self.fileName = fn
        self.startByte = startByte
        self.endByte = endByte
        self.instructionSequence = []
        self.index = 0
        self.lineSize = 8

    def analyze(self):
        self.readFile()
        self.createInstructions()
        self.decodeInstructions()


    def readFile(self):
        self.file = open(self.fileName, "rb")
        self.binary = self.file.read()
        print("Read " + str(len(self.binary)) + " bytes from " + self.fileName)

    def createInstructions(self):
        inst = Instruction(0, "", "", "")
        for i in range(self.startByte, self.endByte):
            if(i % self.lineSize == 0):
                line = ""
                for j in range(0, self.lineSize):
                    val = str(hex(self.binary[i+self.lineSize-1-j]).removeprefix("0x"))
                    if len(val) == 1:
                        val = "0" + val
                    line += val
                if((i//self.lineSize)%2==0):
                    inst.opcode1 = line
                else:  
                    inst.opcode2 = line

            if(inst.opcode1 != "" and inst.opcode2 != ""):
                self.instructionSequence.append(Instruction(i - 8, inst.opcode1, inst.opcode2, ""))
                inst = Instruction(i, "", "", "")
                self.index += 1
        print("Number of instructions: ", self.index)
    
    def decodeInstructions(self):
        for i in range(0, self.index):
            # Check if the instruction isn't padding
            if(self.instructionSequence[i].opcode1 == "0000000000000000" and self.instructionSequence[i].opcode2 == "0000000000000000"):
                self.instructionSequence[i].decoded = "PADDING"
                continue

            if(self.instructionSequence[i].opcode1[13:] == "918"):
                self.instructionSequence[i].decoded += "NOP"

            # Assign opcode and operands
            if(self.instructionSequence[i].opcode1[13:] == "943"):
                address = "0x" + self.instructionSequence[i].opcode2[12:] + self.instructionSequence[i].opcode1[0:8]
                self.instructionSequence[i].decoded += "CALL.ABS.NOINC " + address

            if(self.instructionSequence[i].opcode1[13:] == "947"):
                address = "0x" + self.instructionSequence[i].opcode1[0:8]
                self.instructionSequence[i].decoded += "BRA " + address

            if(self.instructionSequence[i].opcode1[13:] == "948"):
                address = "0x" + self.instructionSequence[i].opcode1[0:8]
                self.instructionSequence[i].decoded += "WARPSYNC " + address

            if(self.instructionSequence[i].opcode1[13:] == "949"):
                address = "0x" + self.instructionSequence[i].opcode1[0:8]
                regNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                self.instructionSequence[i].decoded += "BRX R" + str(regNr) + ", " + address

            if(self.instructionSequence[i].opcode1[13:] == "958"):
                address = "0x" + self.instructionSequence[i].opcode1[0:8]
                regNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                self.instructionSequence[i].decoded += "BRXU UR" + str(regNr) + ", " + address

            if(self.instructionSequence[i].opcode1[13:] == "94c"):
                self.instructionSequence[i].decoded += "JMX TODO FURTHER DECODING"
                
            if(self.instructionSequence[i].opcode1[13:] == "950"):
                regNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                self.instructionSequence[i].decoded += "RET.ABS.NODEC R" + str(regNr) + " 0x0"
            
            if(self.instructionSequence[i].opcode1[13:] == "983"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = int(self.instructionSequence[i].opcode1[0:6], 16)
                modifier = int(self.instructionSequence[i].opcode2[12:14], 16)
                if(modifier == 0x8):
                    modifier = ""
                elif(modifier == 0xa):
                    modifier = ".64"
                elif(modifier == 0xc):
                    modifier = ".128"
                elif(modifier == 0x6):
                    modifier = ".S16"
                else:
                    modifier = ".UNKNOWNMODIFIER"

                secondaryModifier = int(self.instructionSequence[i].opcode2[10:12], 16)
                if(secondaryModifier == 0x10):
                    secondaryModifier = ""
                elif(secondaryModifier == 0x30):
                    secondaryModifier = ".LU"
                else:
                    secondaryModifier = ".UNKNOWNMODIFIER"
                self.instructionSequence[i].decoded += "LDL" + secondaryModifier + modifier + " R" + str(destRegNr) + ", [R" + str(sourceRegNr) + "+" + hex(offset) + "]"

            if(self.instructionSequence[i].opcode1[13:] == "202"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 6)
                offset = int(self.instructionSequence[i].opcode1[0:6], 16)
                self.instructionSequence[i].decoded += "MOV R" + str(destRegNr) + ", R" + str(sourceRegNr)

            if(self.instructionSequence[i].opcode1[13:] == "802"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                value = int(self.instructionSequence[i].opcode1[0:8], 16)
                self.instructionSequence[i].decoded += "MOV R" + str(destRegNr) + ", " + hex(value)

            if(self.instructionSequence[i].opcode1[13:] == "816"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = int(self.instructionSequence[i].opcode1[0:8], 16)
                thirdInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                self.instructionSequence[i].decoded += "PRMT R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", " + hex(offset) +  ", R" + str(thirdInput)
            
            if(self.instructionSequence[i].opcode1[13:] == "387"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 6)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = int(self.instructionSequence[i].opcode1[0:6], 16)
                modifier = int(self.instructionSequence[i].opcode2[12:14], 16)
                if(modifier == 0x8):
                    modifier = ""
                elif(modifier == 0xa):
                    modifier = ".64"
                elif(modifier == 0xc):
                    modifier = ".128"
                elif(modifier == 0x6):
                    modifier = ".S16"
                else:
                    modifier = ".UNKNOWNMODIFIER"
                
                secondaryModifier = int(self.instructionSequence[i].opcode2[10:12], 16)
                if(secondaryModifier == 0x10):
                    secondaryModifier = ""
                elif(secondaryModifier == 0x30):
                    secondaryModifier = ".LU"
                else:
                    secondaryModifier = ".UNKNOWNMODIFIER"
                self.instructionSequence[i].decoded += "STL" + secondaryModifier + modifier + " [R" + str(sourceRegNr) + "+" + hex(offset) + "], R" + str(destRegNr)

            if(self.instructionSequence[i].opcode1[13:] == "385"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode2, 14)
                offset = self.instructionSequence[i].opcode1[0:8]
                modifier = int(self.instructionSequence[i].opcode2[10:14], 16)
                modifiers = {
                    0x10e9: ".E.SYS",
                    0x1149: ".E.STRONG.GPU",
                    0x114d: ".E.128.STRONG.GPU",
                    0x1145: ".E.U16.STRONG.GPU",
                    0x114b: ".E.64.STRONG.GPU",
                    0x10eb: "UNKNOWNPART.64",
                }
                if modifier in modifiers:
                    modifier = modifiers[modifier]
                else:
                    modifier = ".UNKNOWNMODIFIER"
                self.instructionSequence[i].decoded += "ST" + modifier + " [R" + str(destRegNr) + "+" + offset + "]" + ", R" + str(sourceRegNr) 

            if(self.instructionSequence[i].opcode1[13:] == "980"):
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                offset = int(self.instructionSequence[i].opcode1[0:8], 16)
                modifier = int(self.instructionSequence[i].opcode2[10:14], 16)
                modifiers = {
                    0x10e9: ".E.SYS",
                    0x1149: ".E.STRONG.GPU",
                    0x114d: ".E.128.STRONG.GPU",
                    0x1145: ".E.U16.STRONG.GPU",
                    0x114b: ".E.64.STRONG.GPU",
                    0x10eb: "UNKNOWNPART.64",
                }
                if modifier in modifiers:
                    modifier = modifiers[modifier]
                else:
                    modifier = ".UNKNOWNMODIFIER"
                self.instructionSequence[i].decoded += "LD" + modifier + " R" + str(destRegNr) + ", [R" + str(sourceRegNr) + "+" + hex(offset) + "]"

            if(self.instructionSequence[i].opcode1[13:] == "210"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                thirdInput = decodeReg(self.instructionSequence[i].opcode1, 6)
                fourthInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                negation = int(self.instructionSequence[i].opcode2[13], 16)
                if negation == 1:
                    negation = "-R"
                else:
                    negation = "P"
                self.instructionSequence[i].decoded += "IADD R" + str(destRegNr) + ", " + negation + str(sourceRegNr) + ", R" + str(thirdInput) + ", R" + str(fourthInput) + ", !PT"

            if(self.instructionSequence[i].opcode1[13:] == "810"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = int(self.instructionSequence[i].opcode1[0:8], 16)
                thirdInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                self.instructionSequence[i].decoded += "IADD R" + str(destRegNr) +", R" + str(sourceRegNr) + ", " + hex(offset) + ", R" + str(thirdInput) 

            if(self.instructionSequence[i].opcode1[13:] == "424"):
                imediate = int(self.instructionSequence[i].opcode1[0:8], 16)
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                thirdInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                self.instructionSequence[i].decoded += "IMAD.MOV.U32 R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", R" + str(thirdInput) + ", " + hex(imediate)

            if(self.instructionSequence[i].opcode1[13:] == "224"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                thirdInput = decodeReg(self.instructionSequence[i].opcode1, 6)
                fourthInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                self.instructionSequence[i].decoded += "IMAD.MOV.U32 R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", R" + str(thirdInput) + ", R" + str(fourthInput)

            if(self.instructionSequence[i].opcode1[13:] == "824"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = int(self.instructionSequence[i].opcode1[0:8], 16)
                thirdInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                someModifyingCodeTODO = int(self.instructionSequence[i].opcode2[9: 14], 16)
                self.instructionSequence[i].decoded += "IMAD R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", " + hex(offset) + ", R" + str(thirdInput)

            if(self.instructionSequence[i].opcode1[13:] == "227"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                thirdInput = decodeReg(self.instructionSequence[i].opcode1, 6)
                fourthInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                self.instructionSequence[i].decoded += "IMAD.HI.U32 R," + str(destRegNr) + ", R" + str(sourceRegNr) + ", R" + str(thirdInput) + ", R" + str(fourthInput)

            if(self.instructionSequence[i].opcode1[13:] == "348"):
                regNr = decodeReg(self.instructionSequence[i].opcode1, 6)
                self.instructionSequence[i].decoded += "WARPSYNC R" + str(regNr)

            if(self.instructionSequence[i].opcode1[13:] == "942"):
                self.instructionSequence[i].decoded += "BREAK"

            if(self.instructionSequence[i].opcode1[13:] == "941"):
                barNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                self.instructionSequence[i].decoded += "BSYNC B" + str(barNr)
            
            if(self.instructionSequence[i].opcode1[13:] == "945"):
                barNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                offset = "TODO"
                self.instructionSequence[i].decoded += "BSSY" + " B" + str(barNr) + ", " + offset 

            if(self.instructionSequence[i].opcode1[13:] == "356"):
                barNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                regNr = decodeReg(self.instructionSequence[i].opcode1, 6)
                self.instructionSequence[i].decoded += "BMOV.32 B" + str(barNr) + ", R" + str(regNr)

            if(self.instructionSequence[i].opcode1[13:] == "355"):
                barNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                regNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                self.instructionSequence[i].decoded += "BMOV.32.CLEAR R" + str(barNr) + ", B" + str(regNr)

            if(self.instructionSequence[i].opcode1[13:] == "212"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                thirdInput = decodeReg(self.instructionSequence[i].opcode1, 6)
                fourthInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                offset = int(self.instructionSequence[i].opcode2[12:14], 16)
                self.instructionSequence[i].decoded += "LOP3.LUT" + " R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", R" + str(thirdInput) + ", R" + str(fourthInput) + ", " + hex(offset) + ", !PT"
            
            if(self.instructionSequence[i].opcode1[13:] == "812"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = int(self.instructionSequence[i].opcode1[0:8], 16)
                thirdInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                lut = int(self.instructionSequence[i].opcode2[12:14], 16)
                self.instructionSequence[i].decoded += "LOP3.LUT" + " R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", " + hex(offset) + ", R" + str(thirdInput) + ", " + hex(lut) + " !PT TODO"
                # instructionSequence[i].decoded += "LOP3.LUT TODO"

            if(self.instructionSequence[i].opcode1[13:] == "38a"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 6)
                addressRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = self.instructionSequence[i].opcode1[0:6]
                modifier = int(self.instructionSequence[i].opcode2[11:16], 16)
                modifiers = {
                    0x149ff: ".E.ADD.F16x2.RN.STRONG.GPU",
                    0xf41ff: ".E.ADD.STRONG.GPU",

                }
                if(modifier in modifiers):
                    modifier = modifiers[modifier]
                else:
                    modifier = ".UNKNOWNMODIFIER"
                self.instructionSequence[i].decoded += "ATOM" + modifier + " PT, R" + str(destRegNr) + ", [R" + str(addressRegNr) + "+0x" + offset + "], R" + str(sourceRegNr)

            if(self.instructionSequence[i].opcode1[13:] == "3a8"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 6)
                addressRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = self.instructionSequence[i].opcode1[0:6]
                modifier = int(self.instructionSequence[i].opcode2[11:16], 16)
                modifiers = {
                    0x149ff: ".E.ADD.F16x2.RN.STRONG.GPU",
                    0xf41ff: ".E.ADD.STRONG.GPU",

                }
                if(modifier in modifiers):
                    modifier = modifiers[modifier]
                else:
                    modifier = ".UNKNOWNMODIFIER"
                self.instructionSequence[i].decoded += "ATOMG" + modifier + " PT, R" + str(destRegNr) + ", [R" + str(addressRegNr) + "+0x" + offset + "], R" + str(sourceRegNr)

            if(self.instructionSequence[i].opcode1[13:] == "207"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                thirdInput = decodeReg(self.instructionSequence[i].opcode1, 6)
                predicate = int(self.instructionSequence[i].opcode2[9:11], 16) >> 3
                self.instructionSequence[i].decoded += "SEL R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", R" + str(thirdInput) + ", P" + str(predicate)


            if(self.instructionSequence[i].opcode1[13:] == "807"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                offset = int(self.instructionSequence[i].opcode1[0:8], 16)
                predicate = int(self.instructionSequence[i].opcode2[9:11], 16) >> 3
                # predicate = int(instructionSequence[i].opcode2[9], 16) << 1
                # if predicate > 7:
                #     predicate = "!P" + str(predicate - 8)
                # else:
                #     predicate = "P" + str(predicate)
                self.instructionSequence[i].decoded += "SEL R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", " + hex(offset) + ", P" + str(predicate)

            if(self.instructionSequence[i].opcode1[13:] == "819"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                imediate = int(self.instructionSequence[i].opcode1[0:8], 16)
                thirdInput = decodeReg(self.instructionSequence[i].opcode2, 14)
                modifier = int(self.instructionSequence[i].opcode2[11:14], 16)
                modifiers = {
                    0x012: ".R.U64",
                    0x006: ".L.U32",
                }
                if modifier in modifiers:
                    modifier = modifiers[modifier]
                else:
                    modifier = ".UNKNOWNMODIFIER"
                self.instructionSequence[i].decoded += "SHF" + modifier + " R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", " + hex(imediate) + ", R" + str(thirdInput)

            if(self.instructionSequence[i].opcode1[13:] == "308"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                self.instructionSequence[i].decoded += "MUFU.RCP R" + str(destRegNr) + ", R" + str(sourceRegNr) + " POSSIBLY WRONG REGISTERS " 

            if(self.instructionSequence[i].opcode1[13:] == "305"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 6)
                self.instructionSequence[i].decoded += "F2I.FTZ.U32.TRUNC.NTZ R" + str(destRegNr) + ", R" + str(sourceRegNr) + " POSSIBLY WRONG REGISTERS "
            if(self.instructionSequence[i].opcode1[13:] == "306"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 6)
                self.instructionSequence[i].decoded += "F2I.U32.RP R" + str(destRegNr) + ", R" + str(sourceRegNr) + " POSSIBLY WRONG REGISTERS "

            if(self.instructionSequence[i].opcode1[13:] == "217"):
                destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                thirdInput = decodeReg(self.instructionSequence[i].opcode1, 6)
                predication = int(self.instructionSequence[i].opcode2[9:11], 16)
                if predication == 0x38:
                    predication = "PT"
                elif(predication == 0x78):
                    predication = "!PT"
                else:
                    predication = "UNKNOWNPREDICATION"

                modifier = int(self.instructionSequence[i].opcode2[12:14], 16)
                if(modifier == 0x0):
                    modifier = ".U32"
                elif(modifier == 0x2):
                    modifier = ""
                else:
                    modifier = ".UNKNOWNMODIFIER"
                self.instructionSequence[i].decoded += "IMNMX" + modifier + " R" + str(destRegNr) + ", R" + str(sourceRegNr) + ", R" + str(thirdInput) + ", " + predication
            
            if(self.instructionSequence[i].opcode1[13:] == "817"):
                self.destRegNr = decodeReg(self.instructionSequence[i].opcode1, 10)
                self.sourceRegNr = decodeReg(self.instructionSequence[i].opcode1, 8)
                self.immediate = int(self.instructionSequence[i].opcode1[0:8], 16)
                predication = int(self.instructionSequence[i].opcode2[9:11], 16)
                if predication == 0x38:
                    predication = "PT"
                elif(predication == 0x78):
                    predication = "!PT"
                else:
                    predication = "UNKNOWNPREDICATION"
                self.instructionSequence[i].decoded += "IMNMX R" + str(self.destRegNr) + ", R" + str(self.sourceRegNr) + ", " + hex(self.immediate) + ", " + predication


            if(self.instructionSequence[i].opcode1[13:] == "992"):
                self.instructionSequence[i].decoded += "MEMBAR.SC.GPU/CTA"

            if(self.instructionSequence[i].opcode1[13:] == "98f"):
                self.instructionSequence[i].decoded += "CCTL.IVALL"

            if(self.instructionSequence[i].opcode1[13:] == "95c"):
                self.instructionSequence[i].decoded += "BPT.TRAP 0x1 (TODO)"

            if(self.instructionSequence[i].opcode1[13:] == "98e"):
                self.instructionSequence[i].decoded += "RED TODO DECODE FURTHER"

            if(self.instructionSequence[i].opcode1[13:] == "20c"):
                cregNr1 = decodeReg(self.instructionSequence[i].opcode1, 8)
                cregNr2 = decodeReg(self.instructionSequence[i].opcode1, 6)
                firstPNR = str(int(self.instructionSequence[i].opcode2[11], 16) >> 1)
                finalPNr = self.instructionSequence[i].opcode2[14]
                if(finalPNr == "7"):
                    finalPNr = "T"
                compareCode = self.instructionSequence[i].opcode2[12:14]
                compareCodes = {
                    "53": ".NE.AND.EX",
                    "52": ".NE.AND",
                    "51": ".NE.U32.AND.EX",
                    "50": ".NE.U32.AND",
                    "20": ".EQ.U32.AND",
                    "22": ".EQ.AND",
                    "27": ".EQ.OR.EX",
                    "10": ".LT.U32.AND ",
                    "11": ".LT.U32.AND.EX",
                    "60": ".GE.U32.AND",
                    "40": ".GT.U32.AND",
                    "41": ".GT.U32.AND.EX",
                }
                if(compareCode in compareCodes):
                    compareCode = compareCodes[compareCode]
                else:
                    compareCode = ".UNKNOWN"

                # TODO INCOMPLETE

                self.instructionSequence[i].decoded += "ISETP" + compareCode + " P" + firstPNR + ", PT, R" + str(cregNr1) + ", R" + str(cregNr2) +", P" + finalPNr + " !TODO INCOMPLETE DECODE!"   

            if(self.instructionSequence[i].opcode1[13:] == "80c"):
                cregNr1 = decodeReg(self.instructionSequence[i].opcode1, 8)
                imediate = int(self.instructionSequence[i].opcode1[0:8], 16)
                firstPNR = str(int(self.instructionSequence[i].opcode2[11], 16) >> 1)
                finalPNr = self.instructionSequence[i].opcode2[14]
                if(finalPNr == "7"):
                    finalPNr = "T"
                compareCode = self.instructionSequence[i].opcode2[12:14]
                compareCodes = {
                    "53": ".NE.AND.EX",
                    "52": ".NE.AND",
                    "51": ".NE.U32.AND.EX",
                    "50": ".NE.U32.AND",
                    "20": ".EQ.U32.AND",
                    "22": ".EQ.AND",
                    "27": ".EQ.OR.EX",
                    "10": ".LT.U32.AND ",
                    "11": ".LT.U32.AND.EX",
                    "60": ".GE.U32.AND",
                    "40": ".GT.U32.AND",
                    "41": ".GT.U32.AND.EX",
                }
                if(compareCode in compareCodes):
                    compareCode = compareCodes[compareCode]
                else:
                    compareCode = ".UNKNOWN"

                # TODO INCOMPLETE

                self.instructionSequence[i].decoded += "ISETP" + compareCode + " P" + firstPNR + ", PT, R" + str(cregNr1) + ", " + hex(imediate) +", P" + finalPNr + " !TODO INCOMPLETE DECODE!"  

            if(self.instructionSequence[i].decoded == ""):
                self.instructionSequence[i].decoded += "UNKNOWN"

            # Assign predicate
            if(self.instructionSequence[i].opcode1[12] != "7"):
                predicate = int(self.instructionSequence[i].opcode1[12], 16)
                if predicate > 7:
                    predicate = "@!P" + str(predicate - 8)
                else:
                    predicate = "@P" + str(predicate)
                self.instructionSequence[i].decoded = predicate + " " + self.instructionSequence[i].decoded

            self.instructionSequence[i].print()


# Helper functions
def decodeReg(s, index):
    reg = int(s[index:index+2], 16)
    if(reg == 255):
        reg = "Z"
    return reg

def decodePred(s, index):
    pred = int(s[index:index+2], 16)
    if(pred == 15):
        pred = "T"
    return pred