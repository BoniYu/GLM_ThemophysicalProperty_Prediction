# Report: GLM for Thermophysical Property Prediction

> Work in progress. Covers the tutorial replication up to the piecewise linear fit.

## 1. Thermodynamic Background

- Steam properties (V, U, H, S) are state functions, so each is a function of the state variables only.
- For a pure single-phase fluid, the phase rule (F = C − P + 2) gives 2 degrees of freedom, so superheated vapor properties are functions of P and T.
- For saturated liquid or vapor (two phases), F = 1, so properties depend on P alone.
- Each property has its own units and scale, so each is modeled separately.

## 2. Data

- Source: Appendix F of Smith, Van Ness & Abbott, *Introduction to Chemical Engineering Thermodynamics* (7th ed.), via the MLCE_book repository (`superheated_vapor.csv`).
- Wide format: one row per (pressure, property), with `Liq_Sat`, `Vap_Sat` and one column per temperature (°C).
- Temperature column headers are read as strings (`'75'`, `'100'`, ...) and must be converted to numbers before use.
- Temperature columns contain NaN where a (P, T) combination is not tabulated.
- Data was split by the `Property` column into separate dataframes `V`, `U`, `H` and `S`.

## 3. Target and Feature (Part 1)

- **Target:** `Liq_Sat` in the V dataframe (saturated liquid specific volume, cm³/g)
- **Feature:** pressure P (kPa)
- 136 data points. Specific volume ranges from 1.000 to 1.504 (mean 1.215).

## 4. Exploratory Data Analysis

- Plotted `Liq_Sat` against P for all four properties.
- The trend is clearly non-linear for V, steep at low pressure and flattening at high pressure.

## 5. Single Linear Regression (whole range)

| Quantity | Value |
|---|---|
| R² | 0.975 |
| Intercept | 1.078 |
| Slope | 3.92e-5 |

**Residual analysis**

- Residuals (actual − predicted) are not random. They are negative at low pressure (down to about −0.08), positive in the mid range (peak about +0.02 near 2500 kPa), and negative again at high pressure (about −0.02).
- This systematic pattern shows the model form is wrong: a straight line cannot capture the curvature.
- The line overestimates at low pressure (predicts about 1.08 vs. an actual value of about 1.00).

**Why R² is still high**

- R² averages error over all points and is dominated by the long, nearly linear high-pressure range.
- The steep low-pressure region has few points and small absolute errors, so it barely affects R².
- A high R² does not mean a good model. Residuals must be checked.

**Side experiment: wrong target (`Vap_Sat`)**

- R² = 0.017, intercept 2990, slope −0.452.
- Saturated vapor volume behaves roughly like V ≈ RT/P (hyperbolic) and spans orders of magnitude, so a straight line in P fails completely.
- Useful contrast case for choosing basis functions later (e.g. 1/P or log).

## 6. Piecewise Linear Regression (3 sections)

Sections split at 300 kPa and 1500 kPa, with a separate linear fit in each.

| Section | Range (kPa) | Slope | Intercept | R² |
|---|---|---|---|---|
| 1 | < 300 | 2.314e-4 | 1.0144 | 0.9263 |
| 2 | 300 to 1500 | 6.677e-5 | 1.0592 | 0.9870 |
| 3 | ≥ 1500 | 3.442e-5 | 1.1107 | 0.9990 |

Results match the tutorial exactly.

**Observations**

- Slopes decrease with pressure: the curve is steepest at low pressure and flattens out.
- Intercepts of sections 2 and 3 do not match the physical low-pressure volume (about 1.0), since those lines are only valid within their own range.
- R² rises as sections get closer to linear. R² values are not directly comparable to the whole-range fit, because R² is relative to the variance within each section. RMSE or MAE should be used for a fair comparison.

**Limitation: discontinuous model**

- At 300 kPa the neighboring lines differ by about 0.0046 cm³/g, and at 1500 kPa by about 0.0030 cm³/g.
- The gradient is undefined at the boundaries, which is problematic for optimization and process simulation.
- This motivates a smooth, single model (GLM with basis functions).

## 7. Open Questions / Next Steps

- Compare RMSE and MAE of the single-line and piecewise models.
- Test whether standardizing P changes the OLS fit (expected: same predictions, different coefficients).
- Train/test split and extrapolation check.
- Multivariate linear regression for superheated vapor enthalpy H(P, T).
- GLM with polynomial basis (degree 4) and with a logarithmic basis, with residual plots.