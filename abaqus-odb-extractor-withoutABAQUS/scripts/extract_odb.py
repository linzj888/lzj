#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
import csv


def extract_odb_data(odb_path, output_path):
    """Extract data from ODB file without using Abaqus library directly"""
    
    print(f"=== Extracting data from: {odb_path} ===")
    
    # Create temporary Abaqus Python script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        temp_script = f.name
        f.write("""
import sys
from odbAccess import openOdb

odb_path = sys.argv[1]
output_path = sys.argv[2]

# Open ODB
odb = openOdb(path=odb_path)

# Get last step and frame
step = odb.steps.values()[-1]
frame = step.frames[-1]
instance = odb.rootAssembly.instances.values()[0]

# Collect field outputs
field_outputs = {}
for var in ['S', 'U']:
    if var in frame.fieldOutputs.keys():
        field_outputs[var] = frame.fieldOutputs[var]

# Extract data
results = []
nodes = instance.nodes

# Create lookup dictionaries
field_lookups = {}
for var_name, field_output in field_outputs.items():
    node_value_map = {}
    for value in field_output.values:
        if hasattr(value, 'nodeLabel'):
            node_value_map[value.nodeLabel] = value
    field_lookups[var_name] = node_value_map

# Extract node data
for node in nodes:
    row = {
        'ID': node.label,
        'X': node.coordinates[0],
        'Y': node.coordinates[1],
        'Z': node.coordinates[2] if len(node.coordinates) > 2 else 0.0
    }
    
    # Add field data
    for var_name in field_outputs.keys():
        if var_name in field_lookups and node.label in field_lookups[var_name]:
            value = field_lookups[var_name][node.label]
            if isinstance(value.data, (list, tuple)):
                row[var_name] = ';'.join([str(v) for v in value.data])
            else:
                row[var_name] = value.data
            
            # Add Mises if available
            if var_name == 'S' and hasattr(value, 'mises'):
                row['MISES'] = value.mises
        else:
            row[var_name] = 'N/A'
            if var_name == 'S':
                row['MISES'] = 'N/A'
    
    results.append(row)

# Write to CSV
if results:
    fieldnames = ['ID', 'X', 'Y', 'Z']
    all_keys = set()
    for row in results:
        all_keys.update(row.keys())
    additional_keys = [k for k in all_keys if k not in ['ID', 'X', 'Y', 'Z']]
    fieldnames.extend(sorted(additional_keys))
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

odb.close()
print(f"Extracted {len(results)} records")
""")
    
    try:
        # Run the temporary script using Abaqus Python
        cmd = [r'C:\SIMULIA\Commands\abaqus.bat', 'python', temp_script, odb_path, output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("Success! Data extracted successfully.")
            print(f"Output saved to: {output_path}")
            return True
        else:
            print(f"Error running Abaqus Python: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("Error: Process timed out")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    finally:
        # Clean up temporary script
        try:
            os.unlink(temp_script)
        except:
            pass


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_odb_without_abaqus_lib.py <odb_file> [output_csv]")
        sys.exit(1)
    
    odb_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        # Default output to current directory
        base_name = os.path.splitext(os.path.basename(odb_path))[0]
        output_path = f"{base_name}_data.csv"
    
    if not os.path.exists(odb_path):
        print(f"Error: ODB file not found: {odb_path}")
        sys.exit(1)
    
    extract_odb_data(odb_path, output_path)


if __name__ == "__main__":
    main()