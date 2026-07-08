"""
model.py — Modeling utilities for salary prediction.

Builds the preprocessing and model pipelines used in Notebook 3.
Models are trained on a log-transformed target, so the metric helper
converts predictions back to USD before computing errors.
"""

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def collapse_rare_categories(series: pd.Series, top_n: int, other_label: str = 'Other') -> pd.Series:
    """Keep the top_n most frequent categories and lump the rest together."""
    top = series.value_counts().nlargest(top_n).index
    return series.where(series.isin(top), other_label)


def build_preprocessor(nominal_cols: list, numeric_cols: list) -> ColumnTransformer:
    """
    One-hot encode nominal columns and scale numeric ones.
    Scaling does nothing for the tree models but helps the linear one,
    and having a single transformer keeps every pipeline identical.
    """
    return ColumnTransformer([
        ('cat', OneHotEncoder(handle_unknown='ignore'), nominal_cols),
        ('num', StandardScaler(), numeric_cols),
    ])


def build_model_pipelines(preprocessor, random_state: int = 42) -> dict:
    """Return the four model pipelines compared in the notebook."""
    estimators = {
        'Baseline (median)': DummyRegressor(strategy='median'),
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=300, random_state=random_state),
        'Gradient Boosting': GradientBoostingRegressor(random_state=random_state),
    }
    return {name: Pipeline([('pre', preprocessor), ('model', est)])
            for name, est in estimators.items()}


def regression_metrics(y_true_usd, y_pred_log) -> dict:
    """
    MAE, RMSE and R2 in dollars. Predictions come in log scale
    (the models are trained on log1p of the salary), so they are
    converted back with expm1 before comparing.
    """
    y_pred = np.expm1(y_pred_log)
    return {
        'MAE': mean_absolute_error(y_true_usd, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_true_usd, y_pred)),
        'R2': r2_score(y_true_usd, y_pred),
    }
