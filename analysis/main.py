from GadgetGeneration import memoryDumpAnalyzer as rda
from GadgetGeneration import gadgetConstructor as gc
from GadgetGeneration import binaryAnalyzer as ba
from ISAAnalysis import AnalyseISAUsingBinary as aib

# analyzer = rda.rawDumpAnalyzer("<path to memory dump>", 0x0026e00000, (((0x0026e00000>>21) + 1) << 21))
# analyzer.analyze()

# analyzer = ba.BinaryAnalyzer("<path to fatbin>")
# analyzer.createInstructionSequence()
# constructor.instructions = analyzer.instructionSequence
# constructor.analyze()

# TuringISA = aib.BinToISA("sm_75")
# TuringISA.analyzeBinary("<path to fatbin>")
# TuringISA.analyzeDump("<path to dumped fatbin>")
# TuringISA.printOpcodes(True)
# TuringISA.analyzeSubOps()
# TuringISA.generateReport("opcodes_SM75.md")