---
name: csv-to-fno-dataset
description: Skill for processing CSV data from ABAQUS ODB files and preparing FNO model training datasets
github_url: https://github.com/yourusername/csv-to-fno-dataset
github_hash: main
version: 0.1.0
created_at: 2026-02-02T11:00:00.000Z
entry_point: scripts/process_csv.py
---

# csv-to-fno-dataset Skill

This skill processes CSV data extracted from ABAQUS ODB files and prepares standardized training datasets for Fourier Neural Operator (FNO) models.

## Overview

The skill provides functionality to:
- Load and process CSV files containing node coordinates and displacement data
- Extract elastic modulus values from filenames
- Standardize features and labels
- Reshape data into FNO model-compatible format
- Save processed datasets for model training

## Usage

### Prerequisites

Ensure the following dependencies are installed:
- numpy
- pandas
- scikit-learn

### Input Parameters

The skill accepts the following parameters:
- `data_dir`: Directory containing CSV files
- `output_dir`: Directory to save processed datasets
- `e_moduli`: List of elastic modulus values (optional, will be extracted from filenames if not provided)

### Example Usage

```bash
python scripts/process_csv.py --data_dir "D:\test\parametric_inp_fixed" --output_dir "."
```

## Implementation Details

The skill consists of the following components:
- `scripts/process_csv.py`: Main script for processing CSV data
- `scripts/create_dataset.py`: Script for creating standardized FNO datasets
- `scripts/utils.py`: Utility functions for data processing

## Output

The skill generates the following output files:
- `fno_training_data.npy`: Raw processed data
- `fno_dataset.npz`: Standardized FNO training dataset
- `scalers.npz`: Data standardization parameters
- `fno_dataset_info.txt`: Dataset information and statistics

## Data Format

### Input CSV Format

```csv
ID,Type,X,Y,Z,U
1,Node,5.2586102,-111.0,3.820604,0.0;0.0;0.0
2,Node,3.820604,-111.0,5.2586102,0.0;0.0;0.0
...
```

### Output Dataset Format

- Features: (num_samples, nodes_per_sample, 3) - Node coordinates
- Labels: (num_samples, nodes_per_sample, 3) - Displacement components
- Elastic moduli: List of elastic modulus values used
