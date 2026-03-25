# scnet-manager

SCNet 超算作业统一管理工具，集成上传、下载、SLURM 模板修改功能。

## 功能
- **init**: 初始化/更新配置文件
- **upload**: 上传文件到远程服务器
- **submit**: 上传并提交计算作业
- **download**: 下载计算结果
- **create**: 根据模板创建 SLURM 文件

## 配置文件
首次使用需运行 `scnet-manager init` 进行初始化配置。

配置文件位置：`D:\skills\scnet-manager\config.ini`

## 用法
```bash
# 初始化配置（首次使用）
scnet-manager init

# 上传文件（需先配置）
scnet-manager upload -f file1.inp file2.slurm

# 上传并提交计算
scnet-manager submit -f sharp.slurm vshape.inp --slurm sharp.slurm

# 下载结果
scnet-manager download -p vshape

# 创建 SLURM 文件
scnet-manager create -t /home/openclaw/Downloads/abaqus.slurm -i vshape.inp -o sharp.slurm -n 1 -c 20
```

## 参数

### 通用参数
| 参数 | 说明 |
|------|------|
| init | 初始化配置文件 |

### upload / submit 参数
| 参数 | 简写 | 说明 |
|------|------|------|
| --files | -f | 要上传的文件（可多个） |
| --slurm | -s | SLURM 文件名（submit 时使用） |

### download 参数
| 参数 | 简写 | 说明 |
|------|------|------|
| --prefix | -p | 文件前缀 |
| --files | -f | 指定具体文件 |
| --all | -a | 下载全部 |

### create 参数
| 参数 | 简写 | 说明 |
|------|------|------|
| --template | -t | SLURM 模板文件 |
| --input | -i | 输入文件（.inp） |
| --output | -o | 输出 SLURM 文件名 |
| --nodes | -n | 节点数 |
| --cores | -c | 每节点核心数 |
| --partition | -q | 分区（默认 kshcnormal） |

## 示例
```bash
# 首次初始化
scnet-manager init

# 创建 1 节点 20 核心的 SLURM
scnet-manager create -t abaqus.slurm -i vshape.inp -o sharp.slurm -n 1 -c 20

# 上传并提交
scnet-manager submit -f sharp.slurm vshape.inp -s sharp.slurm

# 下载结果
scnet-manager download -p vshape

# 仅上传
scnet-manager upload -f vshape.inp sharp.slurm
```

## 依赖
- scnet-upload: 上传文件
- scnet-download: 下载结果
- slurm-modifier: 创建 SLURM 文件