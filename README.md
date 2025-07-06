# ODER-Retrieval-Simulations

Code, simulations, and documentation for:
**"The ODER Framework: Modeling Forecast Retrieval Failure Across Institutional Actors"**
Evlondo Cooper, 2025

---

## Overview

The Observer-Dependent Entropy Retrieval (ODER) framework models climate forecast failure not as a problem of accuracy, but as a breakdown in signal recognition across institutional actors.
This repository supports simulation, benchmarking, and interpretability of observer-specific retrieval dynamics.

Retrieval is modeled as a time-dependent convergence process governed by a logistic entropy uptake law (see Equation 3 in the manuscript).
This formal structure is implemented in the notebook via the s_retr() function and used throughout to calculate recognition timing (τ_res), lag (Δτ), and retrieval collapse outcomes.

It includes:

* A fully executable simulation notebook that reproduces all benchmark figures from the paper
* Hard-coded observer parameters from three real-world climate events
* An interactive panel for testing γ, τ\_char, and entropy threshold parameters
* A user-defined event tester for simulating real retrieval scenarios and their consequences

---

## Repository Structure

```
├── data/
│   └── retrieval_lag_table.csv       # Calibration data for real-world benchmark events
├── notebooks/
│   └── climate_oder_retrieval.ipynb  # Main simulation notebook (fully self-contained)
├── environment.yml                   # Reproducible environment file (Conda)
├── .gitignore                        # Prevents notebook checkpoints, cache, system files
├── LICENSE                           # MIT License
└── README.md                         # This file
```

---

## Dependencies

The simulation environment requires:

* Python 3.10+
* NumPy
* Matplotlib
* Pandas
* Jupyter Notebook
* Optional: `ipywidgets` (for interactive slider panel)

To install:

**Using Conda (recommended):**

conda env create -f environment.yml
conda activate oder-env

**Using pip (alternative):**

pip install numpy matplotlib pandas jupyter ipywidgets

---

## Running the Simulation

Open the notebook:

notebooks/climate\_oder\_retrieval.ipynb

The notebook provides:

* Reproduction of benchmark retrieval curves for O1, O2, O3 observer classes
* Δτ tables for each event
* Interactive sliders for testing retrieval parameter sensitivity
* A user-defined event simulator (enter real UTC timestamps to test retrieval collapse)
* Interpretation and mitigation guidance based on observer class and Δτ

---

## Benchmarked Events

These three events are hard-coded into the simulation:

| Event                      | Year | Observer Class           | Lag (hours) | Source                   |
| -------------------------- | ---- | ------------------------ | ----------- | ------------------------ |
| Hurricane Ida              | 2021 | O1 (Forecast desk)       | 9           | NOAA Service Assessment  |
| Siberian Heatwave          | 2020 | O2 (Regional agency)     | 72          | WMO + Hydromet Reports   |
| Antarctic Sea Ice Collapse | 2023 | O3 (Policy/Communicator) | 360         | NSIDC Sea Ice Index v3.0 |

Full source metadata is included in `data/retrieval_lag_table.csv`.

---

## Usage Example

To test a new retrieval scenario:

1. Run all cells in the notebook.
2. Scroll to **Section 7: User-defined event test**.
3. Enter two UTC timestamps, e.g.:

Signal timestamp: 2025-07-01T06:00:00Z
Bulletin timestamp: 2025-07-01T14:00:00Z
Observer class: O1

4. The notebook will return:

   * τ\_res (when that observer would have recognized the signal)
   * Δτ (timing difference)
   * Verdict (collapse or not)
   * Interpretability layer (what it means and what could mitigate delay)

---

## Citation

If you use this repository, please cite:

Cooper, E. (2025). *The ODER Framework: Modeling Forecast Retrieval Failure Across Institutional Actors*.
Available at: [https://doi.org/10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX)

Cooper, E. (2025). Climate ODER Retrieval Simulation: Benchmarking Forecast Recognition Across Institutional Observers (v1.0.1). Zenodo. https://doi.org/10.5281/zenodo.15824444

## License

This repository is released under the MIT License.
