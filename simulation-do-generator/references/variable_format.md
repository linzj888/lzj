# Variable Format and Identification Specification

## Overview

This document defines the format and structure for design variables in simulation input files. It serves as a reference for how variables are identified, categorized, and used in the batch generation process.

## Variable JSON Format

### Structure

Each extracted variable is represented as a JSON object with the following structure:

```json
{
  "name": "Variable_Name_X",
  "current_value": <numeric_value>,
  "description": "Human-readable description",
  "type": "material|load|boundary|geometry",
  "line_number": <integer>,
  "original_line": "Original line content from input file",
  "suggested_range": {
    "min": <minimum_value>,
    "max": <maximum_value>
  }
}
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Unique identifier for the variable | `"Material_EX_1"` |
| `current_value` | float | The current value in the input file | `210000000000.0` |
| `description` | string | Human-readable description | `"Elastic Modulus"` |
| `type` | string | Category of variable | `"material"`, `"load"`, `"boundary"`, `"geometry"` |
| `line_number` | integer | Line number in input file (1-indexed) | `45` |
| `original_line` | string | Original line content | `"MP, EX, 1, 210e9"` |
| `suggested_range.min` | float | Suggested minimum value for parametric study | `168000000000.0` |
| `suggested_range.max` | float | Suggested maximum value for parametric study | `252000000000.0` |

## Variable Types

### Material Properties

Variables related to material characteristics.

**ANSYS Keywords:**
- `MP, EX` - Young's Modulus
- `MP, NUXY` - Poisson's Ratio
- `MP, DENS` - Density
- `TB` - Material behavior (plasticity, etc.)

**ABAQUS Keywords:**
- `*Elastic` - Elastic properties
- `*Density` - Density
- `*Plastic` - Plastic properties
- `*Expansion` - Thermal expansion

**Example:**
```json
{
  "name": "Material_EX_1",
  "current_value": 210000000000.0,
  "description": "Elastic Modulus",
  "type": "material",
  "line_number": 23,
  "original_line": "MP, EX, 1, 210e9",
  "suggested_range": {
    "min": 168000000000.0,
    "max": 252000000000.0
  }
}
```

### Load Conditions

Variables related to applied loads and forces.

**ANSYS Keywords:**
- `F` - Concentrated force
- `SF` - Surface loads (pressure, etc.)
- `BF` - Body forces

**ABAQUS Keywords:**
- `*Cload` - Concentrated loads
- `*Dsload` - Distributed surface loads
- `*Dload` - Distributed body loads

**Example:**
```json
{
  "name": "Load_Force_1",
  "current_value": 1000.0,
  "description": "Applied Force",
  "type": "load",
  "line_number": 156,
  "original_line": "F, 10, FY, -1000",
  "suggested_range": {
    "min": 800.0,
    "max": 1200.0
  }
}
```

### Boundary Conditions

Variables related to constraints and boundary conditions.

**ANSYS Keywords:**
- `D` - Degree of freedom constraints
- `DK` - Keypoint constraints
- `DL` - Line constraints

**ABAQUS Keywords:**
- `*Boundary` - Boundary conditions
- `*Temperature` - Temperature constraints

**Example:**
```json
{
  "name": "Boundary_Displacement_1",
  "current_value": 0.0,
  "description": "Displacement Constraint",
  "type": "boundary",
  "line_number": 89,
  "original_line": "D, 5, UY, 0.01",
  "suggested_range": {
    "min": 0.0,
    "max": 0.02
  }
}
```

### Geometric Parameters

Variables related to geometry and dimensions.

**ANSYS Keywords:**
- `R` - Real constants (thickness, cross-section)
- `ET` - Element type (geometric implication)

**ABAQUS Keywords:**
- `*Shell Section` - Shell thickness
- `*Beam Section` - Beam cross-section
- `*Solid Section` - Material assignment (affects geometry implicitly)

**Example:**
```json
{
  "name": "Shell_Thickness_1",
  "current_value": 0.005,
  "description": "Shell Thickness",
  "type": "geometry",
  "line_number": 78,
  "original_line": "*Shell Section, elset=Shell_1, material=Aluminum\n0.005",
  "suggested_range": {
    "min": 0.003,
    "max": 0.007
  }
}
```

## Design Points CSV Format

### Structure

Design points are stored in CSV format with the following structure:

```csv
Run_ID,Variable_Name_1,Variable_Name_2,...,Variable_Name_N
Run_001,value_1_1,value_1_2,...,value_1_N
Run_002,value_2_1,value_2_2,...,value_2_N
...
Run_M,value_M_1,value_M_2,...,value_M_N
```

### Example

```csv
Run_ID,Material_EX_1,Load_Force_1,Shell_Thickness_1
Run_001,168000000000.0,800.0,0.003
Run_002,210000000000.0,1000.0,0.005
Run_003,252000000000.0,1200.0,0.007
```

### Field Descriptions

| Field | Description | Format |
|-------|-------------|--------|
| `Run_ID` | Unique identifier for each simulation run | `Run_XXX` (3-digit zero-padded) |
| `Variable_Name_*` | Column for each variable | Numeric value (float) |

## Variable Value Replacement Rules

### Numeric Values

Numeric values can be represented in multiple formats:
- Decimal: `210000000000.0`
- Scientific notation (ANSYS): `210e9`
- Scientific notation (standard): `2.10E11`

**Replacement Rule:**
When replacing numeric values, the script should:
1. Match the value format used in the original line
2. Maintain consistent precision (decimal places, significant figures)
3. Use the same notation style (decimal vs. scientific)

### String Values

String values (e.g., material names, boundary condition labels) should be replaced exactly.

## Range Calculation Rules

### Default Range Calculation

The default suggested range is calculated as:

```
min_value = current_value - (|current_value| × 0.2)
max_value = current_value + (|current_value| × 0.2)
```

This provides a ±20% variation by default.

### Type-Specific Adjustments

Some variable types require special range handling:

| Variable Type | Special Handling |
|---------------|-----------------|
| `poisson` | Constrained to [0.0, 0.5] range |
| `density` | Constrained to be ≥ 0.1 |
| `zero_based` | If current_value = 0, use [-1.0, 1.0] |
| `percentage` | Constrained to [0.0, 1.0] or [0, 100] depending on format |

## Validation Rules

### Variable Name Validation

- Must contain only alphanumeric characters and underscores
- Must not start with a number
- Must be unique within the variable set
- Recommended format: `Category_Description_Index`

### Value Validation

- Numeric values must be valid floating-point numbers
- Scientific notation must follow standard format (e.g., `1.23E-4`)
- Ranges must satisfy: `min_value < max_value`

### Range Validation

For each variable:
- `min_value` should be less than `max_value`
- `current_value` should be within `[min_value, max_value]` or close to it
- Type-specific constraints (e.g., Poisson ratio range) should be respected

## Output File Naming Convention

Generated input files follow the naming pattern:

```
input_XXX.<extension>
```

Where:
- `XXX` is a 3-digit zero-padded run number (001, 002, etc.)
- `<extension>` is the original file extension (`.dat`, `.inp`, `.txt`, etc.)

**Examples:**
- `input_001.dat`
- `input_002.inp`
- `input_150.txt`

## Error Handling

### Common Error Cases

1. **Variable Not Found in CSV**
   - Error: A design point references a variable that doesn't exist in the variable list
   - Solution: Validate variable names match before generation

2. **Line Number Out of Range**
   - Error: The specified line number exceeds the file length
   - Solution: Validate line numbers during parsing

3. **Value Replacement Failed**
   - Error: Could not locate the target value in the specified line
   - Solution: Use exact position information and fallback to pattern matching

4. **Range Constraint Violation**
   - Error: Generated design point value falls outside specified range
   - Solution: Clip values to range boundaries during generation

## Best Practices

1. **Maintain Original Format**
   - Preserve the original file's formatting and comments
   - Only modify the specific variable values

2. **Use Unique Variable Names**
   - Avoid naming conflicts by including category and index
   - Example: `Material_EX_1`, `Material_EX_2`

3. **Document Units**
   - Maintain consistent units throughout
   - Note unit systems in file headers or comments

4. **Validate Before Generation**
   - Check variable ranges are reasonable
   - Ensure design points are within feasible parameter space

5. **Version Control**
   - Keep track of template file versions
   - Document variable changes between versions
