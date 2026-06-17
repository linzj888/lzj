#!/usr/bin/env python3
"""
Parse simulation input file (ANSYS/ABAQUS) and extract design variables.

This script analyzes simulation input files to identify key design variables
including material properties, boundary conditions, loads, and geometric parameters.

Usage:
    python parse_simulation_input.py --input <input_file> --type <ansys|abaqus> [--output <output_json>]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Union


class SimulationParser:
    """Base class for simulation input file parsers."""

    def __init__(self, input_file: str, software_type: str):
        self.input_file = Path(input_file)
        self.software_type = software_type.lower()
        self.variables = []
        self.file_content = None

    def parse(self) -> Dict[str, Any]:
        """Parse the input file and extract variables."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as f:
            self.file_content = f.read()

        if self.software_type == 'ansys':
            return self._parse_ansys()
        elif self.software_type == 'abaqus':
            return self._parse_abaqus()
        else:
            raise ValueError(f"Unsupported software type: {self.software_type}")

    def _parse_ansys(self) -> Dict[str, Any]:
        """Parse ANSYS input file."""
        lines = self.file_content.split('\n')

        # ANSYS keyword patterns
        patterns = {
            'material': {
                'regex': r'MP,\s*EX,\s*\d+,\s*([\d.]+E?[-+]?\d*)',
                'name_template': 'Material_EX',
                'description': 'Elastic Modulus',
                'type': 'material'
            },
            'density': {
                'regex': r'MP,\s*DENS,\s*\d+,\s*([\d.]+E?[-+]?\d*)',
                'name_template': 'Material_DENS',
                'description': 'Density',
                'type': 'material'
            },
            'force': {
                'regex': r'F,\s*[^,]+,\s*[^,]+,\s*([\d.]+E?[-+]?\d*)',
                'name_template': 'Load_Force',
                'description': 'Applied Force',
                'type': 'load'
            },
            'pressure': {
                'regex': r'SF,\s*[^,]+,\s*PRES,\s*([\d.]+E?[-+]?\d*)',
                'name_template': 'Load_Pressure',
                'description': 'Applied Pressure',
                'type': 'load'
            }
        }

        variables = []
        var_counters = {}

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('!') or line.startswith('$'):
                continue

            for var_type, pattern_info in patterns.items():
                match = re.search(pattern_info['regex'], line, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1)
                        float_value = float(value)

                        # Generate unique variable name
                        counter = var_counters.get(var_type, 1)
                        var_name = f"{pattern_info['name_template']}_{counter}"
                        var_counters[var_type] = counter + 1

                        variables.append({
                            'name': var_name,
                            'current_value': float_value,
                            'description': pattern_info['description'],
                            'type': pattern_info['type'],
                            'line_number': line_num,
                            'original_line': line,
                            'suggested_range': self._calculate_suggested_range(float_value, var_type)
                        })
                    except (ValueError, IndexError):
                        continue

        return {
            'software': 'ANSYS',
            'input_file': str(self.input_file),
            'variables': variables,
            'total_variables': len(variables)
        }

    def _parse_abaqus(self) -> Dict[str, Any]:
        """Parse ABAQUS input file with enhanced pattern recognition."""
        lines = self.file_content.split('\n')
        variables = []
        var_counters = {}
        line_num = 0

        # Track current context (e.g., within a material definition)
        current_material = None

        while line_num < len(lines):
            line = lines[line_num].strip()

            # Skip comments and empty lines
            if not line or line.startswith('**'):
                line_num += 1
                continue

            line_upper = line.upper()

            # ==================== Material Properties ====================
            if '*MATERIAL' in line_upper:
                # Extract material name
                match = re.search(r'name\s*=\s*([^,]+)', line, re.IGNORECASE)
                if match:
                    current_material = match.group(1).strip()

            elif '*DENSITY' in line_upper:
                # Extract density value from next data line
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    value = self._extract_numeric_value(lines[value_line_num])
                    if value is not None:
                        self._add_variable(
                            variables, var_counters, 'density',
                            'Material_Density', 'Density', 'material',
                            value, line_num + 1, lines[value_line_num]
                        )

            elif '*ELASTIC' in line_upper:
                # Extract elastic modulus and Poisson's ratio
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    values = self._extract_numeric_values(lines[value_line_num])
                    if len(values) >= 2:
                        # First value is Young's modulus (E)
                        self._add_variable(
                            variables, var_counters, 'elastic_modulus',
                            'Material_Elastic', 'Elastic Modulus', 'material',
                            values[0], line_num + 1, lines[value_line_num]
                        )
                        # Second value is Poisson's ratio (ν)
                        self._add_variable(
                            variables, var_counters, 'poisson',
                            'Material_Poisson', 'Poisson Ratio', 'material',
                            values[1], line_num + 1, lines[value_line_num]
                        )

            elif '*EXPANSION' in line_upper:
                # Extract thermal expansion coefficient
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    value = self._extract_numeric_value(lines[value_line_num])
                    if value is not None:
                        self._add_variable(
                            variables, var_counters, 'expansion',
                            'Material_Expansion', 'Thermal Expansion Coefficient', 'material',
                            value, line_num + 1, lines[value_line_num]
                        )

            elif '*PLASTIC' in line_upper:
                # Extract plastic yield stress
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    values = self._extract_numeric_values(lines[value_line_num])
                    if len(values) >= 1:
                        self._add_variable(
                            variables, var_counters, 'plastic_yield',
                            'Material_YieldStress', 'Yield Stress', 'material',
                            values[0], line_num + 1, lines[value_line_num]
                        )

            # ==================== Loads ====================
            elif '*CLOAD' in line_upper and 'CLOAD' not in line_upper.replace('*CLOAD', ''):
                # Concentrated load
                # Format: *Cload, op=<MOD|NEW>
                # Data line: <node_set>, <dof>, <magnitude>
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    data_line = lines[value_line_num].strip()

                    # Try to extract all parts (node_set, dof, magnitude)
                    parts = [p.strip() for p in data_line.split(',')]

                    if len(parts) >= 3:
                        # parts[0] = node_set name
                        # parts[1] = degree of freedom (1, 2, 3, etc.)
                        # parts[2] = magnitude

                        node_set = parts[0]
                        dof = parts[1]
                        magnitude_str = parts[2]

                        # Extract numeric magnitude
                        magnitude = self._extract_numeric_value(magnitude_str)
                        if magnitude is not None:
                            var_name = f'Load_Cload_{var_counters.get("cload", 1)}'
                            var_counters['cload'] = var_counters.get('cload', 1) + 1

                            variables.append({
                                'name': var_name,
                                'current_value': magnitude,
                                'value_type': 'numeric',
                                'description': f'Concentrated Load on {node_set} (DOF={dof})',
                                'type': 'load',
                                'line_number': line_num + 1,
                                'original_line': data_line,
                                'suggested_range': self._calculate_suggested_range(magnitude, 'cload')
                            })

            elif '*DSLOAD' in line_upper:
                # Distributed surface load (pressure)
                # Format: *Dsload, op=<MOD|NEW>
                # Data line: <surface_name>, <load_type>, <magnitude>
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    data_line = lines[value_line_num].strip()
                    parts = [p.strip() for p in data_line.split(',')]

                    if len(parts) >= 2:
                        surface_name = parts[0]
                        load_type = parts[1] if len(parts) > 1 else 'P'

                        # Look for magnitude
                        if len(parts) >= 3:
                            magnitude = self._extract_numeric_value(parts[2])
                            if magnitude is not None:
                                var_name = f'Load_Dsload_{var_counters.get("dsload", 1)}'
                                var_counters['dsload'] = var_counters.get('dsload', 1) + 1

                                variables.append({
                                    'name': var_name,
                                    'current_value': magnitude,
                                    'value_type': 'numeric',
                                    'description': f'Distributed Surface Load on {surface_name} (Type={load_type})',
                                    'type': 'load',
                                    'line_number': line_num + 1,
                                    'original_line': data_line,
                                    'suggested_range': self._calculate_suggested_range(magnitude, 'dsload')
                                })

            elif '*DLOAD' in line_upper and 'DSLOAD' not in line_upper:
                # Distributed body load (e.g., gravity, centrifugal)
                # Format: *Dload, op=<MOD|NEW>
                # Data line: <element_set>, <load_type>, <magnitude>
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    data_line = lines[value_line_num].strip()
                    parts = [p.strip() for p in data_line.split(',')]

                    if len(parts) >= 2:
                        element_set = parts[0]
                        load_type = parts[1]

                        if len(parts) >= 3:
                            magnitude = self._extract_numeric_value(parts[2])
                            if magnitude is not None:
                                var_name = f'Load_Dload_{var_counters.get("dload", 1)}'
                                var_counters['dload'] = var_counters.get('dload', 1) + 1

                                variables.append({
                                    'name': var_name,
                                    'current_value': magnitude,
                                    'value_type': 'numeric',
                                    'description': f'Distributed Body Load on {element_set} (Type={load_type})',
                                    'type': 'load',
                                    'line_number': line_num + 1,
                                    'original_line': data_line,
                                    'suggested_range': self._calculate_suggested_range(magnitude, 'dload')
                                })

            elif '*TEMPERATURE' in line_upper:
                # Temperature boundary condition
                # Format: *Temperature, op=<MOD|NEW>
                # Data line: <node_set>, <temperature_value>
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    data_line = lines[value_line_num].strip()
                    parts = [p.strip() for p in data_line.split(',')]

                    if len(parts) >= 2:
                        node_set = parts[0]
                        temp_value = self._extract_numeric_value(parts[1])
                        if temp_value is not None:
                            var_name = f'BC_Temperature_{var_counters.get("temperature", 1)}'
                            var_counters['temperature'] = var_counters.get('temperature', 1) + 1

                            variables.append({
                                'name': var_name,
                                'current_value': temp_value,
                                'value_type': 'numeric',
                                'description': f'Temperature Boundary Condition on {node_set}',
                                'type': 'boundary',
                                'line_number': line_num + 1,
                                'original_line': data_line,
                                'suggested_range': self._calculate_suggested_range(temp_value, 'temperature')
                            })

            # ==================== Boundary Conditions ====================
            elif '*BOUNDARY' in line_upper:
                # Displacement boundary conditions
                # Format: *Boundary, op=<MOD|NEW>
                # Data line format 1: <node_set>, <start_dof>, <end_dof>
                # Data line format 2: <node_set>, <dof>, <magnitude>
                # Data line format 3: <node_set>, <dof>, <magnitude>, <amplitude>
                # Data line format 4: <node_set>, <dof>, <magnitude>, <amplitude>, <sensitivity>

                value_line_num = self._find_next_data_line(lines, line_num + 1)
                while value_line_num is not None:
                    # Check if we've hit the next keyword before processing this data line
                    # Scan forward from current line to see if there's a keyword before the next data line
                    for check_line_num in range(line_num + 1, value_line_num):
                        if lines[check_line_num].strip().startswith('*'):
                            # Found a keyword before this data line, stop processing
                            value_line_num = None
                            break

                    if value_line_num is None:
                        break

                    data_line = lines[value_line_num].strip()

                    # Parse boundary condition line
                    parts = [p.strip() for p in data_line.split(',')]

                    if len(parts) >= 2:
                        node_set = parts[0]
                        second_part = parts[1].upper()

                        # Check for special boundary types (string values) in the second position
                        if second_part in ['ENCASTRE', 'PINNED', 'XSYMM', 'YSYMM', 'ZSYMM']:
                            var_name = f'BC_Boundary_{var_counters.get("boundary", 1)}'
                            var_counters['boundary'] = var_counters.get('boundary', 1) + 1

                            variables.append({
                                'name': var_name,
                                'current_value': second_part,
                                'value_type': 'string',
                                'description': f'Boundary Condition on {node_set} ({second_part})',
                                'type': 'boundary',
                                'line_number': line_num + 1,
                                'original_line': data_line,
                                'suggested_range': {
                                    'min': second_part,
                                    'max': second_part,
                                    'options': ['ENCASTRE', 'PINNED', 'XSYMM', 'YSYMM', 'ZSYMM']
                                }
                            })

                        # Check for special boundary types in the third position
                        elif len(parts) >= 3:
                            third_part = parts[2].upper()

                            if third_part in ['ENCASTRE', 'PINNED', 'XSYMM', 'YSYMM', 'ZSYMM']:
                                var_name = f'BC_Boundary_{var_counters.get("boundary", 1)}'
                                var_counters['boundary'] = var_counters.get('boundary', 1) + 1

                                variables.append({
                                    'name': var_name,
                                    'current_value': third_part,
                                    'value_type': 'string',
                                    'description': f'Boundary Condition on {node_set} ({third_part})',
                                    'type': 'boundary',
                                    'line_number': line_num + 1,
                                    'original_line': data_line,
                                    'suggested_range': {
                                        'min': third_part,
                                        'max': third_part,
                                        'options': ['ENCASTRE', 'PINNED', 'XSYMM', 'YSYMM', 'ZSYMM']
                                    }
                                })

                            else:
                                # Try numeric magnitude in third position
                                magnitude = self._extract_numeric_value(third_part)
                                if magnitude is not None and magnitude != 0:
                                    dof = parts[1]
                                    var_name = f'BC_Displacement_{var_counters.get("boundary_disp", 1)}'
                                    var_counters['boundary_disp'] = var_counters.get('boundary_disp', 1) + 1

                                    variables.append({
                                        'name': var_name,
                                        'current_value': magnitude,
                                        'value_type': 'numeric',
                                        'description': f'Displacement Constraint on {node_set} (DOF={dof})',
                                        'type': 'boundary',
                                        'line_number': line_num + 1,
                                        'original_line': data_line,
                                        'suggested_range': self._calculate_suggested_range(magnitude, 'boundary_disp')
                                    })

                    # Check for next boundary data line
                    value_line_num = self._find_next_data_line(lines, value_line_num + 1)

            # ==================== Section Properties (Geometric) ====================
            elif '*SHELL SECTION' in line_upper:
                # Shell thickness
                # Format: *Shell Section, elset=<name>, material=<name>
                # Data line: <thickness>
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    value = self._extract_numeric_value(lines[value_line_num])
                    if value is not None:
                        self._add_variable(
                            variables, var_counters, 'shell_thickness',
                            'Geom_ShellThickness', 'Shell Thickness', 'geometry',
                            value, line_num + 1, lines[value_line_num]
                        )

            elif '*BEAM SECTION' in line_upper:
                # Beam cross-section dimensions
                # Format: *Beam Section, elset=<name>, material=<name>, section=<type>
                # Data line: <dim1>, <dim2>, ...
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    values = self._extract_numeric_values(lines[value_line_num])
                    for i, val in enumerate(values):
                        self._add_variable(
                            variables, var_counters, f'beam_dim{i+1}',
                            f'Geom_Beam_Dim{i+1}', f'Beam Section Dimension {i+1}', 'geometry',
                            val, line_num + 1, lines[value_line_num]
                        )

            # ==================== Step Parameters ====================
            elif '*STATIC' in line_upper and 'STEP' not in line_upper:
                # Static step with time parameters
                # Extract from *Static line itself or next data line
                # Format: *Static or *Static, <time_period>, <initial_increment>, <min_increment>, <max_increment>
                # Or data line: <time_period>, <initial_increment>, <min_increment>, <max_increment>
                match = re.search(r',\s*([\d.]+E?[-+]?\d*)', line)
                if match:
                    # Time period on keyword line
                    try:
                        time_period = float(match.group(1))
                        self._add_variable(
                            variables, var_counters, 'static_time',
                            'Step_StaticTime', 'Static Step Time Period', 'step',
                            time_period, line_num + 1, line
                        )
                    except ValueError:
                        pass
                else:
                    # Time period on data line
                    value_line_num = self._find_next_data_line(lines, line_num + 1)
                    if value_line_num is not None:
                        values = self._extract_numeric_values(lines[value_line_num])
                        if len(values) >= 1:
                            self._add_variable(
                                variables, var_counters, 'static_time',
                                'Step_StaticTime', 'Static Step Time Period', 'step',
                                values[0], line_num + 1, lines[value_line_num]
                            )

            elif '*DYNAMIC' in line_upper:
                # Dynamic step parameters
                match = re.search(r',\s*([\d.]+E?[-+]?\d*)', line)
                if match:
                    try:
                        time_period = float(match.group(1))
                        self._add_variable(
                            variables, var_counters, 'dynamic_time',
                            'Step_DynamicTime', 'Dynamic Step Time Period', 'step',
                            time_period, line_num + 1, line
                        )
                    except ValueError:
                        pass

            # ==================== Initial Conditions ====================
            elif '*INITIAL CONDITIONS' in line_upper:
                if 'VELOCITY' in line_upper:
                    # Initial velocity conditions
                    # Format: *Initial Conditions, type=VELOCITY
                    # Data line: <node_set>, <dof>, <magnitude>
                    value_line_num = self._find_next_data_line(lines, line_num + 1)
                    while value_line_num is not None:
                        # Check if we've hit the next keyword before processing this data line
                        hit_keyword = False
                        for check_line_num in range(line_num + 1, value_line_num):
                            stripped_line = lines[check_line_num].strip()
                            if stripped_line.startswith('*') and not stripped_line.startswith('**'):
                                # 只把非注释的关键字行算命中
                                hit_keyword = True
                                break
                        if hit_keyword:
                            break

                        data_line = lines[value_line_num].strip()
                        parts = [p.strip() for p in data_line.split(',')]

                        if len(parts) >= 3:
                            node_set = parts[0]
                            dof = parts[1]
                            magnitude = self._extract_numeric_value(parts[2])

                            if magnitude is not None:
                                dof_names = ['X', 'Y', 'Z', 'RX', 'RY', 'RZ']
                                dof_label = dof_names[int(dof) - 1] if dof.isdigit() and 1 <= int(dof) <= 6 else dof

                                var_name = f'Init_Velocity_{dof_label}_{var_counters.get("init_velocity", 1)}'
                                var_counters['init_velocity'] = var_counters.get('init_velocity', 1) + 1

                                variables.append({
                                    'name': var_name,
                                    'current_value': magnitude,
                                    'value_type': 'numeric',
                                    'description': f'Initial {dof_label} Velocity on {node_set}',
                                    'type': 'initial',
                                    'line_number': line_num + 1,
                                    'original_line': data_line,
                                    'suggested_range': self._calculate_suggested_range(magnitude, 'velocity')
                                })

                        # Check for next velocity data line
                        value_line_num = self._find_next_data_line(lines, value_line_num + 1)

            elif '*VISCO' in line_upper and 'STEP' in line_upper:
                # Visco step parameters
                value_line_num = self._find_next_data_line(lines, line_num + 1)
                if value_line_num is not None:
                    values = self._extract_numeric_values(lines[value_line_num])
                    if len(values) >= 1:
                        self._add_variable(
                            variables, var_counters, 'visco_time',
                            'Step_ViscoTime', 'Visco Step Time Period', 'step',
                            values[0], line_num + 1, lines[value_line_num]
                        )

            # ==================== Contact Properties ====================
            elif '*SURFACE INTERACTION' in line_upper:
                # Check for friction coefficient in following lines
                if line_num + 1 < len(lines) and '*FRICTION' in lines[line_num + 1].upper():
                    value_line_num = self._find_next_data_line(lines, line_num + 2)
                    if value_line_num is not None:
                        value = self._extract_numeric_value(lines[value_line_num])
                        if value is not None:
                            self._add_variable(
                                variables, var_counters, 'friction',
                                'Contact_Friction', 'Friction Coefficient', 'contact',
                                value, line_num + 2, lines[value_line_num]
                            )

            line_num += 1

        return {
            'software': 'ABAQUS',
            'input_file': str(self.input_file),
            'variables': variables,
            'total_variables': len(variables)
        }

    def _find_next_data_line(self, lines: List[str], start_line: int) -> int:
        """
        Find the next line that contains data (not a keyword or comment).
        Returns line number or None if not found.
        """
        for i in range(start_line, len(lines)):
            line = lines[i].strip()
            if line and not line.startswith('*') and not line.startswith('**'):
                return i
        return None

    def _extract_numeric_value(self, line: str) -> float:
        """Extract the first numeric value from a line."""
        match = re.search(r'[+-]?\d*\.?\d+(?:[eE][+-]?\d+)?', line)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
        return None

    def _extract_numeric_values(self, line: str) -> List[float]:
        """Extract all numeric values from a line."""
        values = []
        for match in re.finditer(r'[+-]?\d*\.?\d+(?:[eE][+-]?\d+)?', line):
            try:
                values.append(float(match.group()))
            except ValueError:
                pass
        return values

    def _add_variable(self, variables: List[Dict], var_counters: Dict[str, int],
                      var_type: str, name_template: str, description: str,
                      var_category: str, value: float, line_num: int, original_line: str):
        """Helper to add a variable to the list."""
        try:
            counter = var_counters.get(var_type, 1)
            var_name = f"{name_template}_{counter}"
            var_counters[var_type] = counter + 1

            variables.append({
                'name': var_name,
                'current_value': value,
                'value_type': 'numeric',
                'description': description,
                'type': var_category,
                'line_number': line_num,
                'original_line': original_line,
                'suggested_range': self._calculate_suggested_range(value, var_type)
            })
        except (ValueError, IndexError):
            pass

    def _calculate_suggested_range(self, current_value: Union[float, str], var_type: str) -> Dict[str, Any]:
        """Calculate suggested range for a variable based on its type."""
        # Handle string values
        if isinstance(current_value, str):
            return {
                'min': current_value,
                'max': current_value,
                'options': [current_value]
            }

        if current_value == 0:
            return {'min': -1.0, 'max': 1.0}

        # Default: ±20% variation
        delta = abs(current_value) * 0.2

        # Adjust based on variable type
        if var_type in ['poisson', 'friction']:
            # Poisson ratio and friction coefficient typically 0.0-0.5 (or 0.0-1.0 for friction)
            return {'min': max(0.0, current_value - 0.1), 'max': min(0.5 if var_type == 'poisson' else 1.0, current_value + 0.1)}
        elif var_type in ['density']:
            # Density shouldn't be negative
            return {'min': max(0.1, current_value - delta), 'max': current_value + delta}
        elif var_type in ['expansion']:
            # Expansion coefficient is typically small
            return {'min': max(0.0, current_value - delta), 'max': current_value + delta}
        elif var_type in ['temperature']:
            # Temperature in Kelvin, reasonable range
            return {'min': max(273.15, current_value - 50), 'max': current_value + 50}
        elif 'time' in var_type:
            # Time periods
            return {'min': max(0.1, current_value - delta), 'max': current_value + delta}
        elif var_type in ['shell_thickness', 'beam_dim1', 'beam_dim2', 'beam_dim3']:
            # Geometric dimensions
            return {'min': max(0.001, current_value - delta), 'max': current_value + delta}
        elif 'velocity' in var_type:
            # Velocity parameters, allow ±30% variation
            delta_vel = abs(current_value) * 0.3
            return {'min': current_value - delta_vel, 'max': current_value + delta_vel}
        else:
            return {'min': current_value - delta, 'max': current_value + delta}


def main():
    parser = argparse.ArgumentParser(
        description='Parse simulation input file and extract design variables'
    )
    parser.add_argument('--input', required=True, help='Path to input file')
    parser.add_argument('--type', required=True,
                        choices=['ansys', 'abaqus'],
                        help='Software type')
    parser.add_argument('--output', help='Output JSON file (default: stdout)')

    args = parser.parse_args()

    try:
        parser_obj = SimulationParser(args.input, args.type)
        result = parser_obj.parse()

        output_json = json.dumps(result, indent=2)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"Variables extracted and saved to {args.output}")
        else:
            print(output_json)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
