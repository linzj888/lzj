---
name: fno-model-training
description: Skill for training and validating Fourier Neural Operator (FNO) models for displacement field prediction
github_url: https://github.com/yourusername/fno-model-training
github_hash: main
version: 0.1.0
created_at: 2026-02-02T11:05:00.000Z
entry_point: scripts/train_model.py
---

# fno-model-training Skill

This skill trains and validates Fourier Neural Operator (FNO) models for predicting displacement fields from ABAQUS simulation data.

## Overview

The skill provides functionality to:
- Load standardized FNO training datasets
- Train FNO models (using MLPRegressor as a simplified implementation)
- Validate model performance
- Generate prediction visualizations
- Save trained models for future use

## Usage

### Prerequisites

Ensure the following dependencies are installed:
- numpy
- scikit-learn
- joblib (for model saving/loading)
- matplotlib (for visualization, optional)

### Input Parameters

The skill accepts the following parameters:
- `dataset_file`: FNO training dataset file
- `model_output`: Path to save trained model
- `hidden_layers`: Hidden layer sizes for MLPRegressor (default: [256, 128, 64])
- `max_iter`: Maximum iterations for model training (default: 2000)
- `test_split`: Test data split ratio (default: 0.2)

### Example Usage

```bash
python scripts/train_model.py --dataset_file "fno_dataset.npz" --model_output "fno_model.pkl"
```

## Implementation Details

The skill consists of the following components:
- `scripts/train_model.py`: Main script for training FNO models
- `scripts/validate_model.py`: Script for validating model performance
- `scripts/model.py`: FNO model implementation
- `scripts/utils.py`: Utility functions for model training and evaluation

## Output

The skill generates the following output files:
- `fno_model.pkl`: Trained FNO model
- `model_evaluation.txt`: Model performance evaluation
- `prediction_visualization.png`: Prediction vs actual displacement visualization (optional)

## Model Architecture

The skill implements a simplified FNO model using MLPRegressor with the following architecture:
- Input layer: 3 features (node coordinates)
- Hidden layers: Configurable (default: [256, 128, 64])
- Output layer: 3 outputs (displacement components)

## Performance Metrics

The skill evaluates model performance using the following metrics:
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)

## Example Performance

For a typical dataset with 5 elastic modulus samples:
- Training MSE: ~0.013
- Testing MSE: ~0.0078
- RMSE: ~0.088
- MAE: ~0.053

## Use Cases

This skill is suitable for:
- Predicting displacement fields for new elastic modulus values
- Accelerating parametric finite element simulations
- Reducing computational cost of design optimization
- Enabling real-time displacement predictions
