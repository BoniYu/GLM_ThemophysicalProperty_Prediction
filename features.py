import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
# If the class stays defined in the notebook, the saved file refers to __main__.log_feature

class log_feature(BaseEstimator, TransformerMixin):
    """Turn a pressure column P into two columns: [P, ln(P)]."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.hstack((X, np.log(X)))