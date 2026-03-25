# scnet-upload

上传文件到 SCNet 超算集群并提交 Abaqus 计算作业。

## 功能
- 功能一：上传本地文件到远程服务器目录
- 功能二：SSH 远程提交 SLURM 作业

## 预设配置
- 用户名：scntwbdhgf
- 主机：cancon.hpccube.com
- 端口：65023
- 密钥：~/Downloads/scntwbdhgf_cancon.hpccube.com_RsaKeyExpireTime_2026-04-16_14-17-04.txt
- 远程目录：/public/home/scntwbdhgf/apprepo/abaqus/2022-null/case

## 用法
```bash
# 上传文件（默认上传 abaqus.mod.slurm）
scnet-upload --upload

# 上传并提交计算（默认使用 abaqus.slurm 提交）
scnet-upload --upload --submit
```

## 参数
| 参数 | 简写 | 说明 |
|------|------|------|
| --upload | -u | 上传文件到远程目录 |
| --submit | -s | 上传后提交计算作业 |
| --files | -f | 指定要上传的文件（可多个） |
| --slurm | | 指定 SLURM 文件名（用于提交） |

## 示例
```bash
# 只上传文件（默认 abaqus.mod.slurm）
scnet-upload -u

# 上传并提交计算（默认 abaqus.slurm）
scnet-upload -u -s

# 上传指定文件
scnet-upload -u -f /home/openclaw/Downloads/sharp.slurm /home/openclaw/Downloads/vshape.inp

# 上传指定文件并提交
scnet-upload -u -s -f /home/openclaw/Downloads/sharp.slurm /home/openclaw/Downloads/vshape.inp --slurm sharp.slurm
```

## 依赖
预设配置已保存，无需额外配置。
