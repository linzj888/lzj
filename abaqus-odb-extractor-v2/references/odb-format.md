# ABAQUS ODB文件结构与常用变量参考

## 目录
1. [ODB文件结构](#odb文件结构)
2. [常用变量代码](#常用变量代码)
3. [变量数据类型](#变量数据类型)
4. [输出格式说明](#输出格式说明)
5. [使用示例](#使用示例)

---

## ODB文件结构

### ODB文件层次结构
```
Odb
├── Steps (分析步骤)
│   └── Step (如: Step-1, Step-2)
│       └── Frames (帧/增量)
│           └── Frame (如: Increment=1, Time=0.1)
│               └── FieldOutputs (场输出变量)
│                   └── FieldOutput (如: S, E, U)
│                       └── Values (值)
│                           ├── Node (节点值)
│                           └── Element (单元值)
└── RootAssembly (根装配)
    ├── Instances (实例)
    │   └── Instance (如: PART-1-1)
    │       ├── Nodes (节点)
    │       └── Elements (单元)
    ├── NodeSets (节点集)
    └── ElementSets (单元集)
```

### 关键概念
- **Step (步骤)**: 分析步骤，如静力分析、动力分析等
- **Frame (帧)**: 每个增量或时间点
- **FieldOutput (场输出)**: 分布在模型上的变量值
- **HistoryOutput (历史输出)**: 特定位置的时间历程数据

---

## 常用变量代码

### 力学变量
| 代码 | 名称 | 描述 | 位置 |
|------|------|------|------|
| **S** | Stress | 应力张量 | 单元中心/节点 |
| **E** | Strain | 应变张量 | 单元中心/节点 |
| **PE** | Plastic Strain | 塑性应变 | 单元中心 |
| **PEEQ** | Equivalent Plastic Strain | 等效塑性应变 | 单元中心 |
| **U** | Displacement | 位移 | 节点 |
| **UR** | Rotation | 转动 | 节点 |
| **RF** | Reaction Force | 反作用力 | 节点 |
| **RM** | Reaction Moment | 反作用力矩 | 节点 |

### 热学变量
| 代码 | 名称 | 描述 | 位置 |
|------|------|------|------|
| **NT** | Nodal Temperature | 节点温度 | 节点 |
| **TEMP** | Temperature | 温度 | 单元中心/节点 |
| **HFL** | Heat Flux | 热流密度 | 单元中心 |

### 接触变量
| 代码 | 名称 | 描述 | 位置 |
|------|------|------|------|
| **CPRESS** | Contact Pressure | 接触压力 | 接触点 |
| **CSHEAR** | Contact Shear Stress | 接触剪应力 | 接触点 |
| **COPEN** | Contact Opening | 接触开合量 | 接触点 |
| **CSLIP** | Contact Slip | 接触滑移 | 接触点 |

### 能量变量
| 代码 | 名称 | 描述 |
|------|------|------|
| **ALLIE** | Internal Energy | 内能 |
| **ALLKE** | Kinetic Energy | 动能 |
| **ALLPD** | Plastic Dissipation | 塑性耗散能 |
| **ALLVD** | Viscous Dissipation | 粘性耗散能 |

### 其他常用变量
| 代码 | 名称 | 描述 |
|------|------|------|
| **SDV** | Solution Dependent Variable | 状态变量 |
| **DT** | Time increment | 时间增量 |
| **STATUS** | Element status | 单元状态（删除/激活） |

---

## 变量数据类型

### 标量 (Scalar)
- 单个数值
- 示例: PEEQ, TEMP, NT
- 表示: `value` (直接数值)

### 向量 (Vector)
- 3个分量
- 示例: U (位移), RF (反力)
- 表示: `[x, y, z]`

### 张量 (Tensor)
- 6个分量（对称张量）
- 示例: S (应力), E (应变)
- 表示: `[s11, s22, s33, s12, s13, s23]`
  - `s11, s22, s33`: 正应力/应变分量
  - `s12, s13, s23`: 剪应力/应变分量

### 主应力/应变
- 3个主值 + 3个方向余弦
- 表示较复杂，通常提取张量后计算

---

## 输出格式说明

### CSV格式
- 特点: 通用性强，可被Excel、Python、Matlab等软件读取
- 结构:
  ```
  ID,Type,X,Y,Z,S,U
  1,Node,0.0,0.0,0.0,"[1.0e6,0.0,0.0,0.0,0.0,0.0]","[0.001,0.0,0.0]"
  2,Node,1.0,0.0,0.0,"[0.9e6,0.0,0.0,0.0,0.0,0.0]","[0.0009,0.0,0.0]"
  ```

### Excel格式 (.xlsx)
- 特点: 方便查看和编辑，支持公式和图表
- 保留原始数据类型
- 适合快速可视化分析

### TXT格式
- 特点: 纯文本，格式简单
- 适合作为其他程序的输入
- 使用制表符分隔

---

## 使用示例

### 示例1: 提取应力和位移数据
```bash
abaqus python extract_odb.py \
  --odb_path job.odb \
  --variables S,U \
  --output results.csv
```

### 示例2: 提取特定步骤的应变数据
```bash
abaqus python extract_odb.py \
  --odb_path job.odb \
  --variables E,PEEQ \
  --output strain_results.xlsx \
  --step Step-2 \
  --frame 10
```

### 示例3: 提取节点集的温度
```bash
abaqus python extract_odb.py \
  --odb_path thermal_job.odb \
  --variables NT \
  --output temperature.csv \
  --node_set SET-HOT
```

### 示例4: 提取接触压力
```bash
abaqus python extract_odb.py \
  --odb_path contact_job.odb \
  --variables CPRESS,COPEN \
  --output contact.txt
```

### 示例5: 批量提取多个变量
```bash
abaqus python extract_odb.py \
  --odb_path job.odb \
  --variables S,E,U,PE,PEEQ,RF \
  --output all_results.xlsx
```

---

## 注意事项

1. **变量可用性**: 不是所有变量在所有ODB文件中都存在，取决于输出请求设置
2. **位置**: 同一个变量可能在节点和单元都有值，取决于输出设置
3. **单位**: ODB中的单位与模型定义一致，需自行确认
4. **大文件**: 大型ODB文件可能包含大量数据，建议使用节点集/单元集限制提取范围
5. **内存消耗**: 提取所有数据可能消耗大量内存，分批提取更安全

---

## 常见问题

### Q: 如何知道ODB中有哪些变量？
A: 查看ABAQUS/CAE中的结果输出设置，或在脚本中打印 `frame.fieldOutputs.keys()`

### Q: 如何提取特定节点或单元的数据？
A: 使用 `--node_set` 或 `--element_set` 参数指定节点集/单元集名称

### Q: 如何提取多个时间步的数据？
A: 需要多次调用脚本，每次指定不同的 `--frame` 索引，或者修改脚本循环处理

### Q: 提取的数据量太大怎么办？
A: 
- 使用节点集/单元集缩小范围
- 减少提取的变量数量
- 指定特定的步骤和帧

### Q: 能否提取历史输出数据？
A: 当前脚本主要处理场输出，历史输出需要使用不同的API（historyOutputs）
