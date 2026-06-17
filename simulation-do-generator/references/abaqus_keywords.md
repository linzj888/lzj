# ABAQUS Common Keywords Reference

## Overview

This document provides reference information for common ABAQUS input file keywords that are typically used as design variables in parametric studies.

**Note**: This skill recognizes both numeric and string values as variables. String variables (like boundary condition types ENCASTRE, PINNED, etc.) are identified with a `value_type` of "string" and include a list of valid options.

## Material Properties

### *Material - Define Material
```
*Material, name=<material_name>
```

Example:
```
*Material, name=Steel
```

### *Density - Define Material Density
```
*Density
<density_value>
```

Example:
```
*Density
7850.0
```

### *Elastic - Define Elastic Properties
```
*Elastic, type=<type_option>
<youngs_modulus>, <poisson_ratio>
```

Type options:
- `ISOTROPIC` (default) - Isotropic material
- `ORTHOTROPIC` - Orthotropic material
- `ENGINEERING CONSTANTS` - Use engineering constants

Example:
```
*Elastic
210e9, 0.3           ! Young's modulus = 210 GPa, Poisson's ratio = 0.3
```

### *Plastic - Define Plastic Properties
```
*Plastic, hardening=<hardening_type>
<yield_stress>, <plastic_strain>
...
```

Example:
```
*Plastic, hardening=ISOTROPIC
250e6, 0.0           ! Yield stress = 250 MPa, zero plastic strain
300e6, 0.1           ! Yield stress = 300 MPa at 10% plastic strain
```

### *Expansion - Define Thermal Expansion
```
*Expansion, type=<type_option>
<expansion_coefficient>
```

Example:
```
*Expansion, type=ISO
1.2e-5               ! Isotropic thermal expansion coefficient
```

## Boundary Conditions

### *Boundary - Define Boundary Conditions
```
*Boundary, op=<operation_option>
<node_set_name_or_number>, <degree_of_freedom>, <magnitude>
```

**OR (String-type boundary conditions)**:
```
*Boundary
<node_set_name>, <boundary_type>
```

Degree of freedom (DOF) codes:
- `1, 2, 3` - Translational DOFs (X, Y, Z directions)
- `4, 5, 6` - Rotational DOFs (about X, Y, Z axes)

**String-type boundary conditions** (recognized as string variables):
- `ENCASTRE` - Fully fixed (all 6 DOFs constrained)
- `PINNED` - Pinned support (translational DOFs only)
- `XSYMM` - Symmetry about X-plane
- `YSYMM` - Symmetry about Y-plane
- `ZSYMM` - Symmetry about Z-plane

Operation options:
- `MOD` (default) - Modify existing boundary conditions
- `NEW` - Remove all existing BCs on specified nodes and apply new ones

**Examples**:

Numeric boundary condition:
```
*Boundary
Fixed_Support, 1, 6  ! Constrain all 6 DOFs on node set Fixed_Support
NSet_1, 2, 2, 0.0    ! Constrain DOF 2 (Y-direction) on NSet_1 to 0.0
```

String boundary condition (ENCASTRE):
```
*Boundary
Lower_Surface, ENCASTRE  ! Fully fix Lower_Surface
```

String boundary condition (Symmetry):
```
*Boundary
Symmetry_Plane, XSYMM  ! X-direction symmetry on Symmetry_Plane
```

## Loads

### *Cload - Apply Concentrated Loads
```
*Cload, op=<operation_option>
<node_set_name_or_number>, <degree_of_freedom>, <magnitude>
```

**Format details**:
- First parameter: Node set name or number
- Second parameter: Degree of freedom (1=X, 2=Y, 3=Z, etc.)
- Third parameter: Load magnitude (positive or negative)

**Examples**:
```
*Cload
RF_Point, 1, -1500.00    ! Apply -1500 N force in X-direction on RF_Point
Point_Load, 2, -1000       ! Apply -1000 N force in Y-direction (DOF 2) on node set
```

### *Dsload - Apply Distributed Surface Loads
```
*Dsload, op=<operation_option>
<surface_name>, <load_type>, <magnitude>
```

Common load types:
- `P` - Pressure
- `SHX`, `SHY`, `SHZ` - Shell shear forces

Example:
```
*Dsload
Surf_1, P, 1e6        ! Apply 1 MPa pressure on surface Surf_1
```

### *Dload - Apply Distributed Body Loads
```
*Dload, op=<operation_option>
<element_set_name_or_number>, <load_type>, <magnitude>
```

Common load types:
- `GRAV` - Gravity
- `BX`, `BY`, `BZ` - Body forces

Example:
```
*Dload
All_Elements, GRAV, 9.81  ! Apply gravity of 9.81 m/s² on all elements
```

### *Temperature - Define Temperatures
```
*Temperature, op=<operation_option>
<node_set_name_or_number>, <temperature_value>
```

Example:
```
*Temperature
Heated_Surface, 373.15  ! Apply 373.15 K (100°C) to Heated_Surface
```

## Section Properties

### *Solid Section - Define Solid Section
```
*Solid Section, elset=<element_set_name>, material=<material_name>
```

Example:
```
*Solid Section, elset=Solid_1, material=Steel
```

### *Shell Section - Define Shell Section
```
*Shell Section, elset=<element_set_name>, material=<material_name>
<thickness>
```

Example:
```
*Shell Section, elset=Shell_1, material=Aluminum
0.005                   ! Shell thickness = 5 mm
```

### *Beam Section - Define Beam Section
```
*Beam Section, elset=<element_set_name>, material=<material_name>, section=<section_type>
<dimension_1>, <dimension_2>, ...
```

Example:
```
*Beam Section, elset=Beam_1, material=Steel, section=RECT
0.02, 0.03             ! Rectangular cross-section: 20mm x 30mm
```

## Contact Properties

### *Surface Interaction - Define Surface Interaction Properties
```
*Surface Interaction, name=<interaction_name>
*Friction
<friction_coefficient>
```

Example:
```
*Surface Interaction, name=Friction_1
*Friction
0.3                   ! Friction coefficient = 0.3
```

## Analysis Parameters

### *Step - Define Analysis Step
```
*Step, name=<step_name>, inc=<initial_increment>, nlgeom=<NLGEOM_option>
*Static
<time_period>, <initial_increment>, <min_increment>, <max_increment>
```

Example:
```
*Step, name=Step-1, nlgeom=NO
*Static
1.0, 0.01, 1e-5, 0.1  ! Total time = 1.0, initial increment = 0.01
```

## Common Variable Categories for Parametric Studies

1. **Material Properties**
   - Young's modulus (*Elastic)
   - Poisson's ratio (*Elastic)
   - Density (*Density)
   - Yield strength (*Plastic)
   - Thermal expansion coefficient (*Expansion)

2. **Geometric Parameters**
   - Shell thickness (*Shell Section)
   - Beam cross-section dimensions (*Beam Section)
   - Material assignment changes

3. **Loading Conditions**
   - Concentrated loads (*Cload)
   - Pressure loads (*Dsload)
   - Body loads (*Dload)

4. **Boundary Conditions**
   - Displacement magnitudes (*Boundary)
   - Temperature values (*Temperature)

5. **Contact Properties**
   - Friction coefficients (*Friction)
   - Contact stiffness parameters

## Tips for Parametric Modeling

1. **Parameter Sets**: Use *PARAMETER option for parametric studies
   ```
   *PARAMETER
   E_modulus=210e9
   ```
2. **Assembly Levels**: Define parameters at appropriate levels (part, assembly, or instance)
3. **Design Variables**: For optimization, use Python scripting or the ABAQUS CAE optimization module
4. **Units Consistency**: Maintain consistent units throughout the model (SI, Imperial, etc.)

## ABAQUS Units Reference

Common unit systems:

**SI Units (m-kg-s-N-Pa)**
- Length: meter (m)
- Mass: kilogram (kg)
- Time: second (s)
- Force: Newton (N)
- Stress/Pressure: Pascal (Pa)
- Energy: Joule (J)

**Typical Engineering Units (mm-tonne-s-N-MPa)**
- Length: millimeter (mm)
- Mass: tonne (t)
- Time: second (s)
- Force: Newton (N)
- Stress/Pressure: MPa
- Density: tonne/mm³
