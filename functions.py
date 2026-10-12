from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def polynomial_model(X, y, Z, n):
    pf = PolynomialFeatures(degree=n, include_bias=False)
    scaler = StandardScaler()
    Lr = LinearRegression()
    model_poly = Pipeline([("Scaler", scaler), ("polynomial_features", pf), ("linear_regression", Lr)])
    model_poly.fit(np.column_stack((X, y)), Z)
    return model_poly

