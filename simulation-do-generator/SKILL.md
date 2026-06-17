---
name: simulation-do-generator
description: 仿真实验设计及批量输入文件生成。支持ANSYS/ABAQUS等主流仿真软件的输入文件解析、设计变量识别（材料属性、边界条件、载荷等）、实验设计点生成（随机/拉丁超立方/平均采样）、批量生成仿真输入文件。适用于参数化分析、优化设计、敏感性研究等场景。
---

# 仿真实验设计及批量输入文件生成

## 任务目标
- 本 Skill 用于：自动读取仿真软件输入文件，识别设计变量，生成实验设计方案，批量生成仿真输入文件
- 能力包含：
  - 解析 ANSYS/ABAQUS 输入文件并提取设计变量
  - 交互式收集变量调整信息（范围、数量等）
  - 支持随机、拉丁超立方、平均三种实验设计方法
  - 批量生成带参数的仿真输入文件
- 触发条件：用户需要进行参数化仿真分析、优化设计或敏感性研究

## 前置准备
- 依赖说明：
  ```
  pyDOE2==1.2.1
  ```

## 操作步骤

### 1. 上传并解析输入文件

**步骤 1.1：文件上传**
- 智能体询问："请提供需要分析的仿真输入文件（.inp/.dat/.txt 格式）"
- 等待用户上传文件

**步骤 1.2：确认文件类型**
- 智能体询问："这是 ANSYS 还是 ABAQUS 格式的输入文件？（请输入 ansys 或 abaqus）"
- 记录用户选择的文件类型

**步骤 1.3：解析文件并识别变量**
- 调用 `scripts/parse_simulation_input.py` 解析输入文件：
  ```bash
  python scripts/parse_simulation_input.py --input <input_file> --type <ansys|abaqus>
  ```
- 解析完成后，以清晰表格形式展示识别到的所有设计变量，包括：
  - 变量名称
  - 当前值
  - 变量类型（material/load/boundary/geometry/step）
  - 值类型（numeric/string）
  - 描述
- 提供变量分类统计（材料属性 X 个、载荷 Y 个、边界条件 Z 个等）

### 2. 选择设计变量并设置参数范围

**步骤 2.1：选择需要调整的变量**
- 智能体询问："请选择需要参与 DOE 的设计变量（可输入变量编号或名称，多个变量用逗号分隔）"
- 等待用户选择变量

**步骤 2.2：设置每个变量的参数范围**
- 对每个选中的变量，智能体依次询问：
  - "变量 [变量名] 的当前值为 [当前值]，请设置调整范围："
    - "最小值："
    - "最大值："
  - 如果变量是字符串类型（如边界条件类型 ENCASTRE、PINNED 等）：
    - "变量 [变量名] 是字符串类型，可选值为：[选项列表]"
    - "请选择要使用的值（可输入多个选项用逗号分隔）"
- 智能体根据当前值提供默认范围建议（±20%）

**步骤 2.3：选择实验设计方法**
- 智能体询问："请选择实验设计方法："
  - "1. random - 随机采样"
  - "2. lhs - 拉丁超立方采样（推荐，均匀覆盖参数空间）"
  - "3. uniform - 平均/网格采样"
- 记录用户选择

**步骤 2.4：设置采样点数量**
- 智能体询问："请设置需要生成的计算点数量："
- 记录用户输入的数值
- 如果选择 uniform 方法，智能体提示："平均采样将生成 [总点数] 个点（各维度的采样点数乘积）"

### 3. 生成实验设计点

**步骤 3.1：生成设计点矩阵**
- 调用 `scripts/generate_design_points.py` 生成设计点：
  ```bash
  python scripts/generate_design_points.py --variables <variables_json> --method <method> --points <num_points> --output design_points.csv
  ```
- 参数说明：
  - `variables_json`：包含变量名称、范围等信息的 JSON 文件
  - `method`：采样方法（random/lhs/uniform）
  - `num_points`：生成的计算点数量

**步骤 3.2：展示设计点预览**
- 展示生成的 design_points.csv 文件前 5 行预览
- 显示变量名称、各设计点的参数值
- 提示："完整设计点矩阵见附件 design_points.csv"

**步骤 3.3：确认生成批量文件**
- 智能体询问："设计点已生成，是否继续批量生成仿真输入文件？（输入 yes 确认，no 返回修改）"
- 如果用户输入 "no"，返回步骤 2 修改参数
- 如果用户输入 "yes"，继续下一步

### 4. 批量生成仿真输入文件

**步骤 4.1：生成输入文件**
- 调用 `scripts/batch_generate_inputs.py` 批量生成文件：
  ```bash
  python scripts/batch_generate_inputs.py --template <template_file> --design-points design_points.csv --output-dir ./generated_inputs
  ```
- 生成的输入文件命名格式：`input_001.inp`, `input_002.inp`, ...（根据原文件扩展名）

**步骤 4.2：生成文件清单**
- 智能体生成汇总报告：
  - "✅ 已生成 [N] 个仿真输入文件"
  - "📁 文件位置：./generated_inputs/"
  - 显示文件列表及对应的关键参数值（前 3 个）

### 5. 打包输出文件

**步骤 5.1：创建压缩包**
- 调用 `scripts/package_outputs.py` 将所有生成的文件打包：
  ```bash
  python scripts/package_outputs.py --input-dir ./generated_inputs --csv design_points.csv --output simulation_inputs.zip
  ```
- 打包内容包括：
  - 所有生成的仿真输入文件（.inp 或 .dat 格式）
  - design_points.csv 文件（实验设计点矩阵）
- 智能体输出打包信息：
  - "📦 已创建压缩包：simulation_inputs.zip"
  - "📊 包含文件：[N] 个输入文件 + 1 个 CSV 文件"
  - "💾 文件大小：[X.XX] MB"

### 6. 任务完成与文件下载

**步骤 6.1：提供明确的下载链接**
- 智能体以醒目的方式提供压缩包下载链接：
  - "📥 **下载链接**：[simulation_inputs.zip](./simulation_inputs.zip)"
  - "点击上方链接下载完整的仿真输入文件包"

**步骤 6.2：压缩包内容说明**
- 智能体列出压缩包包含的文件：
  - "压缩包内容："
  - "  - design_points.csv（实验设计点矩阵）"
  - "  - input_001.inp（设计点 1 的输入文件）"
  - "  - input_002.inp（设计点 2 的输入文件）"
  - "  - ..."
  - "  - input_NNN.inp（设计点 NNN 的输入文件）"

**步骤 6.3：任务总结**
- 智能体输出任务完成总结：
  - "📊 识别变量：[N] 个（材料 X 个、载荷 Y 个、边界 Z 个、几何 A 个、步参数 B 个）"
  - "🔬 实验设计：[方法] 采样，[N] 个设计点"
  - "📁 生成文件：[N] 个仿真输入文件"
  - "📦 压缩包：simulation_inputs.zip ([X.XX] MB)"

**步骤 6.4：后续建议**
- 智能体提供后续操作建议：
  - "下载并解压 simulation_inputs.zip"
  - "可使用生成的输入文件进行批量仿真计算"
  - "建议使用脚本或作业调度系统提交批量任务"
  - "如需修改参数或重新生成，可重新执行上述步骤"

## 资源索引
- 必要脚本：
  - [scripts/parse_simulation_input.py](scripts/parse_simulation_input.py)（解析仿真输入文件，提取设计变量）
  - [scripts/generate_design_points.py](scripts/generate_design_points.py)（生成实验设计点，支持三种采样方法）
  - [scripts/batch_generate_inputs.py](scripts/batch_generate_inputs.py)（根据设计点批量生成输入文件）
  - [scripts/package_outputs.py](scripts/package_outputs.py)（打包生成的输入文件和 CSV 为 ZIP 压缩包）
- 领域参考：
  - [references/ansys_keywords.md](references/ansys_keywords.md)（ANSYS 常用关键词）
  - [references/abaqus_keywords.md](references/abaqus_keywords.md)（ABAQUS 常用关键词）
  - [references/variable_format.md](references/variable_format.md)（变量识别格式规范）

## 注意事项
- 智能体负责用户交互、参数解释、结果展示等需要理解与决策的任务
- 脚本负责文件解析、数值计算、批量生成等确定性操作
- 在关键步骤（参数确认、设计点预览）提供用户确认机会
- 拉丁超立方采样适用于多变量参数空间探索，推荐优先使用
- 批量生成前确保输出目录有足够磁盘空间

## 使用示例

### 示例1：ANSYS 参数化分析
**完整交互流程**：
1. **用户上传** `beam_model.dat` 文件
2. **智能体询问**："这是 ANSYS 还是 ABAQUS 格式的输入文件？"
   - **用户回答**："ansys"
3. **智能体展示**识别到的 5 个设计变量：
   - Material_EX_1 (210 GPa) - 弹性模量
   - Material_DENS_1 (7850) - 密度
   - Geom_Thickness_1 (0.01) - 厚度
   - Load_Force_1 (10000) - 载荷
   - Load_Pressure_1 (1e6) - 压力
4. **智能体询问**："请选择需要参与 DOE 的设计变量"
   - **用户回答**："1, 4"（选择弹性模量和载荷）
5. **智能体询问**每个变量的范围：
   - **Material_EX_1**：最小值 "200000"，最大值 "250000"
   - **Load_Force_1**：最小值 "8000"，最大值 "15000"
6. **智能体询问**："请选择实验设计方法（1.random/2.lhs/3.uniform）"
   - **用户回答**："2"（拉丁超立方采样）
7. **智能体询问**："请设置需要生成的计算点数量"
   - **用户回答**："10"
8. **智能体展示**设计点预览（前 5 行），询问是否继续
   - **用户回答**："yes"
9. **智能体生成** 10 个 ANSYS 输入文件和 design_points.csv
10. **智能体提供**文件下载链接，任务完成

### 示例2：ABAQUS 优化设计
**完整交互流程**：
1. **用户上传** `plate_model.inp` 文件
2. **智能体询问**："这是 ANSYS 还是 ABAQUS 格式的输入文件？"
   - **用户回答**："abaqus"
3. **智能体展示**识别到的 6 个设计变量：
   - Material_Density_1 (7850) - 密度
   - Material_Elastic_1 (210000000000) - 弹性模量
   - Material_Poisson_1 (0.3) - 泊松比
   - BC_Boundary_1 (ENCASTRE) - 边界条件（字符串类型）
   - Load_Cload_1 (-1500) - 集中载荷
   - Step_StaticTime_1 (1.0) - 静态步时间
4. **用户选择**变量 2, 3, 5（弹性模量、泊松比、载荷）
5. **设置范围**：
   - Material_Elastic_1: 180000-240000
   - Material_Poisson_1: 0.25-0.35
   - Load_Cload_1: -2000 到 -1000
6. **选择方法**：uniform（平均采样）
7. **设置点数**：每维度 3 个点，共 27 个设计点
8. **确认生成**，批量生成 27 个 ABAQUS 输入文件
9. **智能体提供** design_points.csv 和所有 .inp 文件的下载链接