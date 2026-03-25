---
name: abaqus-odb-extractor
description: 从ABAQUS仿真结果.odb文件中提取应力、应变、位移、温度等变量并保存为CSV/Excel/TXT格式；支持选择特定步骤、帧、节点集或单元集；适用于后处理分析和数据导出
dependency:
  system:
    - echo "请确保已安装ABAQUS软件并配置好环境变量"
---

# ABAQUS ODB变量提取器

## 任务目标
- 本Skill用于:从ABAQUS仿真结果的.odb文件中提取指定变量数据
- 能力包含:应力、应变、位移、温度等场变量的提取，支持多种输出格式
- 触发条件:用户需要导出ABAQUS仿真结果到外部文件进行分析时

## 前置准备
- 环境要求:
  - 需要已安装ABAQUS软件
  - 确保abaqus命令在系统PATH中
  - 确保ABAQUS Python环境可用

- 依赖说明:本Skill主要使用ABAQUS自带的odbAccess模块，无需额外安装Python包
  - 如需输出Excel格式，建议安装openpyxl（可选）:
    ```bash
    pip install openpyxl
    ```

## 操作步骤

### 1. 准备ODB文件
- 确认.odb文件路径正确
- 了解需要提取的变量代码（见下文变量列表）
- 确定需要提取的步骤和帧（可选）

### 2. 执行提取
调用 `scripts/extract_odb.py` 脚本处理ODB文件:

**基本用法:**
```bash
abaqus python scripts/extract_odb.py \
  --odb_path <odb文件路径> \
  --variables <变量代码列表> \
  --output <输出文件路径>
```

**关键参数说明:**
- `--odb_path`: ODB文件路径（必需）
- `--variables`: 变量代码列表，逗号或空格分隔（必需）
- `--output`: 输出文件路径（必需）
- `--step`: 步骤名称（可选，默认最后一个步骤）
- `--frame`: 帧索引（可选，默认最后一帧）
- `--node_set`: 节点集名称（可选，默认所有节点）
- `--element_set`: 单元集名称（可选）
- `--format`: 输出格式 csv/excel/txt（可选，自动根据扩展名判断）

### 3. 常用变量代码
以下是一些最常用的变量代码（完整列表见 [references/odb-format.md](references/odb-format.md)）:

**力学变量:**
- `S`: 应力张量
- `E`: 应变张量
- `U`: 位移
- `PE`: 塑性应变
- `PEEQ`: 等效塑性应变
- `RF`: 反作用力

**热学变量:**
- `NT`: 节点温度
- `TEMP`: 温度

**接触变量:**
- `CPRESS`: 接触压力
- `COPEN`: 接触开合量

### 4. 输出文件选择
根据输出格式选择适当的文件扩展名:
- `.csv`: 通用格式，适合Excel、Python、Matlab等
- `.xlsx`: Excel格式，方便查看和编辑
- `.txt`: 纯文本格式，适合程序读取

## 资源索引
- 核心脚本: [scripts/extract_odb.py](scripts/extract_odb.py)
  - 用途:从ODB文件中提取变量并保存为指定格式
  - 参数:odb文件路径、变量列表、输出路径、步骤/帧选择、节点/单元集选择
- 变量参考: [references/odb-format.md](references/odb-format.md)
  - 何时读取:需要查找变量代码、了解变量数据类型、查看使用示例时

## 使用示例

### 示例1: 提取应力和位移数据
```bash
abaqus python scripts/extract_odb.py \
  --odb_path ./simulation_job.odb \
  --variables S,U \
  --output ./results/stress_displacement.csv
```

### 示例2: 提取特定步骤的应变数据到Excel
```bash
abaqus python scripts/extract_odb.py \
  --odb_path ./simulation_job.odb \
  --variables E,PEEQ \
  --output ./results/strain_data.xlsx \
  --step Step-2 \
  --frame 5
```

### 示例3: 提取节点集的温度数据
```bash
abaqus python scripts/extract_odb.py \
  --odb_path ./thermal_simulation.odb \
  --variables NT \
  --output ./results/temperature_set1.csv \
  --node_set SET-HOT-REGION
```

### 示例4: 提取接触压力和开合量
```bash
abaqus python scripts/extract_odb.py \
  --odb_path ./contact_analysis.odb \
  --variables CPRESS,COPEN \
  --output ./results/contact_data.txt
```

### 示例5: 提取完整的力学响应
```bash
abaqus python scripts/extract_odb.py \
  --odb_path ./full_analysis.odb \
  --variables S,E,U,PE,PEEQ,RF \
  --output ./results/complete_response.xlsx
```

## 注意事项
- **环境要求**: 必须在ABAQUS环境中运行，使用 `abaqus python` 而不是 `python` 命令
- **变量可用性**: 只有在ABAQUS中设置了输出请求的变量才能被提取
- **数据量控制**: 大型模型建议使用节点集/单元集限制提取范围，避免内存溢出
- **单位一致性**: ODB中的单位与模型定义一致，提取时需自行确认
- **多帧提取**: 如需提取多个时间帧的数据，需要多次运行脚本，每次指定不同的frame索引
- **错误处理**: 如果指定的变量或步骤不存在，脚本会输出可用的选项

## 高级用法
- **自定义节点集/单元集**: 在ABAQUS/CAE中预先定义好节点集或单元集，提取时使用 `--node_set` 或 `--element_set` 参数
- **批处理**: 可以编写shell脚本循环处理多个ODB文件或多个时间帧
- **后处理集成**: 提取的CSV/Excel文件可以方便地导入Python (pandas)、Matlab等进行进一步分析和绘图

## 故障排查
- **"无法导入abaqus模块"**: 确保使用 `abaqus python` 命令运行脚本
- **"步骤不存在"**: 使用ABAQUS/CAE查看实际的步骤名称
- **"变量不存在"**: 检查原始模型中是否设置了该变量的输出请求
- **"内存不足"**: 减少提取的变量数量或使用节点集/单元集限制范围
