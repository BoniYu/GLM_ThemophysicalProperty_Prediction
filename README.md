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

All metrics are computed on the training data. A train/test split has not been done.

### Saturated liquid volume V(P)

| Model | Coefficients | R² |
|---|---|---|
| Linear | 2 | 0.975 |
| Polynomial, degree 2 | 3 | 0.987 |
| Polynomial, degree 3 | 4 | 0.994 |
| Polynomial, degree 4 | 5 | 0.997 |
| Polynomial, degree 5 | 6 | 0.998 |
| Logarithmic (P, ln P) | 3 | 0.998 |

V = 0.9568 + 3.134×10⁻⁵ · P + 0.02004 · ln P  (P in kPa, V in cm³/g)

### Superheated enthalpy H(P, T)

| Model | Features | R² | RMSE [kJ/kg] |
|---|---|---|---|
| Linear | 2 | 0.9877 | 33.6 |
| Polynomial, degree 2 | 5 | 0.9978 | 14.1 |
| Polynomial, degree 3 | 9 | 0.9996 | 6.2 |
| Logarithmic (P, T, ln P, T ln P) | 4 | 0.9942 | 23.1 |

### Findings
- A basis function that matches the physics (the log for V) gives a better fit with fewer coefficients than a high-degree polynomial.
- Unscaled high-degree polynomials fail numerically with newer scikit-learn versions. Standardizing the inputs before the polynomial step fixes it.
- For H, the degree-2 and degree-3 polynomials fit better than the log basis, because most of the curvature is in temperature.
- Models for V are saved in `models/` with their coefficients.