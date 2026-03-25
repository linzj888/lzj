#!/usr/bin/env python3
"""
Batch generate simulation input files from design points.

This script takes a template input file and generates multiple versions
with different parameter values based on design points from a CSV file.

Usage:
    python batch_generate_inputs.py --template <template_file> --design-points <design_points_csv> --output-dir <output_directory>
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
import json


class BatchInputGenerator:
    """Generate batch simulation input files from design points."""

    def __init__(self, template_file: str, design_points_csv: str, output_dir: str):
        self.template_file = Path(template_file)
        self.design_points_csv = Path(design_points_csv)
        self.output_dir = Path(output_dir)

        # Read template file
        if not self.template_file.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_file}")

        with open(self.template_file, 'r', encoding='utf-8', errors='ignore') as f:
            self.template_lines = f.readlines()

        # Read design points
        if not self.design_points_csv.exists():
            raise FileNotFoundError(f"Design points file not found: {self.design_points_csv}")

        self.design_points = self._read_design_points()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_design_points(self) -> List[Dict[str, Any]]:
        """Read design points from CSV file."""
        points = []

        with open(self.design_points_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                points.append(row)

        return points

    def generate(self):
        """Generate all input files from design points."""
        if not self.design_points:
            raise ValueError("No design points found in CSV file")

        # Get variable names (excluding Run_ID)
        variable_names = [col for col in self.design_points[0].keys() if col != 'Run_ID']

        print(f"Generating {len(self.design_points)} input files...")
        print(f"Variables: {', '.join(variable_names)}")

        generated_files = []

        for point in self.design_points:
            run_id = point['Run_ID']
            output_filename = self._generate_output_filename(run_id)
            output_path = self.output_dir / output_filename

            # Generate file content
            content = self._generate_file_content(point, variable_names)

            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(content)

            generated_files.append({
                'run_id': run_id,
                'filename': output_filename,
                'path': str(output_path),
                'parameters': {var: point[var] for var in variable_names}
            })

        print(f"\nSuccessfully generated {len(generated_files)} files")
        print(f"Output directory: {self.output_dir}")

        return generated_files

    def _generate_output_filename(self, run_id: str) -> str:
        """Generate output filename based on template extension."""
        template_ext = self.template_file.suffix

        # Clean run_id and format it
        clean_id = run_id.replace('Run_', '').replace('run_', '').zfill(3)

        return f"input_{clean_id}{template_ext}"

    def _generate_file_content(self, point: Dict[str, str], variable_names: List[str]) -> List[str]:
        """
        Generate file content by replacing variable values in template.

        This method uses a simple replacement strategy. For complex cases,
        you may need to load variable position information from a JSON file.
        """
        content = self.template_lines.copy()

        # For now, we'll try to find and replace variable values
        # This is a simplified approach - for production use, you would need
        # exact position information from the parsing step

        for var_name in variable_names:
            value = point[var_name]

            # Try to find the original value in the template
            # This is a heuristic approach - ideally, you'd have exact positions

            # For ANSYS/ABAQUS files, we look for numeric patterns
            # and try to match them with current values

            # Create patterns to search for
            numeric_patterns = self._find_numeric_patterns_in_template(content, value)

            # Replace occurrences
            if numeric_patterns:
                # Replace all occurrences (simplified - in reality you'd want
                # to be more selective based on variable context)
                for i, line in enumerate(content):
                    for pattern in numeric_patterns:
                        if pattern in line:
                            content[i] = line.replace(pattern, str(value))
                            break  # Only replace first occurrence per line

        return content

    def _find_numeric_patterns_in_template(self, content: List[str], target_value: str) -> List[str]:
        """
        Find numeric patterns in template that match or are close to target value.

        This is a simplified heuristic. In production, you'd use exact position
        information from the parsing step.
        """
        patterns = []

        try:
            target_float = float(target_value)

            # Convert to scientific notation if needed
            scientific_str = f"{target_float:.6E}".replace('+', '')

            # Common representations
            patterns.append(str(target_float))
            patterns.append(f"{target_float:.4f}")
            patterns.append(f"{target_float:.6f}")
            patterns.append(scientific_str)

        except ValueError:
            # If not a numeric value, use as-is
            patterns.append(target_value)

        return patterns


def batch_generate_with_positions(
    template_file: str,
    design_points_csv: str,
    output_dir: str,
    variables_json: str
):
    """
    Generate batch input files using exact position information.

    This is the recommended approach for production use.

    Args:
        template_file: Path to template input file
        design_points_csv: Path to design points CSV file
        output_dir: Output directory for generated files
        variables_json: Path to JSON file with variable position information
    """
    # Read template
    template_path = Path(template_file)
    with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
        template_lines = f.readlines()

    # Read variables with positions
    with open(variables_json, 'r', encoding='utf-8') as f:
        variables_info = json.load(f)

    # Read design points
    design_points_path = Path(design_points_csv)
    with open(design_points_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        design_points = list(reader)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create variable lookup
    var_lookup = {var['name']: var for var in variables_info['variables']}

    print(f"Generating {len(design_points)} input files using exact positions...")

    generated_files = []

    for point in design_points:
        run_id = point['Run_ID']
        clean_id = run_id.replace('Run_', '').replace('run_', '').zfill(3)
        output_filename = f"input_{clean_id}{template_path.suffix}"
        output_file_path = output_path / output_filename

        # Copy template
        new_lines = template_lines.copy()

        # Replace variables at exact positions
        for var_name, var_info in var_lookup.items():
            if var_name in point:
                line_num = var_info['line_number'] - 1  # Convert to 0-indexed
                new_value = point[var_name]

                if line_num < len(new_lines):
                    original_line = new_lines[line_num]
                    original_value = str(var_info['current_value'])

                    # Also try to find the scientific notation version in original_line
                    # Extract numeric value from original_line
                    import re as re_module
                    num_pattern = r'([+-]?\d*\.?\d+[eE][+-]?\d+|[+-]?\d+\.?\d*)'
                    numbers_in_line = re_module.findall(num_pattern, original_line)

                    # Find the number that matches the current_value
                    matched_number = None
                    for num in numbers_in_line:
                        try:
                            if abs(float(num) - var_info['current_value']) < 1e-6:
                                matched_number = num
                                break
                        except ValueError:
                            continue

                    # Replace value in line
                    if matched_number:
                        # Replace the matched numeric pattern
                        new_line = original_line.replace(matched_number, new_value)
                    else:
                        # Fallback: use regex with escaped value
                        escaped_value = re.escape(str(var_info['current_value']))
                        pattern = f"({escaped_value})(?=[^0-9.eE-])"
                        new_line = re.sub(pattern, new_value, original_line, count=1)

                    if new_line != original_line:
                        new_lines[line_num] = new_line
                    else:
                        # Last resort: try direct string replacement
                        new_lines[line_num] = original_line.replace(original_value, new_value)

        # Write file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        generated_files.append({
            'run_id': run_id,
            'filename': output_filename,
            'path': str(output_file_path)
        })

    print(f"Successfully generated {len(generated_files)} files")
    print(f"Output directory: {output_path}")

    return generated_files


def main():
    parser = argparse.ArgumentParser(
        description='Batch generate simulation input files from design points'
    )
    parser.add_argument('--template', required=True,
                        help='Template input file')
    parser.add_argument('--design-points', required=True,
                        help='Design points CSV file')
    parser.add_argument('--output-dir', required=True,
                        help='Output directory for generated files')
    parser.add_argument('--variables-json',
                        help='JSON file with variable position information (recommended for exact replacement)')

    args = parser.parse_args()

    try:
        if args.variables_json:
            # Use exact position-based replacement
            batch_generate_with_positions(
                args.template,
                args.design_points,
                args.output_dir,
                args.variables_json
            )
        else:
            # Use heuristic-based replacement (less accurate)
            generator = BatchInputGenerator(args.template, args.design_points, args.output_dir)
            generator.generate()

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
