"""
Notebook Generator for ml/notebooks/
Generates clean, valid Jupyter Notebooks (.ipynb) for the Smart Panchayat AI platform.
"""

import json
import os

NOTEBOOKS_DIR = "ml/notebooks"
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

def make_cell(cell_type: str, source: str):
    return {
        "cell_type": cell_type,
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.14.7"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

# 1. exploratory_analysis.ipynb
cells_eda = [
    make_cell("markdown", "# Exploratory Data Analysis: Smart Panchayat Socioeconomic Dynamics\n\nThis notebook analyzes the 60,000-record synthetic Panchayat dataset calibrated on official benchmarks (PAI, NITI Aayog MPI, NFHS-5, Census 2011) across **Kerala, Karnataka, Tamil Nadu, Andhra Pradesh, and Maharashtra**."),
    make_cell("code", "import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\n# Load dataset\ndf = pd.read_parquet('../datasets/synthetic/synthetic_panchayats_all_5_states.parquet')\nprint(f'Dataset Shape: {df.shape}')\ndf.head()"),
    make_cell("markdown", "## 1. Cross-State Comparative Distribution of Core Indicators"),
    make_cell("code", "fig, axes = plt.subplots(2, 2, figsize=(15, 10))\nsns.boxplot(data=df, x='state', y='poverty_rate', ax=axes[0, 0], palette='Set2')\naxes[0, 0].set_title('Multidimensional Poverty Rate by State')\naxes[0, 0].tick_params(axis='x', rotation=20)\n\nsns.boxplot(data=df, x='state', y='drinking_water_coverage', ax=axes[0, 1], palette='Set2')\naxes[0, 1].set_title('Drinking Water Tap Coverage (JJM) by State')\naxes[0, 1].tick_params(axis='x', rotation=20)\n\nsns.boxplot(data=df, x='state', y='literacy_rate', ax=axes[1, 0], palette='Set2')\naxes[1, 0].set_title('Adult Literacy Rate by State')\naxes[1, 0].tick_params(axis='x', rotation=20)\n\nsns.boxplot(data=df, x='state', y='annual_panchayat_budget_lakhs', ax=axes[1, 1], palette='Set2')\naxes[1, 1].set_title('Annual Panchayat Budget (₹ Lakhs) by State')\naxes[1, 1].tick_params(axis='x', rotation=20)\n\nplt.tight_layout()\nplt.show()"),
    make_cell("markdown", "## 2. Priority Sector Distribution Across States"),
    make_cell("code", "pd.crosstab(df['state'], df['priority_sector'], normalize='index').round(3) * 100"),
    make_cell("markdown", "## 3. Correlation Structure Among Domain Scores"),
    make_cell("code", "score_cols = [c for c in df.columns if 'score' in c]\nplt.figure(figsize=(10, 8))\nsns.heatmap(df[score_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f')\nplt.title('Correlation Matrix: Domain Scores')\nplt.show()"),
]

# 2. data_generation.ipynb
cells_gen = [
    make_cell("markdown", "# Synthetic Dataset Generation & Benchmarking Methodology\n\nThis notebook demonstrates the mathematical generation pipeline translating official government statistics into multi-tier synthetic records."),
    make_cell("code", "import sys\nsys.path.append('../src')\nfrom data_collection import STATE_BENCHMARKS, get_state_benchmark\nfrom synthetic_generator import generate_state_dataset\n\nprint('Supported States in Registry:', list(STATE_BENCHMARKS.keys()))"),
    make_cell("markdown", "## 1. Inspect Government Empirical Baseline Parameters"),
    make_cell("code", "import pandas as pd\nbench_df = pd.DataFrame(STATE_BENCHMARKS).T\nbench_df[['mpi_poverty_pct', 'literacy_rate', 'tap_water_coverage_pct', 'rural_hh_size', 'avg_annual_budget_lakhs']]"),
    make_cell("markdown", "## 2. Generate and Validate a State Dataset"),
    make_cell("code", "df_kerala = generate_state_dataset('Kerala', n_records=1000, seed=42)\nprint(f'Kerala Sample Shape: {df_kerala.shape}')\nprint(df_kerala[['population', 'poverty_rate', 'overall_development_score', 'priority_sector']].describe())"),
    make_cell("markdown", "## 3. Verify Non-Linear Target Constraints"),
    make_cell("code", "print('Priority Sector Counts in Sample:')\nprint(df_kerala['priority_sector'].value_counts())\nprint('\\nDevelopment Gap Category Counts:')\nprint(df_kerala['development_gap_category'].value_counts())"),
]

# 3. model_training.ipynb
cells_train = [
    make_cell("markdown", "# Model Selection & Multi-Architecture Benchmarking\n\nTrains and compares **CatBoost, XGBoost, LightGBM, and Random Forest** on 60,000 records with grouped leakage-free validation."),
    make_cell("code", "import sys\nsys.path.append('../src')\nimport pandas as pd\nimport numpy as np\nfrom feature_engineering import PanchayatFeatureEngineer\nfrom preprocessing import PanchayatPreprocessor, split_dataset\n\n# 1. Load Data\ndf = pd.read_parquet('../datasets/synthetic/synthetic_panchayats_all_5_states.parquet')\nfe = PanchayatFeatureEngineer()\ndf_fe = fe.transform(df)\n\n# 2. Grouped Split (Zero Leakage)\ntrain_df, test_df = split_dataset(df_fe, test_size=0.20, seed=42)\n\n# 3. Preprocessing\nprep = PanchayatPreprocessor()\nprep.fit(train_df)\nX_train = prep.transform_features(train_df)\nX_test = prep.transform_features(test_df)\n\ny_train = prep.target_encoders['priority_sector'].transform(train_df['priority_sector'])\ny_test = prep.target_encoders['priority_sector'].transform(test_df['priority_sector'])"),
    make_cell("markdown", "## 1. Train and Benchmark Classifiers"),
    make_cell("code", "import lightgbm as lgb\nimport xgboost as xgb\nfrom sklearn.ensemble import RandomForestClassifier\nimport catboost as cb\nfrom sklearn.metrics import accuracy_score, classification_report\n\nmodels = {\n    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),\n    'LightGBM': lgb.LGBMClassifier(n_estimators=150, learning_rate=0.08, random_state=42, verbose=-1),\n    'XGBoost': xgb.XGBClassifier(n_estimators=150, learning_rate=0.08, random_state=42, eval_metric='mlogloss', n_jobs=-1),\n    'CatBoost': cb.CatBoostClassifier(iterations=180, learning_rate=0.08, random_seed=42, verbose=0),\n}\n\nfor name, m in models.items():\n    m.fit(X_train, y_train)\n    preds = m.predict(X_test)\n    if hasattr(preds, 'flatten'):\n        preds = preds.flatten().astype(int)\n    acc = accuracy_score(y_test, preds)\n    print(f'{name} Test Accuracy: {acc*100:.2f}%')"),
    make_cell("markdown", "## 2. Train Clustering and Anomaly Detection"),
    make_cell("code", "from sklearn.cluster import KMeans\nfrom sklearn.ensemble import IsolationForest\n\nkmeans = KMeans(n_clusters=4, random_state=42).fit(X_train)\niso = IsolationForest(contamination=0.03, random_state=42).fit(X_train)\n\nprint('KMeans Cluster Centers Shape:', kmeans.cluster_centers_.shape)\nprint('Anomalies in Test Set:', (iso.predict(X_test) == -1).sum())"),
]

# 4. model_evaluation.ipynb
cells_eval = [
    make_cell("markdown", "# Model Evaluation, Explainability & Linear Programming Optimization\n\nEvaluates the champion models, computes SHAP feature attributions, and demonstrates Linear Programming budget optimization."),
    make_cell("code", "import sys\nsys.path.append('../src')\nfrom predict import get_inference_service\nfrom budget_optimizer import LinearBudgetOptimizer\nimport shap\nimport matplotlib.pyplot as plt\n\nservice = get_inference_service()\nprint('Inference Service Active.')"),
    make_cell("markdown", "## 1. Predict on a Test Gram Panchayat"),
    make_cell("code", "sample_gp = {\n    'state': 'Maharashtra',\n    'district': 'Nandurbar',\n    'block_taluk_mandal': 'Nandurbar Taluka 1',\n    'gram_panchayat': 'Nand_Gaon_45',\n    'population': 4200,\n    'poverty_rate': 0.32,\n    'drinking_water_coverage': 0.40,\n    'sanitation_coverage': 0.48,\n    'literacy_rate': 0.65,\n    'school_dropout_rate': 0.12,\n    'road_connectivity_rate': 0.52,\n    'child_stunting_rate': 0.44,\n    'annual_panchayat_budget_lakhs': 180.0,\n    'available_dev_funds_lakhs': 150.0\n}\n\nres = service.predict_panchayat(sample_gp)\nprint('Predicted Priority Sector:', res['predictions']['priority_sector'])\nprint('Development Gap Category:', res['predictions']['development_gap_category'])\nprint('Estimated Budget Requirement: ₹', res['predictions']['estimated_development_requirement_lakhs'], 'Lakhs')\nprint('Cluster Archetype:', res['predictions']['cluster_archetype'])"),
    make_cell("markdown", "## 2. Inspect LP Budget Optimization"),
    make_cell("code", "import pandas as pd\npd.DataFrame(res['budget_allocation']['allocations_lakhs'].items(), columns=['Sector', 'Allocation (₹ Lakhs)'])"),
    make_cell("markdown", "## 3. Audit Rationale & Top SHAP Contributors"),
    make_cell("code", "print('Audit Explanations:')\nfor exp in res['budget_allocation']['explanations']:\n    print(' -', exp)\n\nprint('\\nTop SHAP Risk Drivers:')\nfor d in res['explainability']['top_drivers']:\n    print(f' * {d[\"feature\"]}: SHAP Value {d[\"shap_value\"]}')"),
]

notebooks = {
    "exploratory_analysis.ipynb": cells_eda,
    "data_generation.ipynb": cells_gen,
    "model_training.ipynb": cells_train,
    "model_evaluation.ipynb": cells_eval,
}

for name, cells in notebooks.items():
    path = os.path.join(NOTEBOOKS_DIR, name)
    nb_json = make_notebook(cells)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb_json, f, indent=2)
    print(f"Generated {path}")

print("All notebooks created successfully!")
