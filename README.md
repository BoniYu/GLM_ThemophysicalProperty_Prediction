# GLM for Thermophysical Property Prediction

Generalized linear models (linear regression with basis functions) for predicting thermophysical properties of water and steam from steam-table data. The project follows the [MLCE_book GLM tutorial](https://edgarsmdn.github.io/MLCE_book/03_GLM_thermophysical.html) and adds extra analysis: scaling effects, a multi-output fit, and physical interpretation of the fitted coefficients.

> **Status:** complete. Metrics are on training data only; no train/test split was done.

## Data

Steam tables for saturated and superheated water from Appendix F of Smith, Van Ness, Abbott & Swihart, *Introduction to Chemical Engineering Thermodynamics*, 7th ed., as distributed with MLCE_book.

- File: `superheated_vapor.csv` (https://github.com/edgarsmdn/MLCE_book/tree/main/references)
- Properties: V [cm³/g], U [kJ/kg], H [kJ/kg], S [kJ/(kg·K)]
- Pressure in kPa, temperature in °C
- 2063 valid (P, T) points, identical for V, U, H and S

## What was done

1. **Saturated liquid volume V(P):** linear (whole range and piecewise), polynomial (degrees 1 to 5) and logarithmic models.
2. **Superheated enthalpy H(P, T):** multiple linear regression, polynomial models (degrees 1 to 3) and a logarithmic basis.
3. **Multi-output regression (extra analysis):** H, U and S from P and T together. S needed its own logarithmic basis.

## Results

All metrics are on the training data.

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

### Superheated entropy S(P, T)

| Model | R² | RMSE [kJ/(kg·K)] |
|---|---|---|
| Linear in P, T | 0.665 | |
| Log basis (P, T, ln P, T ln P) | 0.9948 | 0.0562 |
| **Log basis (P, T, ln P, ln T_K)** | **0.9962** | **0.0484** |

S = 1.1423 − 1.730×10⁻⁵ · P + 1.311×10⁻³ · T − 0.4686 · ln P + 1.388 · ln T_K  (T in °C, T_K = T + 273.15)

The ln P coefficient is within about 2% of −R for steam (−0.4615), and the effective heat capacity at 300 °C is about 2.14 kJ/(kg·K).

## Key findings

- The best basis depends on the physics of each property: ln P for V, a T² term for H, and ln P and ln T for S.
- A high R² can hide missing structure. Residual and predicted vs actual plots showed it for the linear H and S models.
- Standardize inputs before high-degree polynomial features; otherwise newer scikit-learn versions drop terms and R² collapses.

## Project structure

```
glm-thermophysical/
├── data/
├── Notebooks/
├── models/              # saved V models (joblib) and coefficients (JSON)
├── features.py          # custom transformers (log features)
├── Report.md            # detailed write-up
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install numpy pandas matplotlib scikit-learn jupyter joblib
```

## Limitations

- No train/test split, extrapolation test or cross-validation. Metrics describe how well each basis approximates the table, not generalization.
- Only the V models are saved.
- The data is a smooth steam table without measurement noise.

## References

- Sanchez Medina, E. I., del Rio Chanona, A., Ganzer, C. *Machine Learning in Chemical Engineering* (MLCE_book), 2023. https://edgarsmdn.github.io/MLCE_book/
- Smith, J. M., Van Ness, H. C., Abbott, M. M., Swihart, M. T. *Introduction to Chemical Engineering Thermodynamics*, 7th ed., McGraw-Hill, 2004.