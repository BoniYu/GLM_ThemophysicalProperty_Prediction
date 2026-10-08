# GLM for Thermophysical Property Prediction

Generalized linear models (GLMs) for predicting thermophysical properties of water/steam from steam-table data. The project follows the MLCE_book GLM tutorial first, then extends it with proper validation and thermodynamic consistency checks.

Status: in progress. Tutorial replication is underway; extensions are planned.

## Overview

Steam-table properties (specific volume, internal energy, enthalpy, entropy) are non-linear functions of pressure and temperature. This project shows how linear regression, extended with basis functions, can model them with smooth, interpretable equations that are useful for process simulation and optimization.

Each property (V, U, H, S) is modeled separately, since each has its own units and scale. For a pure single-phase fluid, two intensive variables (here T and P) fix the state, so the superheated-vapor models take both as inputs. Saturated liquid is a one-dimensional problem in pressure.

## Data

Steam tables for saturated and superheated water from Appendix F of Smith, Van Ness, Abbott & Swihart, Introduction to Chemical Engineering Thermodynamics, 7th ed. (McGraw-Hill, 2004), as distributed with the MLCE_book repository:

File: superheated_vapor.csv
Source: https://github.com/edgarsmdn/MLCE_book/tree/main/references
Properties: V [cm³/g], U [kJ/kg], H [kJ/kg], S [kJ/kg/K]
Pressure in kPa, temperature in °C, plus saturated liquid and vapor columns

## Plan

1. Tutorial replication: EDA, piecewise linear, multivariate linear, polynomial and log-basis GLMs
2. Extensions: train/test split, scaling, basis comparison, models for U, H, S, thermodynamic consistency checks

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install numpy pandas matplotlib scikit-learn jupyter
```

## References

- Sanchez Medina, del Rio Chanona, Ganzer. *Machine Learning in Chemical Engineering*, 2023.
- Smith, Van Ness, Abbott, Swihart. *Introduction to Chemical Engineering Thermodynamics*, 7th ed., 2004.

## Results

- To be added once the modeling phase is complete. Detailed findings will go in a separate Report.md.