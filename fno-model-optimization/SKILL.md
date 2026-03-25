---
name: fno-model-optimization
description: FNO模型优化工具，支持交互式配置和多种优化算法
github_url: https://github.com/yourusername/fno-model-optimization
github_hash: main
version: 1.0.0
created_at: 2026-03-04
entry_point: scripts/interactive_optimization.py
---

# FNO模型优化 Skill

## 概述

这个skill专门用于调用已训练好的FNO（Fourier Neural Operator）模型进行参数优化，支持：
- 交互式配置优化参数
- 多种鲁棒性优化算法（网格搜索、SciPy优化）
- 灵活的设计变量和目标函数配置
- 详细的优化历史记录和可视化
- 完整的优化报告生成

## 功能特性

1. **交互式配置**：通过对话式界面获得以下信息：
   - 待调用的已训练模型路径
   - 优化的输入变量和变量范围
   - 优化的目标函数
   - 优化算法选择

2. **多种优化算法**：
   - 网格搜索（Grid Search）- 鲁棒性强，适合全局搜索
   - SciPy L-BFGS-B - 快速局部优化
   - 支持混合策略（网格搜索+局部优化）

3. **灵活的目标函数**：
   - 最小化最大位移
   - 最小化平均位移
   - 自定义目标函数

4. **完整的输出**：
   - 优化结果报告（TXT格式）
   - 优化历史可视化（PNG格式）
   - 最优设计点的详细结果

## 安装依赖

```bash
pip install numpy scikit-learn joblib matplotlib scipy
```

## 使用方法

### 交互式使用（推荐）

```bash
python scripts/interactive_optimization.py
```

程序会通过对话方式引导您配置：
1. 模型文件路径
2. 标准化器文件路径
3. 数据集文件路径
4. 设计变量配置（名称、范围）
5. 优化目标选择
6. 优化算法选择
7. 输出目录

### 命令行参数

```bash
python scripts/optimize.py \
  --model_path "../fno_model.pkl" \
  --scalers_path "../scalers.npz" \
  --dataset_path "../fno_dataset.npz" \
  --output_dir "." \
  --var_name "e_modulus" \
  --var_min 50000 \
  --var_max 250000 \
  --objective "max_displacement" \
  --method "grid" \
  --n_points 100
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--model_path` | str | 必需 | FNO模型文件路径（.pkl） |
| `--scalers_path` | str | 必需 | 标准化器文件路径（.npz） |
| `--dataset_path` | str | 必需 | 数据集文件路径（.npz） |
| `--output_dir` | str | "." | 输出目录 |
| `--var_name` | str | "e_modulus" | 设计变量名称 |
| `--var_min` | float | 50000 | 设计变量最小值 |
| `--var_max` | float | 250000 | 设计变量最大值 |
| `--objective` | str | "max_displacement" | 优化目标（max_displacement/average_displacement） |
| `--method` | str | "grid" | 优化方法（grid/scipy） |
| `--n_points` | int | 100 | 网格搜索采样点数 |

### Python API使用

```python
from fno_optimization import FNOOptimizer

# 创建优化器
optimizer = FNOOptimizer(
    model_path="fno_model.pkl",
    scalers_path="scalers.npz",
    dataset_path="fno_dataset.npz"
)

# 配置优化
best_value, best_objective = optimizer.optimize(
    var_name="e_modulus",
    var_bounds=(50000, 250000),
    objective="max_displacement",
    method="grid",
    n_points=100
)

# 保存结果
optimizer.save_results(best_value, best_objective, output_dir=".")
optimizer.plot_optimization_history(output_dir=".")
```

## 输出文件

运行后会生成以下文件：

| 文件名 | 格式 | 说明 |
|--------|------|------|
| `optimization_results.txt` | TXT | 优化结果详细报告 |
| `optimization_history.png` | PNG | 优化历史可视化图 |

## 优化目标

### 支持的目标函数

1. **max_displacement**（默认）：最小化最大位移
   - 计算所有节点的总位移，取最大值，最小化该值

2. **average_displacement**：最小化平均位移
   - 计算所有节点的总位移，取平均值，最小化该值

### 自定义目标函数

可以通过继承`FNOOptimizer`类并重写`evaluate_objective`方法来实现自定义目标函数。

## 优化算法

### 网格搜索（Grid Search）

- **特点**：鲁棒性强，适合全局搜索
- **适用场景**：不知道最优解大致位置时
- **参数**：`n_points` - 采样点数

### SciPy L-BFGS-B

- **特点**：快速局部优化，收敛快
- **适用场景**：有较好的初始猜测时
- **参数**：`maxiter` - 最大迭代次数

## 示例

### 快速开始 - 交互式

```bash
cd fno-model-optimization
python scripts/interactive_optimization.py
```

按照提示输入：
1. 模型路径：`../fno_model.pkl`
2. 标准化器路径：`../scalers.npz`
3. 数据集路径：`../fno_dataset.npz`
4. 变量名称：`e_modulus`
5. 变量范围：`50000` 到 `250000`
6. 优化目标：`max_displacement`
7. 优化方法：`grid`
8. 采样点数：`100`

### 命令行优化

```bash
python scripts/optimize.py \
  --model_path "../fno_model.pkl" \
  --scalers_path "../scalers.npz" \
  --dataset_path "../fno_dataset.npz" \
  --var_name "e_modulus" \
  --var_min 50000 \
  --var_max 250000 \
  --objective "max_displacement" \
  --method "grid" \
  --n_points 100
```

## 注意事项

1. 确保已训练好的模型、标准化器和数据集文件路径正确
2. 设计变量范围应该合理，覆盖可能的最优解区域
3. 网格搜索的采样点数越多，结果越精确，但计算时间也越长
4. 对于单变量优化，网格搜索通常是足够鲁棒的选择
5. 优化结果的质量取决于训练模型的准确性

## 扩展功能

未来计划支持：
- 多变量优化
- 更多优化算法（贝叶斯优化、遗传算法等）
- 约束优化
- 并行计算加速
