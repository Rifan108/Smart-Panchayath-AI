"""
Synthetic Data Generation Module (Calibration Engine)
Bridges to data/generate_multi_state_dataset.py
Ensures explicit is_synthetic=True markers and adherence to NITI Aayog/Census parameters.
"""

from data.generate_multi_state_dataset import generate_multi_state_dataset, generate_ward_record

if __name__ == "__main__":
    generate_multi_state_dataset()

