# Slurm Modifier Skill Specification

## 1. Purpose
Modify SLURM job script parameters (nodes and cores per node).

## 2. Use Cases
- Adjust node count for SLURM jobs
- Modify cores per node
- Generate new SLURM files with custom configurations

## 3. Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| input_file | string | Yes | Path to source SLURM file |
| output_file | string | No | Path to output (default: add .mod suffix) |
| nodes | integer | Yes | Number of nodes (or range like 2-10) |
| cores_per_node | integer | Yes | Cores per node |

## 4. Modification Rules
- Parse #SBATCH -N lines
- Parse #SBATCH --ntasks-per-node lines
- Replace with new values
- Preserve all other content unchanged

## 5. Examples
```
# 改为 4 节点，每节点 20 核心
slurm-modifier input.slurm output.slurm --nodes 4 --cores 20

# 改为 2-10 节点范围
slurm-modifier input.slurm output.slurm --nodes 2-10
```

## 6. Output
Generate modified SLURM file with updated node/core settings.