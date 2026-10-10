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

## 8. Superheated Vapor: Multivariate Linear Regression (Part 2)

### 8.1 Target and features

- **Target:** specific enthalpy H [kJ/kg] of superheated vapor (temperature columns `'75'` to `'650'` of the H dataframe)
- **Features:** pressure P [kPa] and temperature T [°C]
- Superheated vapor is single-phase, so T and P are independent (F = 2) and H = f(P, T).
- Empty cells (NaN) mark states below the saturation temperature at that pressure, or temperatures not tabulated.

### 8.2 Data preparation

- The H table has 136 pressures × 33 temperatures = 4,488 cells.
- `np.meshgrid(P, T)` builds two grids of shape (33, 136), one with the pressure and one with the temperature of every cell. Z (the H block) has shape (136, 33), so it is transposed to match.
- X, Y and Z.T are flattened with `reshape(-1, 1)` so that position *i* refers to the same cell in all three arrays.
- Rows with NaN enthalpy are removed with a boolean mask.

| Check | Value |
|---|---|
| Total cells | 4,488 |
| Filled cells (`notna().sum().sum()`) | 2,063 |
| NaN cells | 2,425 |
| Rows after cleaning | 2,063 |

The cleaned row count matches the number of filled cells in the table.

**Implementation note:** the tutorial's loop (`P_clean[j] = Ps[i]`) fails on recent NumPy versions because `Ps[i]` is a one-element array, not a scalar. Fixed by masking on the raveled arrays instead of looping.

### 8.3 Model

`LinearRegression` on `[P, T]` → H.

| Quantity | Value |
|---|---|
| P coefficient | −0.0181 kJ/kg per kPa |
| T coefficient | 2.267 kJ/kg/K |
| Intercept | 2380.3 kJ/kg |
| R² | 0.9877 |

**Interpretation**

- **T coefficient:** the average heat capacity of steam over the data range, physically sensible (about 2 kJ/kg/K).
- **P coefficient:** small and negative. Enthalpy of a real gas falls slightly with pressure at constant T. For an ideal gas it would be zero.
- **Intercept:** H extrapolated to P = 0, T = 0 °C, well outside the data (table starts at 75 °C). A fitting constant, not a physical value.

### 8.4 Residual analysis

Residuals (actual − predicted) range from about −190 to +90 kJ/kg, up to roughly 5 to 7% of H.

**Residuals vs. temperature**

- U-shaped: positive at low T (about +90 at 75 °C), minimum near 300 to 340 °C (about −190 at high P), positive again at high T (about +87 at 650 °C).
- A plane is linear in T, so this shows H is curved in T. This is consistent with heat capacity rising with temperature.
- The largest errors are near the saturation boundary at high pressure, where steam is farthest from ideal-gas behavior.

**Residuals vs. pressure**

- Each temperature forms its own streak, and the slope of the streak depends on T. Cool steam starts positive and falls steeply with P. Hot steam starts negative and rises with P.
- The plane has a single P coefficient, but the effect of P on H changes with T (strong at low T, near zero at high T, as for an ideal gas). This indicates a **P × T interaction** that the model cannot represent.

**Why R² is still high (0.988):** H increases steadily with T, which dominates the total variance, so a plane captures most of it. As in Part 1, a high R² does not mean a good model.

### 8.5 Conclusion and next steps

- The multivariate linear model is physically reasonable but systematically wrong in two ways: curvature in T and a P × T interaction.
- Next: refit with a degree-2 polynomial in (P, T), which adds T², P² and P × T, then repeat the same two residual plots. Standardize inputs, since P is in the thousands and T in the hundreds.
- Still to do: 3D surface plot with `plot_surface`, polynomial and log-basis GLM for saturated liquid V, hand-built prediction functions from fitted coefficients, train/test and extrapolation checks, RMSE and MAE comparison.