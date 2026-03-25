#!/usr/bin/env python3
"""
Generate design of experiments (DOE) design points for simulation.

This script generates design points using various sampling methods:
- Random sampling
- Latin Hypercube Sampling (LHS)
- Uniform/Grid sampling

Usage:
    python generate_design_points.py --variables <variables_json> --method <random|lhs|uniform> --points <num_points> --output <output_csv>
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

try:
    import pyDOE as pydoe
except ImportError:
    pydoe = None
    print("Warning: pyDOE not installed. LHS method will not be available.")


class DesignPointGenerator:
    """Generate design points for design of experiments."""

    def __init__(self, variables_info: Dict[str, Any]):
        self.variables = variables_info.get('variables', [])
        self.variable_names = [var['name'] for var in self.variables]
        self.ranges = [
            (var['suggested_range']['min'], var['suggested_range']['max'])
            for var in self.variables
        ]

    def generate(self, method: str, num_points: int) -> np.ndarray:
        """Generate design points using specified method."""
        if not self.variables:
            raise ValueError("No variables specified for design point generation")

        num_vars = len(self.variables)

        if method == 'random':
            return self._random_sampling(num_points, num_vars)
        elif method == 'lhs':
            if pydoe is None:
                raise ImportError("pyDOE2 is required for LHS method")
            return self._lhs_sampling(num_points, num_vars)
        elif method == 'uniform':
            return self._uniform_sampling(num_points, num_vars)
        else:
            raise ValueError(f"Unsupported method: {method}")

    def _random_sampling(self, num_points: int, num_vars: int) -> np.ndarray:
        """Generate random sampling points."""
        points = np.random.rand(num_points, num_vars)
        return self._scale_points(points)

    def _lhs_sampling(self, num_points: int, num_vars: int) -> np.ndarray:
        """Generate Latin Hypercube Sampling points."""
        points = pydoe.lhs(num_vars, samples=num_points, criterion='maximin')
        return self._scale_points(points)

    def _uniform_sampling(self, num_points: int, num_vars: int) -> np.ndarray:
        """Generate uniform/grid sampling points."""
        # Calculate points per dimension
        points_per_dim = int(round(num_points ** (1.0 / num_vars)))
        total_points = points_per_dim ** num_vars

        # Create grid points
        grid_axes = []
        for i in range(num_vars):
            axis_values = np.linspace(0, 1, points_per_dim)
            grid_axes.append(axis_values)

        # Generate meshgrid and reshape
        mesh = np.meshgrid(*grid_axes)
        points = np.column_stack([m.flatten() for m in mesh])

        # If we have more points than requested, randomly sample
        if total_points > num_points:
            indices = np.random.choice(total_points, num_points, replace=False)
            points = points[indices]

        return self._scale_points(points)

    def _scale_points(self, points: np.ndarray) -> np.ndarray:
        """Scale points from [0,1] to actual variable ranges."""
        scaled_points = np.zeros_like(points)

        for i in range(points.shape[1]):
            min_val, max_val = self.ranges[i]
            scaled_points[:, i] = min_val + points[:, i] * (max_val - min_val)

        return scaled_points

    def save_to_csv(self, points: np.ndarray, output_file: str):
        """Save design points to CSV file."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['Run_ID'] + self.variable_names)

            # Write data
            for i, point in enumerate(points, 1):
                row = [f'Run_{i:03d}'] + list(point)
                writer.writerow(row)

        print(f"Design points saved to {output_file}")
        print(f"Total points generated: {len(points)}")
        print(f"Variables: {', '.join(self.variable_names)}")


def create_variables_config(variables: List[str], ranges: Dict[str, tuple]) -> Dict[str, Any]:
    """
    Create a variables configuration dictionary from user input.

    Args:
        variables: List of variable names
        ranges: Dictionary mapping variable names to (min, max) tuples

    Returns:
        Dictionary in the format expected by DesignPointGenerator
    """
    var_list = []

    for var_name in variables:
        min_val, max_val = ranges.get(var_name, (0.0, 1.0))

        # Calculate a reasonable current value as midpoint
        current_val = (min_val + max_val) / 2.0

        var_list.append({
            'name': var_name,
            'current_value': current_val,
            'description': f'Variable {var_name}',
            'type': 'custom',
            'suggested_range': {
                'min': float(min_val),
                'max': float(max_val)
            }
        })

    return {
        'software': 'Custom',
        'variables': var_list,
        'total_variables': len(var_list)
    }


def main():
    parser = argparse.ArgumentParser(
        description='Generate design of experiments design points'
    )
    parser.add_argument('--variables', required=True,
                        help='Variables JSON file with range definitions')
    parser.add_argument('--method', required=True,
                        choices=['random', 'lhs', 'uniform'],
                        help='Sampling method')
    parser.add_argument('--points', type=int, required=True,
                        help='Number of design points to generate')
    parser.add_argument('--output', required=True,
                        help='Output CSV file')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    args = parser.parse_args()

    # Set random seed if provided
    if args.seed:
        np.random.seed(args.seed)

    try:
        # Load variables configuration
        with open(args.variables, 'r', encoding='utf-8') as f:
            variables_info = json.load(f)

        # Generate design points
        generator = DesignPointGenerator(variables_info)
        points = generator.generate(args.method, args.points)

        # Save to CSV
        generator.save_to_csv(points, args.output)

        # Print summary
        print(f"\nSampling method: {args.method}")
        print(f"Point range summary:")
        for i, var_name in enumerate(generator.variable_names):
            print(f"  {var_name}: [{points[:, i].min():.4f}, {points[:, i].max():.4f}]")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
