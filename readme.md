# CUDA, Woulda, Shoulda: Returning Exploits for a SASS-y World
This repository accompanies the our paper published at EuroSec 2025, which you can read [here](https://adriaanjacobs.github.io/files/eurosec2025cudawouldashoulda.pdf).


## Analysis of the CUDA SASS Architecture

``` py
TuringISA = aib.BinToISA("sm_75")
TuringISA.analyzeBinary("<path to fatbin>")
TuringISA.analyzeDump("<path to dumped fatbin>")
TuringISA.printOpcodes(True)
TuringISA.analyzeSubOps()
TuringISA.generateReport("<output file path>")
```

## Generation and Analysis of ROP Gadgets

``` py
analyzer = rda.rawDumpAnalyzer("<path to memory dump>", 0x0026e00000, (((0x0026e00000>>21) + 1) << 21))
analyzer.analyze()
```

``` py
analyzer = ba.BinaryAnalyzer("<path to fatbin>")
analyzer.createInstructionSequence()
constructor.instructions = analyzer.instructionSequence
constructor.analyze()
```

## Vulnerable GPU Application and Proof-of-Concept ROP Chains

```
cd vulnerableGPUApp
make dbg=1
./build/vuln <path to input file>
```

## Cite this Work
Read our paper: https://adriaanjacobs.github.io/files/eurosec2025cudawouldashoulda.pdf
```
@article{roels2025cuda,
  title={CUDA, Woulda, Shoulda: Returning Exploits in a SASS-y World},
  author={Roels, Jonas and Jacobs, Adriaan and Volckaert, Stijn},
  year={2025},
  doi={10.1145/3722041.3723099},
  booktitle = {The 18th European Workshop on Systems Security},
  series={EuroSec'25}
}
```