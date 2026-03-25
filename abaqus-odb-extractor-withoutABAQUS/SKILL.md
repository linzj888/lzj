---
name: abaqus-odb-extractor
description: Extract data from Abaqus ODB simulation result files without requiring Abaqus software installation. Use when needing to read and process Abaqus simulation results, extract node coordinates, displacement, stress data, and other field outputs from .odb files.
---

# Abaqus ODB Extractor

## Overview

This skill enables extraction of data from Abaqus ODB simulation result files without requiring Abaqus software installation. It uses a Python script that calls Abaqus Python internally to read ODB files and extract relevant data.

## Quick Start

### Extracting Data from ODB Files

```bash
python scripts/extract_odb.py <odb_file> [output_csv]
```

**Example:**
```bash
python scripts/extract_odb.py "D:\test\fullworkflow\simulations\input_001.odb"
```

This will create an output CSV file with the same name as the ODB file (e.g., `input_001_data.csv`).

## How It Works

The extractor uses a two-step process:

1. **Temporary Script Creation**: Generates a temporary Abaqus Python script that contains the actual ODB reading logic
2. **Subprocess Execution**: Calls Abaqus Python to run the temporary script and extract data
3. **Result Processing**: Collects the extracted data and saves it to a CSV file

## Extracted Data

The script extracts the following data:

- **Node information**: ID, coordinates (X, Y, Z)
- **Displacement data**: U1, U2, U3 (if available)
- **Stress data**: S (if available)
- **Mises stress**: MISES (if available)

## Script Details

### `scripts/extract_odb.py`

Main extraction script that:
- Takes ODB file path as input
- Optionally accepts output CSV path
- Automatically handles temporary script creation
- Runs Abaqus Python to extract data
- Saves results to CSV format

### Key Features

- **No Abaqus Installation Required**: Uses existing Abaqus Python if available
- **Flexible Output**: Can specify custom output path or use default
- **Error Handling**: Includes timeout and exception handling
- **Data Validation**: Checks for available field outputs
- **Efficient Processing**: Uses lookup dictionaries for faster data access

## Requirements

- **Abaqus Python**: The script requires access to Abaqus Python (typically at `C:\SIMULIA\Commands\abaqus.bat`)
- **Python 3**: The main script runs in any Python 3 environment

## Usage Examples

### Basic Extraction
```bash
python scripts/extract_odb.py "path/to/simulation.odb"
```

### Specifying Output Path
```bash
python scripts/extract_odb.py "path/to/simulation.odb" "output/results.csv"
```

### Batch Processing
```bash
for file in *.odb; do
    python scripts/extract_odb.py "$file"
done
```

## Troubleshooting

### Common Issues

1. **Abaqus Python not found**: Ensure Abaqus is installed and `abaqus.bat` is in the system PATH
2. **ODB file not accessible**: Check file permissions and path
3. **Timeout errors**: For large ODB files, increase the timeout in the script
4. **No data extracted**: Check if the ODB file contains the expected field outputs

### Error Messages

- "Error: ODB file not found": Verify the file path is correct
- "Error running Abaqus Python": Check Abaqus installation and permissions
- "Process timed out": Increase timeout value in the script

## Resources

### scripts/
- `extract_odb.py`: Main extraction script

### references/
- (Optional) Add documentation on ODB file format or specific field outputs

### assets/
- (Optional) Add example ODB files or output templates
