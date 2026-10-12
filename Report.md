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

## Part 9: Polynomial GLM for saturated liquid volume V(P)

### Goal
Fit polynomial models of degree 1 to 5 to saturated liquid volume (`Liq_Sat`) as a function of pressure, and compare them with the MLCE_book tutorial.

### Method
- Data: V rows of the steam table, 136 pressure points from 1 to 11400 kPa; target is `Liq_Sat` (1.0 to 1.504 cm³/g).
- Model: scikit-learn `Pipeline` of `PolynomialFeatures` followed by `LinearRegression`.
- Metric: R² on the training data (no train/test split yet).

### First attempt: unscaled pressure
R² did not rise with degree, and degree 4 gave 0.866 against the tutorial's 0.997.

| Degree | R² (unscaled) |
|---|---|
| 1 | 0.975 |
| 2 | 0.987 |
| 3 | 0.935 |
| 4 | 0.866 |
| 5 | 0.790 |

### Diagnosis
- P ranges from 1 to 11400, so P⁴ is about 10¹⁶ while P is about 10³. The polynomial columns differ in size by many orders of magnitude (ill-conditioned).
- The newer scikit-learn solver uses a looser cutoff (`tol=1e-6`) and treats the small columns as noise. The notebook showed `rank_` = 2 for degrees 3 to 5, so only 2 of the polynomial terms were kept, which made higher degrees behave like a lower-degree model.
- The tutorial was most likely run with an older version that kept all terms. This is inferred from the results, not checked against the book's exact version.
- Refitting with a tight cutoff gave 0.994 (degree 3) and 0.997 (degree 4), matching the tutorial.

### Fix
Standardize P before generating the polynomial features:

```python
Pipeline([
    ("scaler", StandardScaler()),
    ("polynomial_features", PolynomialFeatures(degree=n, include_bias=False)),
    ("linear_regression", LinearRegression()),
])
```

### Results after scaling

| Degree | R² |
|---|---|
| 1 | 0.975 |
| 2 | 0.987 |
| 3 | 0.994 |
| 4 | 0.997 |
| 5 | 0.998 |

Degree 4 now matches the tutorial's 0.997.

### Takeaways
- Scaling does not change plain linear regression in exact arithmetic, but it matters for high-degree polynomials because of numerical conditioning.
- A result from a book can change when the library underneath it changes. Check the rank and conditioning of the fit instead of trusting R² alone.
- Training R² always rises with degree. Whether degree 4 or 5 is actually better needs a train/test split and an extrapolation check, which are planned extensions.

### Next
Log-basis GLM for V, then the train/test and extrapolation comparison of polynomial and log models.

## Part 4: Polynomial and logarithmic GLMs for saturated liquid volume V(P)

### Goal
Go beyond the straight-line fit by adding basis functions of pressure, and compare the polynomial and logarithmic models on saturated liquid volume (`Liq_Sat`). This closes the single-variable regression part of the project.

### Models
A generalized linear model (GLM) here is still linear in its coefficients. The curve in P comes from the features built from P, not from the fitting method, which is ordinary least squares in every case.

**Linear**

$$V = b_0 + b_1 P$$

**Polynomial of degree n**

$$V = b_0 + b_1 P + b_2 P^2 + \dots + b_n P^n$$

The features are $[P, P^2, \dots, P^n]$.

**Logarithmic basis**

$$V = b_0 + b_1 P + b_2 \ln P$$

The features are $[P, \ln P]$. The input is still one pressure column of shape (136, 1). The pipeline expands it to two features inside, using a custom `log_feature` transformer. The target `Liq_Sat` is not transformed.

### Implementation notes
- The polynomial pipeline is `StandardScaler` → `PolynomialFeatures` → `LinearRegression`. The scaler comes first (see Part 3).
- The log pipeline is `log_feature` → `StandardScaler` → `LinearRegression`. The log step must come first, because P is positive and standardizing would create negative values, for which the log is undefined.
- Scaling does not change the fit for ordinary least squares in exact arithmetic. It matters for conditioning, and it was needed for the high-degree polynomials.

### Results (training R²)

| Model | Number of coefficients | R² |
|---|---|---|
| Linear (P) | 2 | 0.975 |
| Polynomial, degree 2 | 3 | 0.987 |
| Polynomial, degree 3 | 4 | 0.994 |
| Polynomial, degree 4 | 5 | 0.997 |
| Polynomial, degree 5 | 6 | 0.998 |
| **Logarithmic (P, ln P)** | **3** | **0.998** |

Why both features are needed in the log model: ln P alone gives R² = 0.768, worse than the straight line. P captures the steep, almost linear rise at high pressure, and ln P captures the sharp bend at low pressure. Together they follow the whole curve.

### Residual analysis (log model)
- The fitted curve follows the data closely over almost the whole range.
- Residuals are mostly within ±0.01 cm³/g.
- The residuals are **not** random. They form a wave: negative below about 1000 kPa, positive between about 1000 and 5500 kPa, negative again from about 6000 to 10500 kPa, and positive at the highest pressures. This means the model is still missing some systematic structure.
- The lowest-pressure point (P = 1 kPa) has the largest residual, about +0.043. The model predicts a value below the true 1.0, because ln P changes very quickly near P = 1 and the curve cannot follow it.

### Takeaways
- Choosing basis functions that match the physics of the data gives a better model with fewer parameters. The log model (3 coefficients) matches the degree-5 polynomial (6 coefficients) and beats the degree-4 polynomial (5 coefficients).
- High R² does not mean the model is adequate. The residuals still show a pattern, so an even better basis could exist.
- All values above are **training** R². A model with more flexibility will always score at least as well on the data it was fitted on. Whether the log model is really better than the polynomials, and how each behaves outside the fitted pressure range, needs a train/test split and an extrapolation check. These are planned extensions.

### Next
Multilinear regression for superheated vapor enthalpy H(P, T), starting with a degree-2 polynomial in P and T to remove the structure seen in the residuals of the linear model.

## Part 5: Multiple linear regression for superheated enthalpy H(P, T)

### Goal
Predict the specific enthalpy H of superheated steam from two input variables, pressure P and temperature T, and then test whether polynomial features improve the fit.

### Terminology
One output (H) from several inputs (P, T) is strictly **multiple** regression. "Multivariate" strictly means several outputs predicted together. The MLCE_book tutorial uses "multivariate" loosely for several inputs. The method is ordinary least squares in both cases.

### Data preparation
- The steam table is in wide format: 136 pressure rows and 33 temperature columns (75 to 650 °C), with one block of rows per property.
- `np.meshgrid` pairs every pressure with every temperature, giving 33 × 136 = 4488 grid cells. Cells where the state is not superheated are NaN.
- After flattening and removing the NaN cells, **2063** valid (P, T, H) points remain. This matches the count of non-NaN cells in the table.
- V, U, H and S all share the same 2063 valid (P, T) cells.
- Shapes: the inputs form a (2063, 2) matrix of P and T, and the target is a 1D vector of 2063 H values.

### Model 1: linear

$$H = b_0 + b_1 P + b_2 T$$

| Quantity | Value |
|---|---|
| P coefficient | −0.0181 kJ/kg per kPa |
| T coefficient | 2.267 kJ/kg per °C |
| Intercept | 2380.3 kJ/kg |
| R² | 0.9877 |

The model is a plane in (P, T, H) space. Enthalpy rises with temperature and falls slightly with pressure.

### Residual analysis (linear model)
R² is high, but the residuals show clear structure:
- Against **T**: a U-shaped pattern, so the dependence on temperature is curved, not straight.
- Against **P**: a fan shape, so the spread of the errors depends on P. This suggests an interaction between P and T.

A high R² therefore does not mean the model is adequate. Missing curvature and interaction terms are still visible in the residuals.

### Model 2: polynomial in P and T
Features are built from the two variables, and the model is still linear in its coefficients. A polynomial of degree 2 is:

$$H = b_0 + b_1 P + b_2 T + b_3 P^2 + b_4 PT + b_5 T^2$$

The degree-3 polynomial adds the cubic and mixed terms (9 features in total).

Implementation: `StandardScaler` → `PolynomialFeatures(include_bias=False)` → `LinearRegression`. The scaler comes first because the powers of P (up to 11400 kPa) otherwise differ in size by many orders of magnitude, which caused rank truncation for V in Part 3. Coefficients from the pipeline are in standardized units. They are read through `model.named_steps["linear_regression"]`.

### Results (training data)

| Model | Features | R² | MSE | RMSE [kJ/kg] |
|---|---|---|---|---|
| Linear | 2 | 0.9877 | | |
| Polynomial, degree 2 | 5 | 0.9978 | | |
| Polynomial, degree 3 | 9 | 0.9996 | | |

*(Fill in MSE and RMSE from the notebook output. RMSE is the square root of MSE and is in kJ/kg, so it can be compared with the size of H.)*

### Residual analysis (polynomial models)
*(Add what the residual plots against P and T show for degrees 2 and 3: whether the U-shape and the fan have gone.)*

### Caveats
- All numbers are **training** metrics. Training R² never decreases when features are added, so the degree-3 fit being higher does not show that it is better.
- The comparison that matters is on held-out data: a train/test split, and an ordered split that tests extrapolation to higher pressures or temperatures. These are the planned extensions.

### Next
Logarithmic basis for H(P, T), then comparison of all models on held-out data.

## Part 6: Logarithmic basis for superheated enthalpy H(P, T)

### Goal
Test whether log-transformed pressure features improve the model for H(P, T), and compare it with the linear and polynomial models from Part 5.

### Model
The basis combines the two measured variables and their log interaction:

$$H = a_0 + a_1 P + a_2 T + a_3 \ln P + a_4\, T \ln P$$

Features: $[P,\ T,\ \ln P,\ T \ln P]$, built by a custom transformer (`log_feature_PT`) from the (2063, 2) matrix of P and T.

Implementation: `log_feature_PT` → `StandardScaler` → `LinearRegression`. The log step comes first because P must be positive, and standardizing first would create negative values for which the log is undefined. The scaler follows, because the four features have very different sizes.

### Coefficients (original units)

| Term | Coefficient |
|---|---|
| Intercept $a_0$ | |
| $P$ | |
| $T$ | |
| $\ln P$ | |
| $T \ln P$ | |

*(Fill in from the notebook printout. The standardized coefficients are converted to original units by dividing by the scaler's scale and shifting the intercept.)*

### Results (training data)

| Model | Features | R² | RMSE [kJ/kg] |
|---|---|---|---|
| Linear | P, T | | |
| Polynomial, degree 2 | 5 | | |
| Polynomial, degree 3 | 9 | | |
| Logarithmic | P, T, ln P, T ln P | | |

### Residual analysis
*(Describe the residual plots against P and T for the log model, and compare them with the polynomial models.)*

### Discussion
- For saturated liquid V, the log of pressure was the right basis, because volume changes sharply at low pressure. Enthalpy of superheated steam depends mostly on temperature and weakly on pressure, so the best basis may differ from V's.
- Compare the log model with the polynomial models in the table above, and note which fits better and with how many coefficients.
- All metrics here are on training data. Whether a model generalizes needs held-out data.

---

## Project status

**Completed**
- Exploratory analysis of the steam table (wide format, saturation and superheated regions), with the phase-rule reasoning for the inputs.
- Saturated liquid volume V(P): linear (whole range and piecewise), polynomial (degrees 1 to 5, with the scaling fix) and logarithmic models. Models saved with coefficients.
- Superheated enthalpy H(P, T): multiple linear regression, polynomial models (degrees 1 to 3) and logarithmic basis.

**Optional extra analysis (not in the tutorial)**
- Multivariate regression with several outputs (H, U, S) from the same inputs P and T. For ordinary least squares, it gives the same coefficients as separate fits.

**Possible future work**
- Train/test split and an ordered extrapolation split.
- Ridge, Lasso and cross-validation.
- Thermodynamic consistency check H = U + PV.
