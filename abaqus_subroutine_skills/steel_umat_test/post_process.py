#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Post-processing script for steel plasticity test
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from abaqus import *
from abaqusConstants import *

# Constants
JOB_NAME = 'steel_test'
ODB_FILE = JOB_NAME + '.odb'

# Check if ODB file exists
if not os.path.exists(ODB_FILE):
    print(f"Error: {ODB_FILE} not found!")
    exit(1)

print(f"Reading results from {ODB_FILE}...")

# Open ODB file
odb = openOdb(ODB_FILE)

# Get the last frame
assembly = odb.rootAssembly
instance = assembly.instances['Bar-1']
step = odb.steps['Tension']
last_frame = step.frames[-1]

# Get field output
field_output = last_frame.fieldOutputs['S']  # Stress
field_output_eps = last_frame.fieldOutputs['LE']  # Logarithmic strain
field_output_eqps = last_frame.fieldOutputs['PE']  # Plastic strain

# Get element set
elset = instance.elementSets['AllElements']

# Extract stress and strain data
stress_values = []
strain_values = []
plastic_strain_values = []

for element in elset.elements:
    # Get stress at integration points
    stress_data = field_output.getSubset(region=element)
    strain_data = field_output_eps.getSubset(region=element)
    plastic_strain_data = field_output_eqps.getSubset(region=element)
    
    for i, sd in enumerate(stress_data.values):
        # Get von Mises stress
        stress_values.append(sd.mises)
        
        # Get equivalent strain
        strain = strain_data.values[i]
        strain_values.append(strain.mises)
        
        # Get equivalent plastic strain
        plastic_strain = plastic_strain_data.values[i]
        plastic_strain_values.append(plastic_strain.mises)

# Calculate average values
avg_stress = np.mean(stress_values)
avg_strain = np.mean(strain_values)
avg_plastic_strain = np.mean(plastic_strain_values)

print(f"\nAverage results at final step:")
print(f"Average von Mises stress: {avg_stress:.2f} MPa")
print(f"Average von Mises strain: {avg_strain:.4f}")
print(f"Average equivalent plastic strain: {avg_plastic_strain:.4f}")

# Check if failure occurred
if avg_plastic_strain >= 0.2:
    print("\nFailure criteria reached!")
else:
    print("\nNo failure detected.")

# Create history output
print("\nCreating stress-strain curve...")

# Get history output for load end displacement and reaction force
history_region = step.historyRegions['Assembly ASSEMBLY']
disp_history = history_region.historyOutputs['U1: LoadEnd']
force_history = history_region.historyOutputs['RF1: FixedEnd']

# Extract displacement and force data
displacements = []
forces = []

for value in disp_history.values:
    displacements.append(value.data)

for value in force_history.values:
    forces.append(-value.data)  # Negative because it's reaction force

# Calculate engineering stress and strain
area = 10.0 * 10.0  # Cross-sectional area (mm²)
engineering_stress = [f / area for f in forces]
engineering_strain = [d / 100.0 for d in displacements]  # Original length = 100 mm

# Plot stress-strain curve
plt.figure(figsize=(10, 6))
plt.plot(engineering_strain, engineering_stress, 'b-', linewidth=2)
plt.xlabel('Engineering Strain')
plt.ylabel('Engineering Stress (MPa)')
plt.title('Steel Tensile Test - Stress-Strain Curve')
plt.grid(True)
plt.savefig('stress_strain_curve.png', dpi=300, bbox_inches='tight')
print("Stress-strain curve saved as 'stress_strain_curve.png'")

# Close ODB file
odb.close()

print("\nPost-processing completed successfully!")
print("Results:")
print("1. stress_strain_curve.png - Stress-strain curve")
print("2. Console output - Average stress and strain values")
