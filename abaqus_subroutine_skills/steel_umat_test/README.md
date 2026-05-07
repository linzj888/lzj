# UMAT Steel Plasticity with Failure Test Case

## 1. Test Problem Description

### Problem Statement
A simple tensile test of a steel bar to demonstrate the UMAT subroutine for plastic deformation and failure.

### Geometry
- Bar dimensions: 100 mm × 10 mm × 10 mm
- 3D solid element mesh

### Loading
- Displacement controlled tension: 5 mm displacement at one end
- Fixed boundary at the other end

### Material Properties
```
E = 210000 MPa     (Young's modulus)
ν = 0.3           (Poisson's ratio)
σ_y = 250 MPa     (Initial yield stress)
K = 500 MPa       (Hardening coefficient)
n = 0.3           (Hardening exponent)
ε_fail = 0.2       (Failure strain)
```

## 2. Files in This Directory

- `steel_plasticity_failure_umat.f` - UMAT subroutine for steel plasticity with failure
- `steel_test.inp` - Abaqus input file
- `run_test.bat` - Batch script to run the analysis
- `post_process.py` - Python script for result post-processing
- `README.md` - This documentation

## 3. How to Run

### Step 1: Compile the UMAT
```bash
abaqus make library=steel_plasticity_failure_umat.f
```

### Step 2: Run the Analysis
```bash
abaqus job=steel_test input=steel_test.inp
```

### Step 3: Post-process Results
```bash
abaqus python post_process.py
```

## 4. Expected Results

### Stress-Strain Curve
- Elastic region: Linear response up to ~250 MPa
- Plastic region: Work hardening behavior
- Failure: Sudden drop in stress at ε ≈ 0.2

### Deformation
- Uniform deformation in elastic region
- Necking in plastic region
- Complete failure at maximum strain

## 5. UMAT Features Tested

- J2 flow theory implementation
- Isotropic hardening with power law
- Failure criterion based on equivalent plastic strain
- Radial return algorithm
- Consistent tangent modulus

## 6. Troubleshooting

### Common Issues
1. **Compilation errors**: Check Fortran compiler setup
2. **Convergence issues**: Adjust material parameters or increment size
3. **No failure observed**: Increase displacement or adjust failure strain

### Recommended Parameter Ranges
- σ_y: 200-500 MPa
- K: 300-1000 MPa
- n: 0.1-0.5
- ε_fail: 0.1-0.3
