# scnet-download

从 SCNet 超算集群下载计算结果文件。

## 功能
- 下载远程服务器上的计算结果文件到本地

## 预设配置
- 用户名：scntwbdhgf
- 主机：cancon.hpccube.com
- 端口：65023
- 密钥：~/Downloads/scntwbdhgf_cancon.hpccube.com_RsaKeyExpireTime_2026-04-16_14-17-04.txt
- 远程目录：/public/home/scntwbdhgf/apprepo/abaqus/2022-null/case
- 本地目录：~/Downloads

## 用法
```bash
# 下载指定前缀的所有文件（如 vshape.*, sharp.*）
scnet-download -p vshape

# 下载指定文件
scnet-download -f vshape.odb vshape.log

# 下载所有结果文件
scnet-download --all
```

## 参数
| 参数 | 简写 | 说明 |
|------|------|------|
| --prefix | -p | 按文件前缀下载（如 vshape） |
| --files | -f | 指定具体文件名（可多个） |
| --all | -a | 下载远程目录所有文件 |
| --local | -l | 指定本地保存目录（默认 ~/Downloads） |

## 示例
```bash
# 下载 vshape 开头的所有文件
scnet-download -p vshape

# 下载多个指定文件
scnet-download -f vshape.odb vshape.log vshape.dat

# 下载全部结果
scnet-download -a
```

## 依赖
预设配置已保存，无需额外配置。