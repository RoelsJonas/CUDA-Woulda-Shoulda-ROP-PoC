import subprocess
class BinToISA:
    def __init__(self, arch: str):
        self.architecture = arch
        self.opcodes = {}
    
    def analyzeBinary(self, fn: str):
        self.fileName = fn
        self.runCuobjdump()
        self.getOpcodes()

    def analyzeDump(self, fn: str):
        self.fileName = fn
        with open(self.fileName, "r") as f:
            self.objdump = f.read()
        self.getOpcodes()

    def runCuobjdump(self):
        # use subprocess to run cuobjdump
        # cuobjdump -sass -arch <filename> > <filename>.txt
        self.objdump = subprocess.run(["cuobjdump", "-sass", "-arch", self.architecture, self.fileName], stdout=subprocess.PIPE, text=True).stdout
    
    def getOpcodes(self):
        lines = self.objdump.split("\n")
        opcodes = {}
        lastOpcode = ""
        permutation = ""
        decoded = ""
        for line in lines:
            if ";" in line:
                decoded = line.split(";")[0].split("*/")[1].strip()
                if "@" in decoded:
                    decodedStripped = decoded.split(" ")[1].split(".")[0].strip()
                else:
                    decodedStripped = decoded.split(" ")[0].split(".")[0].strip()
                opcode = line.split(";")[1].split("*/")[0].strip()[-3:]
                
                if opcode not in self.opcodes:
                    self.opcodes[opcode] = InstructionType(opcode, decodedStripped)
                lastOpcode = opcode
                permutation = line.split(";")[1].split("*/")[0].split("/*")[1].strip()
                if "." in decoded:
                    subOp = decoded.split(decodedStripped)[1].split(" ")[0].strip()
                    if(subOp != ""):
                        self.opcodes[opcode].addSubOp(SubOperation(subOp))

            elif lastOpcode != "":
                self.opcodes[lastOpcode].addPermutation(decoded, permutation + " " + line.split("*/")[0].split("/*")[1].strip())
                lastOpcode = ""

            
    def analyzeSubOps(self):
        for opcode in self.opcodes:
            self.opcodes[opcode].analyzeSubOps()            

            
    def printOpcodes(self, sub=False):
        # sort opcodes on decoded
        for opcode in sorted(self.opcodes, key=lambda x: self.opcodes[x].decoded):
            if sub:
                print(opcode, self.opcodes[opcode].decoded, end=" {")
                for permutation in self.opcodes[opcode].permutations:
                    print("(" + permutation + " ==> " + self.opcodes[opcode].permutations[permutation], end=") ")
                print("}\n")
            else:  
                print(opcode, self.opcodes[opcode].decoded)


    def generateReport(self, fn: str):
        # Print this all to a file
        with open(fn, "w") as f:
            f.write("# Opcodes for " + self.architecture + "\n")
            lastDecoded = ""
            for opcode in sorted(self.opcodes, key=lambda x: self.opcodes[x].decoded):
                if(lastDecoded != self.opcodes[opcode].decoded):
                    f.write("\n")
                    f.write("### " + self.opcodes[opcode].decoded + "\n")
                    lastDecoded = self.opcodes[opcode].decoded
                    
                f.write("- " + opcode + " (" + bin(int(opcode, 16)) + ")\n")
                for subOp in sorted(self.opcodes[opcode].subOps.values(), key=lambda x: x.subOp):
                    f.write("\t- " +  " (" + subOp.bincode + ") " + subOp.subOp + " (" + str(subOp.occurences) + ") ")
                    for opIndex in subOp.operands.keys():
                        f.write(str(opIndex) + ": " + subOp.operands[opIndex])
                        if opIndex in subOp.opLocations.keys():
                            if(len(subOp.opLocations[opIndex]) == 1 and subOp.opLocations[opIndex][0] not in [14,15,16,17,21,22,23,24,25,26]):
                                f.write("[" + str(subOp.opLocations[opIndex][0]) + "]")
                            else:
                                f.write("{" + str(len(subOp.opLocations[opIndex])) + "}")
                        # for loc in subOp.opLocations[opIndex]:
                        #     if loc in [14,15,16,17,21,22,23,24,25,26]:
                        #         continue
                        #     f.write("[" + str(loc) + "]")
                        f.write(", ")
                    f.write("\n")
                f.write("\n")


class InstructionType:
    def __init__(self, opcode: str, decoded: str): 
        self.opcode = opcode
        self.decoded = decoded
        self.permutations = {}
        self.subOps = {}
    
    def addPermutation(self, permutation: str, bincode: str):
        if permutation not in self.permutations:
            self.permutations[permutation] = bincode

    def addSubOp(self, subOp):
        if subOp not in self.subOps.keys():
            self.subOps[subOp.subOp] = subOp
    
    def analyzeSubOps(self):
        for subOp in self.subOps.values():
            permutations = []
            opcodes = []
            for permutation in self.permutations:
                # print(permutation, subOp.subOp, subOp.subOp in permutation)
                if (subOp.subOp + " ") in permutation:
                    opcodes.append(self.permutations[permutation])
                    permutations.append(permutation)
                    subOp.occurences += 1
            
            if(len(opcodes) == 0):
                continue
                
            mask = ""
            for i in range(len(opcodes[0])):
                if all(opcode[i] == opcodes[0][i] for opcode in opcodes):
                    mask += "1"
                else:
                    mask += "0"

            # mask off control logic, predication and opcode bits
            for i in [14,15,16,17,21,22,23,24,25,26]:
                if(i >= len(mask)):
                    break
                mask = mask[:i] + "o" + mask[i+1:]
            
            maskedOpcodes = ""
            for i in range(len(mask)):
                if mask[i] == "1":
                    maskedOpcodes += opcodes[0][i]
                else:
                    maskedOpcodes += "o"

            self.subOps[subOp.subOp].bincode = maskedOpcodes

            for permutation in permutations:
                decoded = permutation
                if("@" in decoded):
                    decoded = decoded.split(" ")[1]
                parts = decoded.split(" ")[1:]

                index = 0
                for part in parts:
                    part = part.split(",")[0].strip()
                    opType = ""
                    opLoc = []
                    if(part == ""):
                        continue

                    # check if part is R followed by 1 or 2 numbers
                    if((len(part) >= 3 and part[0] == "R" and part[1].isdigit() and part[2].isdigit())
                        or (len(part) >= 2 and part[0] == "R" and (part[1].isdigit() or part[1] == "Z"))
                        or (len(part) >= 3 and (part[0] == "~" or part[0] == "-") and part[1] == "R"  and (part[2].isdigit() or part[2] == "Z"))
                        ):
                        opType = "Rn"

                        # find where in the binary instruction the register is located
                        for i in range(0, 32, 2):
                            ind = i + 2
                            if i > 15:
                                ind += 3
                            # print(i, ind, part, self.permutations[permutation][ind:ind+2])
                            if(part.replace("R", "").replace(",", "").replace(".reuse", "").replace(".H0_H0", "").replace("-", "") == str(decodeReg(self.permutations[permutation], ind))):
                                opLoc.append(i)
                        

                    # check if part is R followed by 1 or 2 numbers
                    elif((len(part) >= 3 and part[0] == "U" and part[1] == "R" and (part[2].isdigit() or part[2] == "Z")) or (len(part) >= 4 and (part[0] == "!" or part[0] == "-" or part[0] == "~") and part[1] == "U" and part[2] == "R" and (part[3].isdigit() or part[3] == "Z"))):
                        opType = "U-Rn"
                        # for i in range(0, 32, 2):
                        #     ind = i + 2
                        #     if i > 15:
                        #         ind += 3
                        #     # print(i, ind, part, self.permutations[permutation][ind:ind+2])
                        #     if(part.replace("UR", "").replace(",", "") == str(decodeReg(self.permutations[permutation], ind))):
                        #         opLoc.append(i)
                    
                    # check if part is P followed by 1
                    elif(len(part) >= 2 and part[0] == "P" and (part[1].isdigit() or part[1] == "T") or (len(part) >= 3 and part[0] == "!" and part[1] == "P" and (part[2].isdigit() or part[2] == "T"))):
                        opType = "Pn"
                        for i in range(0, 32, 1):
                            ind = i + 2
                            if i > 15:
                                ind += 3
                            # print(i, ind, part, self.permutations[permutation][ind:ind+1])
                            if(part.replace(",", "").replace(".reuse", "").replace(".H0_H0", "") == str(decodePred(self.permutations[permutation], ind))):
                                opLoc.append(i)

                    # check if part is UP followed by 1
                    elif(len(part) >= 2 and part[0] == "U" and part[1] == "P" and (part[2].isdigit() or part[2] == "T") or (len(part) >= 3 and (part[0] == "!" or part[0] == "-" or part[0] == "~") and part[1] == "U" and part[2] == "P" and (part[3].isdigit() or part[3] == "T"))):
                        opType = "U-Pn"

                    # check if part is a hexadecimal number
                    elif((len(part) > 2 and part[0] == "0" and part[1] == "x") or (len(part) > 3 and part[0] == "-" and part[1] == "0" and part[2] == "x")):
                        opType = "0x..."

                    # check if part is fixed value
                    elif("INF" in part
                         or "QNAN" in part
                         or part.replace(".", "").replace("-", "").replace("e", "").replace("+", "").isnumeric()
                         ):
                        opType = "fixed value"

                    elif("|UR" in part):
                        opType = "|U.Rn|"

                    elif("|R" in part):
                        opType = "|Rn|"


                    # check if part is a constant memory offset
                    elif((len(part) >= 3 and part[0] == "c" and part[1] == "[" and part[-1] == "]")
                         or (len(part) >= 4 and (part[0] == "~" or part[0] == "-") and part[1] == "c" and part[2] == "[" and part[-1] == "]")
                         and "][" in part
                         ):
                        opType = "c[...][...]"

                    # check if part is a constant memory offset
                    elif((len(part) >= 3 and part[0] == "c" and part[1] == "[" and part[-1] == "]")
                         or (len(part) >= 4 and (part[0] == "~" or part[0] == "-") and part[1] == "c" and part[2] == "[" and part[-1] == "]")
                         ):
                        opType = "c[...][...]"
                    
                    elif("|c[" in part and "][" in part):
                        opType = "|c[...][...]|"

                    # check if part is barrier register
                    elif(len(part) >= 2 and part[0] == "B" and part[1].isdigit()):
                        opType = "barrier"

                    # check if part is register (with offset)
                    elif (len(part) >= 4 and part[0] == "[" and part[1] == "R" and (part[2].isdigit() or "Z") and part[-1] == "]"):
                        opType = "[Rn+...]"

                    # check if part is immediate address
                    elif (len(part) >= 4 and part[0] == "[" and part[1] == "0" and part[2] == "x"):
                        opType = "[0x...]"

                    # check if part is uniform register (with offset)
                    elif (len(part) >= 5 and part[0] == "[" and part[1] == "U" and part[2] == "R" and part[3].isdigit() and part[-1] == "]"):
                        opType = "[U-Rn+...]"


                    else:
                        print("Uncategorized part \"" +  part +"\"")
                        print(permutation)
                    
                    if(index not in self.subOps[subOp.subOp].operands):
                        self.subOps[subOp.subOp].operands[index] = opType
                    
                    elif(opType not in self.subOps[subOp.subOp].operands[index]):
                        # print()
                        # print("Error: Operand type mismatch")
                        # print("Permutation: " + permutation)
                        # print("Index: " + str(index))
                        # print("Part: " + part)
                        # print("OpType: " + opType)
                        # print("Previous: " + self.subOps[subOp.subOp].operands[index])
                        # print()
                        self.subOps[subOp.subOp].operands[index] += "/" + opType
                    
                    if(index not in self.subOps[subOp.subOp].opLocations):
                        if(len(opLoc) > 0):
                            self.subOps[subOp.subOp].opLocations[index] = opLoc
                        # elif(opType in ["Rn", "Pn"]):
                        #     print("No loc found for:", permutation + ";", part, self.permutations[permutation])
                        #     print()
                

                    # refine oplocs, must be in the object already and in our arrary
                    elif len(opLoc) > 0:
                        newOpLocs = []
                        for loc in opLoc:
                            if loc in self.subOps[subOp.subOp].opLocations[index] and loc not in [14,15,16,17,21,22,23,24,25,26]:
                                newOpLocs.append(loc)
                        self.subOps[subOp.subOp].opLocations[index] = newOpLocs

                    # elif(opType in ["Rn", "Pn"]):
                    #         print("No loc found for:", permutation + ";", part, self.permutations[permutation])
                    #         print()
                

                    

                    index += 1


        
        # mask of all bits that stay the same for all subOps
        bincodes = []
        for subOp in self.subOps.values():
            if(subOp.bincode != ""):
                bincodes.append(subOp.bincode)

        if(len(bincodes) == 0):
            return

        mask = ""
        for i in range(len(bincodes[0])):
            
            if all(bincodes[0][i] == bincodes[j][i] for j in range(len(bincodes))):
                mask += "0"
            else:
                mask += "1"
        
        for subOp in self.subOps.values():
            bincode = subOp.bincode
            newBinCode = ""
            for i in range(len(bincode)):
                if mask[i] == "1" or bincode[i] in ["x", " "]:
                    newBinCode += bincode[i]
                else:
                    newBinCode += "o"
            self.subOps[subOp.subOp].bincode = newBinCode

            

class SubOperation:
    def __init__(self, subOp: str):
        self.subOp = subOp
        self.bincode = ""
        self.mask = ""
        self.occurences = 0
        self.operands = {}
        self.opLocations = {}

def decodeReg(s, index):
    reg = int(s[index:index+2], 16)
    if(reg == 255):
        reg = "Z"
    return reg

def decodePred(s, index):
    pred = int(s[index:index+1], 16)
    if(pred == 15):
        return "PT"
    elif(pred > 7):
        return "!P" + str(pred - 8)
    return "P" + str(pred)