# slurm-modifier

修改 SLURM 任务脚本的参数（节点数和每节点核心数）。

## Usage

```
slurm-modifier <input_file> [--output <output_file>] --nodes <nodes> --cores <cores_per_node>
```

## Parameters

| 参数 | 说明 |
|------|------|
| input_file | 源 SLURM 文件路径（必需） |
| output_file | 输出文件路径（可选，默认添加 .mod 后缀） |
| nodes | 节点数，可以是单个数字或范围（如 2-10） |
| cores | 每节点核心数 |

## 示例

```bash
# 改为 4 节点，每节点 20 核心
slurm-modifier /path/to/abaqus.slurm --nodes 4 --cores 20

# 改为 4 节点，每节点 20 核心，输出到新文件
slurm-modifier /path/to/abaqus.slurm --output /path/to/abaqus.new.slurm --nodes 4 --cores 20

# 改为节点范围 2-10
slurm-modifier /path/to/abaqus.slurm --nodes 2-10 --cores 20
```

## 修改内容

- `#SBATCH -N` - 节点数
- `#SBATCH --ntasks-per-node` - 每节点任务数/核心数

其他内容保持不变。