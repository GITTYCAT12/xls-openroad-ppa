## XLS → OpenROAD PPA GSOC-2026
COPPER -Compiler-driven Optimization for PPA-aware Physical Design and RTL
-----

## Description

This project demonstrates a complete RTL-to-GDSII ASIC design flow using the OpenROAD toolchain. It focuses on evaluating Performance, Power, and Area (PPA) for matrix multiplication architectures, integrating RTL design, simulation, and physical implementation in a modern open-source VLSI workflow.

------
## Installation
1. Clone the repository
2. Ensure dependencies for OpenROAD and simulation tools are installed
3. Navigate to the project directory

----
## Run Simulation
```
cd sim
./run.sh
```
-------

## Manual Simulation Flow
```
iverilog -g2012 ../rtl/*.v -o test.out
vvp test.out
gtkwave wave.vcd
```
---------
## Run OpenROAD Flow

```
# Baseline

cd OpenROAD-flow-scripts/flow
make DESIGN_CONFIG=./designs/nangate45/gcd/config.mk

# Systolic Matrix Multiplication

cd OpenROAD-flow-scripts/flow
make DESIGN_CONFIG=./designs/nangate45/matmul_systolic/config.mk

# Unrolled Matrix Multiplication

cd OpenROAD-flow-scripts/flow
make DESIGN_CONFIG=./designs/nangate45/matmul_unrolled/config.mk
```
----------------
### Features

1. Multiple matrix multiplication architectures:
       Systolic Array
      Unrolled Design
      Streaming Processing Elements
2. Full RTL-to-GDSII flow
3. Functional verification with waveform analysis
4. Automated PPA extraction (Timing, Power, Area)
5. Reusable framework for accelerator exploration

------------------------------
## PPA Report Analyzer

A standard-library Python utility summarizes metrics already present in the OpenROAD reports and can export CSV/JSON. It does not run the physical-design flow.

```bash
python scripts/ppa_report.py --reports-dir reports
python scripts/ppa_report.py --reports-dir reports --csv-out out/ppa-summary.csv --json-out out/ppa-summary.json
python -m unittest discover -s tests -v
```

See [the analyzer documentation](docs/ppa-report-analyzer.md) for metric sources, limitations, and interpretation notes.

---

## Results

 ##  Repository Artifacts

### Reports
- reports/matmul_systolic/6_finish.rpt
- reports/matmul_unrolled/6_finish.rpt

### Final Layout (GDS)
- results/matmul_systolic/6_final.gds
- results/matmul_unrolled/6_final.gds

These files enable reproducibility and verification of the reported PPA metrics.
-----------------------------------------------------------------------------------

### Simulation Output

1. C00 = 19
2. C01 = 22
3. C10 = 43
4. C11 = 50
   
-----------------------------

## RTl-GSDII Results

## Baseline Design

<img width="1536" height="766" alt="Screenshot 2026-03-27 120918" src="https://github.com/user-attachments/assets/028d669a-8480-4174-9628-a568908340fc" />

## Matmul_Systolic

<img width="1530" height="771" alt="Screenshot 2026-03-27 190911" src="https://github.com/user-attachments/assets/6e9efd5a-3757-4d23-98f5-27e364aa700d" />

## Matmul_Unrolled

<img width="1541" height="780" alt="Screenshot 2026-03-27 190954" src="https://github.com/user-attachments/assets/3fd60737-74d5-4c05-bc0a-83b607b93fb9" />

-------------------------------------
## GTKwave Results

<img width="1520" height="729" alt="Screenshot 2026-03-27 125134" src="https://github.com/user-attachments/assets/99fb961e-5f17-4954-a05e-11421c982f2a" />

-------------------------------------
##  RTL → GDS PPA Comparison

| Metric | Baseline Design | Systolic MatMul | Unrolled MatMul |
|--------|---------------|----------------|----------------|
| WNS (ns) | -0.05 | 0.00 | 0.00 |
| TNS (ns) | -0.73 | 0.00 | 0.00 |
| Worst Slack (ns) | — | +3.55 | +3.63 |
| Critical Path (ns) | 0.4138 | — | — |
| Max Frequency (MHz) | ~1977 | ~200 | ~200 |
| Sequential Power (W) | 0.000605 | 0.00081 | 0.00000 |
| Combinational Power (W) | 0.00283 | 0.0129 | 0.00375 |
| Clock Power (W) | 0.000303 | 0.000152 | 0.00000 |
| **Total Power** | **3.74 mW** | **13.9 mW** | **3.75 mW** |
| **Area (µm²)** | — | **8694** | **3629** |

------------------------------------

##  Observations

- The baseline design shows timing violations (negative WNS/TNS), while both systolic and unrolled architectures achieve full timing closure.
- The systolic design consumes higher power due to increased data movement and structured pipeline execution.
- The unrolled design is more area and power-efficient for small matrix sizes.
- The systolic architecture is expected to scale better for larger matrix dimensions

  ----------------------------------------------
### Area

- Standard cell implementation using Nangate45 library.
- Extracted from post placement and routing reports.

------------------------------------------
## Analysis

- Baseline design shows timing violations, while both systolic and unrolled architectures achieve full timing closure.
- Power is dominated by combinational logic due to  intensive MAC operations.
- Clean GDSII generation with no critical DRC violations.

-----------------------------------------------------
### Challenges

- Resolving OpenROAD dependency issues.
- Debugging timing violations after clock tree synthesis.
- Ensuring correct simulation setup and waveform validation.
- integrating RTL with full physical design flow

 ---------------------------------------------------------

### Task Conclusion

This project demonstrates a complete RTL-GDSII implementation using open-source tools and highlights trade-offs between performance, power, and area across different hardware architectures

 ----------------------------------------------------------

 ## PROPOSAL FOR GSOC-2026
 
 ##  Description

This project demonstrates a **complete RTL-to-GDSII ASIC design flow** using the OpenROAD toolchain. It focuses on evaluating **Performance, Power, and Area (PPA)** for matrix multiplication (MatMul) architectures.

The work extends to integrate:

- XLS (High-level hardware compiler)
- MatMul accelerator architectures
- OpenROAD (physical design feedback)

to enable **PPA-aware hardware generation**.

--------------------------------------------------------------

## Current Progress VS Target Contribution

| S No |            Parameter	 |        Work Completed	            |    Proposal	                   |      Contribution                            |
|------|----------------------------|--------------------------------------|----------------------------------|----------------------------------------------|
|  1	|       OpenROAD Flow	 |      Full RTL-to-GDS execution       | No Automation is implemented     |  Build automated evaluation pipeline         |
|  2	|       Matmul Architecture	 |     Unrolled and Systolic analyzed.  | Not integrated with compiler.    |  Encode an lowering strategies in XLS        |
|  3	|      PPA understanding	 |     Qualitative + Layout proof	     | No quantitative dataset	     |  Build structured PPA benchmarking           |
|  4	|      RTL generation	 |     Manual Verilog	            | Not scalable	                   |  Auto generate via XLS                       |
|  5	|       Physical feedback	 |     Observed manually	            | No feedback loop	            | Close loop into compiler decisions           |
|  6	|       Compiler             |     Integration Not implemented	     | Core missing piece	            |  Extend XLS IR and backend                   |

------------------------------------------------------------------

## Detailed Goals, Deliverables, and Execution Plan
### a.Compiler level contributions (XLS)

| Goal | Description                        | Deliverable                 | Methodology                   | Outcome                         |
| ---- | ---------------------------------- | --------------------------- | ----------------------------- | ------------------------------- |
| 1    | Introduction to MatMul abstraction | XLS IR extension PR         | Add tensor-level operation    | ML-native compilation           |
| 2    | Support parameterized MatMul       | Configurable dimensions     | Extend IR and lowering        | Flexible accelerator generation |
| 3    | Enable architecture lowering       | Multiple backend strategies | Strategy selector in compiler | Architecture exploration        |

--------------------------------------

### b.RTL Generation

| S No | Strategy | Description            | Implementation          | Expected Hardware Behavior | PPA Impact            |
| ---- | -------- | ---------------------- | ----------------------- | -------------------------- | --------------------- |
| 1    | Unrolled | Fully parallel compute | Combinational datapath  | 1-cycle latency            | High area, congestion |
| 2    | MAC Tree | Pipelined reduction    | Balanced adder tree     | Moderate latency           | Improved timing       |
| 3    | Systolic | PE grid with dataflow  | 2D array with registers | Streaming computation      | Best scalability      |

---------------------------------------

### c.Open ROAD Integration

| Goal | Description              | Deliverable              | Tools               | Outcome              |
| ---- | ------------------------ | ------------------------ | ------------------- | -------------------- |
| 1    | Automate RTL → GDS flow  | Scripted pipeline        | OpenROAD, TCL       | Batch processing     |
| 2    | Standard evaluation      | Unified config templates | Flow configurations | Reproducibility      |
| 3    | Enable multi-design runs | Architecture sweeps      | Python automation   | Comparative analysis |

-----------------------------------------------

### d.PPA Framework

| S No | Parameter   | Source                | Extraction Method    | Purpose              |
| ---- | ----------- | --------------------- | -------------------- | -------------------- |
| 1    | WNS         | STA reports           | Parse STA output     | Timing quality       |
| 2    | TNS         | STA reports           | Aggregate violations | Stability            |
| 3    | Area        | Synthesis / Placement | Report parsing       | Resource usage       |
| 4    | Power       | Estimation reports    | Tool extraction      | Efficiency           |
| 5    | Routability | Routing logs          | Congestion metrics   | Physical feasibility |

---------------------------------------

## Contribution

| S No | Feature               | Task Submitted          | GSoC Proposal                        |
| ---- | --------------------- | ----------------------- | ------------------------------------ |
| 1    | OpenROAD Usage        | Flow execution          | Feedback-driven engine               |
| 2    | XLS Extension         | Basic operator addition | Architecture-aware lowering system   |
| 3    | MatMul Implementation | Single design           | Multiple competing architectures     |
| 4    | PPA Analysis          | Static comparison       | Dynamic compiler-driven optimization |
| 5    | Flow                  | Linear                  | Closed-loop system                   |

---------------------------------------------------------

## End-to-End Framework

<img width="462" height="836" alt="image" src="https://github.com/user-attachments/assets/6e3cb83d-ac57-4595-b022-f96b9d44445e" />

-------------------------------

## Expected Deliverables

| S No | Deliverable               | Description                | Validation         |
| ---- | ------------------------- | -------------------------- | ------------------ |
| 1    | XLS PR (MatMul Operator)  | ML-native abstraction      | Accepted upstream  |
| 2    | RTL Generation Framework  | Multi-architecture backend | Synthesizable RTL  |
| 3    | OpenROAD Integration Flow | Automated pipeline         | Successful GDS     |
| 4    | PPA Dataset               | Comparative results        | Measurable metrics |
| 5    | Optimization Engine       | Heuristic-based selection  | Improved PPA       |
| 6    | Documentation             | Full methodology           | Reproducibility    |
| 7    | Final Demonstration       | End-to-end pipeline        | Working prototype  |

 ------------------------------------------------

 ## Expected Outcomes

| S No | Description                                                 |
| ---- | ----------------------------------------------------------- |
| 1    | First step toward ML-aware hardware compilation in XLS      |
| 2    | Demonstration of compiler + physical design co-optimization |
| 3    | Open-source framework for AI accelerator development        |
| 4    | Insight into architecture vs physical design trade-offs     |
| 5    | Reproducible research pipeline for future extensions        |

-----------------------------------------------------

## Conclusion

This proposal is implementing isolated components and instead delivers a unified, feedback-driven hardware generation system, where:
- Physical design realities guide compiler decisions 
- Architectural choices are validated through real silicon metrics 
- Open-source tools are combined into a reproducible research pipeline

------------------------------------------------------------

### Acknowledgements

- [Mehdi Saligane](https://github.com/msaligane)
- [Xinting Jiang](https://www.linkedin.com/in/xinting-jiang-74a42b28b/)

  

