---
name: abaqus-annotation-generator
description: 自动分析 Abaqus .inp 文件并生成结构化标注报告；提取计算类型、材料类型、单元类型、边界条件、载荷类型、接触信息、模型规模等关键信息；适用于有限元分析模型的快速概览和文档化
---

# Abaqus .inp 文件标注生成器

## 任务目标
- 本 Skill 用于：自动解析 Abaqus 有限元分析输入文件(.inp)，提取关键信息并生成结构化标注报告
- 能力包含：
  1. 识别计算类型（静态、动态、热分析等）
  2. 统计材料类型和属性
  3. 识别单元类型和数量
  4. 提取边界条件定义
  5. 统计载荷类型和位置
  6. 检测接触对定义
  7. 计算模型规模（节点数、单元数）
- 触发条件：用户上传 Abaqus .inp 文件并请求生成标注

## 前置准备
- 无需额外依赖（脚本仅使用 Python 标准库）

## 操作步骤
- 标准流程：
  1. **接收 .inp 文件**
     - 确认用户已上传 .inp 文件到当前目录
     - 记录文件路径（如 `./model.inp`）

  2. **调用解析脚本**
     - 执行命令：`python scripts/parse_abaqus_inp.py --input ./model.inp --output ./model_annotation.md`
     - 脚本将自动解析并提取关键信息
     - 生成 Markdown 格式的标注报告

  3. **交付结果**
     - 将生成的 .md 文件提供给用户下载
     - 如需要，可对标注内容进行补充说明

## 资源索引
- 必要脚本：见 [scripts/parse_abaqus_inp.py](scripts/parse_abaqus_inp.py)（用途：解析 .inp 文件并生成标注）
- 领域参考：见 [references/abaqus-keywords.md](references/abaqus-keywords.md)（用途：Abaqus 关键字说明，何时需要查阅特定关键字含义）

## 注意事项
- 脚本仅分析 .inp 文件中的关键字块，不进行实际的有限元计算
- 标注信息基于文件内容提取，可能不包含隐式定义的属性
- 对于复杂的参数化模型，标注可能需要人工补充
- 支持的标准关键字：*Heading, *Material, *Element, *Boundary, *Load, *Contact Pair, *Node 等

## 使用示例

### 示例 1：基本标注生成
```bash
# 用户上传了 beam_analysis.inp 文件
python scripts/parse_abaqus_inp.py --input ./beam_analysis.inp --output ./beam_analysis_annotation.md
```
输出：`beam_analysis_annotation.md` 文件，包含模型的完整标注信息

### 示例 2：批量处理多个文件
```bash
# 针对多个 .inp 文件分别生成标注
python scripts/parse_abaqus_inp.py --input ./model1.inp --output ./model1_annotation.md
python scripts/parse_abaqus_inp.py --input ./model2.inp --output ./model2_annotation.md
```

### 示例 3：仅使用默认输出路径
```bash
# 输出文件默认与输入文件同名，扩展名为 .md
python scripts/parse_abaqus_inp.py --input ./structure.inp
# 生成 ./structure.md
```
