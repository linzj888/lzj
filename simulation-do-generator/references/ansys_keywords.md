# ANSYS Common Keywords Reference

## Overview

This document provides reference information for common ANSYS input file keywords that are typically used as design variables in parametric studies.

## Material Properties

### MP - Define Material Property
```
MP, Lab, MAT, C0, C1, C2, C3, C4
```

Common material properties (Lab):
- `EX` - Young's Modulus (Elastic Modulus)
- `NUXY` - Poisson's Ratio (Major Poisson's Ratio)
- `DENS` - Density
- `ALPX` - Coefficient of Thermal Expansion
- `KXX` - Thermal Conductivity
- `C` - Specific Heat

Example:
```
MP, EX, 1, 210e9      ! Elastic Modulus for material 1 (210 GPa)
MP, NUXY, 1, 0.3      ! Poisson's ratio for material 1
MP, DENS, 1, 7850     ! Density for material 1 (kg/m³)
```

### TB - Define Material Data Table
```
TB, Lab, MAT, NTEMP, NPTS, TBOPT
```

Common material models (Lab):
- `BKIN` - Bilinear Kinematic Hardening
- `MISO` - Multilinear Isotropic Hardening
- `ELASTIC` - Nonlinear Elastic
- `VISCO` - Viscoelastic

## Loads and Boundary Conditions

### F - Apply Force on Nodes
```
F, NODE, Lab, VALUE, VALUE2, NEND, NINC
```

Force labels (Lab):
- `FX`, `FY`, `FZ` - Force components
- `MX`, `MY`, `MZ` - Moment components

Example:
```
F, 10, FY, -1000      ! Apply -1000 N force in Y direction on node 10
```

### D - Define Degrees of Freedom Constraints
```
D, NODE, Lab, VALUE, VALUE2, NEND, NINC, Lab2, Lab3, ...
```

Degree of freedom labels (Lab):
- `UX`, `UY`, `UZ` - Translational DOFs
- `ROTX`, `ROTY`, `ROTZ` - Rotational DOFs
- `ALL` - All DOFs

Example:
```
D, 1, ALL, 0          ! Constrain all DOFs at node 1
D, 5, UY, 0.01       ! Constrain Y displacement at node 5 to 0.01
```

### SF - Apply Surface Loads on Nodes
```
SF, Nlist, Lab, VALUE, VALUE2
```

Surface load labels (Lab):
- `PRES` - Pressure
- `CONV` - Convection coefficient
- `HFLUX` - Heat flux

Example:
```
SF, 10, PRES, 1e6     ! Apply 1 MPa pressure on node 10
```

## Geometric Parameters

### ET - Define Element Type
```
ET, ITYPE, Ename, KOP1, KOP2, KOP3, KOP4, KOP5, KOP6, INOPR
```

Example:
```
ET, 1, SOLID185       ! Define element type 1 as SOLID185
ET, 2, BEAM188        ! Define element type 2 as BEAM188
```

### R - Define Real Constants
```
R, NSET, R1, R2, R3, R4, R5, R6
```

Used for element-specific geometric properties (beam cross-section, shell thickness, etc.)

Example:
```
R, 1, 0.01, 0.01, 0.001  ! Real constants for beam: area, IYY, IZZ
```

## Analysis Parameters

### TIME - Set Time at End of Load Step
```
TIME, TIME
```

Example:
```
TIME, 1.0              ! Set time at end of load step to 1.0
```

### DELTIM - Time Step Size
```
DELTIM, DTIME, DTMIN, DTMAX, CARRY
```

Example:
```
DELTIM, 0.1, 0.01, 0.5, ON  ! Set initial time step
```

## Common Variable Categories for Parametric Studies

1. **Material Properties**
   - Elastic Modulus (EX)
   - Poisson's Ratio (NUXY)
   - Density (DENS)
   - Yield strength (via TB commands)

2. **Geometric Parameters**
   - Real constants (thickness, cross-section area)
   - Element type selections

3. **Loading Conditions**
   - Force magnitudes (F commands)
   - Pressure values (SF commands)
   - Displacement constraints (D commands)

4. **Boundary Conditions**
   - Constraint locations (node numbers in D commands)
   - Constraint magnitudes (values in D commands)

## Tips for Parametric Modeling

1. **Parameterized Input**: Use *SET commands to define parameters
   ```
   *SET, E_MOD, 210e9   ! Define parameter E_MOD
   MP, EX, 1, %E_MOD%   ! Use parameter in command
   ```

2. **APDL Commands**: Use ANSYS Parametric Design Language (APDL) for complex parameterized models

3. **Design Variables**: For optimization, use the *GET command to extract results and *SET to update parameters
