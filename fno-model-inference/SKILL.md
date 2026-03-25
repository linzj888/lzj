---
name: fno-model-inference
description: FNO (Fourier Neural Operator) 模型推理工具，支持Paraview VTU/VTP格式输出和PyVista可视化
github_url: https://github.com/yourusername/fno-model-inference
github_hash: main
version: 1.0.0
created_at: 2026-02-28
entry_point: scripts/inference.py
---

# FNO模型推理 Skill

## 概述

这个skill专门用于加载和推理FNO（Fourier Neural Operator）模型，支持：
- 加载训练好的FNO模型（.pkl格式）
- 执行模型推理
- 输出Paraview支持的VTU和VTP格式
- 使用PyVista生成高质量可视化
- 数据标准化处理

## 功能特性

1. **模型加载**：支持加载SimplifiedFNO模型
2. **数据标准化**：自动加载和应用训练时的标准化器
3. **多格式输出**：
   - NumPy格式（.npy）
   - Paraview VTU格式
   - Paraview VTP格式
4. **可视化**：使用PyVista生成2x2子图的专业科学可视化
5. **灵活的输入**：支持自定义坐标输入或使用默认坐标

## 安装依赖

```bash
pip install numpy scikit-learn joblib pyvista vtk matplotlib
```

## 使用方法

### 命令行参数

```bash
python scripts/inference.py \
  --model_path "../fno_model.pkl" \
  --scalers_path "../scalers.npz" \
  --training_data_path "../fno_training_data.npy" \
  --output_dir "." \
  --e_modulus 180000
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--model_path` | str | 必需 | FNO模型文件路径（.pkl） |
| `--scalers_path` | str | 必需 | 标准化器文件路径（.npz） |
| `--training_data_path` | str | 必需 | 训练数据文件路径（.npy） |
| `--output_dir` | str | "." | 输出目录 |
| `--e_modulus` | float | 200000 | 目标弹性模量值 |
| `--use_closest` | bool | True | 是否使用最接近的样本 |

### Python API使用

```python
from fno_inference import FNOInference

# 创建推理器
inferencer = FNOInference(
    model_path="fno_model.pkl",
    scalers_path="scalers.npz",
    training_data_path="fno_training_data.npy"
)

# 执行推理
results = inferencer.predict(e_modulus=180000)

# 保存结果
inferencer.save_results(results, output_dir=".")

# 生成可视化
inferencer.visualize(results, output_filename="visualization.png")
```

## 输出文件

运行后会生成以下文件：

| 文件名 | 格式 | 说明 |
|--------|------|------|
| `prediction_results.npy` | NumPy | 完整预测结果（包含坐标和位移） |
| `displacement_results.vtu` | VTU | Paraview UnstructuredGrid格式 |
| `displacement_results.vtp` | VTP | Paraview PolyData格式（推荐） |
| `displacement_pyvista.png` | PNG | PyVista可视化截图 |

## VTU/VTP文件数据说明

Paraview文件包含以下数据数组：

- `x_displacement`: X方向位移
- `y_displacement`: Y方向位移
- `z_displacement`: Z方向位移
- `displacement_vector`: 位移向量（3分量）
- `total_displacement`: 总位移大小

## 示例

### 快速开始

```bash
cd fno-model-inference
python scripts/inference.py \
  --model_path "../fno_model.pkl" \
  --scalers_path "../scalers.npz" \
  --training_data_path "../fno_training_data.npy"
```

### 使用自定义弹性模量

```bash
python scripts/inference.py \
  --model_path "../fno_model.pkl" \
  --scalers_path "../scalers.npz" \
  --training_data_path "../fno_training_data.npy" \
  --e_modulus 150000
```

## Paraview使用指南

1. 打开Paraview
2. 点击 `File` → `Open`
3. 选择 `displacement_results.vtp` 或 `displacement_results.vtu`
4. 点击 `Apply`
5. 在 `Properties` 面板中选择要显示的数据数组
6. 使用 `Threshold` 或 `Clip` 过滤器进行数据分析

## 注意事项

- 当前模型只使用坐标作为输入特征，不包含弹性模量
- 如需预测不同弹性模量下的位移场，需要重新训练模型
- 确保所有依赖库版本兼容
