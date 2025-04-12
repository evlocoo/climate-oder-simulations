# ODER-Retrieval-Simulations
Code and data for "The ODER Framework: Modeling Forecast Retrieval Failure Across Institutional Actors"
# ODER: Observer-Dependent Entropy Retrieval Framework

This repository contains the simulation code, empirical calibration datasets, and documentation supporting the paper:

> **"The ODER Framework: Modeling Forecast Retrieval Failure Across Institutional Actors"**  
> Submitted to *Earth's Future* (2024)

## 📜 Overview

The ODER framework models forecast retrieval as an observer-specific entropy convergence process. It focuses not on forecast accuracy, but on who retrieves the signal—and when.

This repository supports:
- Simulation-based empirical validation of retrieval divergence (Sections 3.2, 6)
- Reproduction of the observer-specific entropy retrieval model (Equation 4)
- Calibrated parameter sets from three real-world climate events:
  - Hurricane Ida (2021)
  - Siberian Heatwave (2020)
  - Antarctic Sea Ice Collapse (2023)

## 📂 Repo Structure


## 🔧 Dependencies

This repo uses:
- Python 3.10+
- NumPy
- Matplotlib
- Pandas (for data handling)
- Jupyter (for interactive notebooks)

## 📈 Reproducing Figure 1

To generate the benchmark retrieval divergence across observer classes:
1. Open `notebooks/Simulated_Retrieval_Divergence.ipynb`
2. Run cells to load `data/retrieval_lag_table.csv`
3. Simulate entropy convergence using parameters from Appendix A
4. Output is plotted against threshold \( S_{\text{obs}} = 0.7 \)

## 📁 Datasets

All parameter estimates are derived from public institutional sources:
- NOAA/NHC bulletins and advisories (Ida)
- NSIDC Sea Ice Index v3.0 (Antarctica)
- WMO + Russian Hydromet logs (Siberia)

See `data/retrieval_lag_table.csv` for lag timing and source links.

## 🔬 Scope & Disclaimer

This repository supports simulation-based empirical validation only.  
It does not contain full institutional-scale deployments or exhaustive parameter fitting.  
For future validation and pilot implementation strategy, see Section 8 of the manuscript.

## 📘 Citation

If you use this repo, please cite:

> Cooper, E. (2024). *The ODER Framework: Modeling Forecast Retrieval Failure Across Institutional Actors*. Submitted to *Earth’s Future*.

## 🔓 License

This repository is released under the MIT License.
