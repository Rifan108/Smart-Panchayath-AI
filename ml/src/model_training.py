"""
Model Training and Spatial Cross-Validation Module
Executes benchmark training across LightGBM, CatBoost, XGBoost, and Random Forest
with strict GroupShuffleSplit to prevent spatial autocorrelation leakage.
"""

from ml.src.train import train_and_evaluate

if __name__ == "__main__":
    train_and_evaluate()

