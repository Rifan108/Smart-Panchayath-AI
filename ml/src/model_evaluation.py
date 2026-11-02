"""
Model Evaluation and Diagnostics Module
Evaluates trained models against grouped spatial holdout test sets,
generating classification reports, confusion matrices, and regression metrics.
"""

from ml.src.evaluate import evaluate_models

if __name__ == "__main__":
    evaluate_models()

