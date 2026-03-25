# scnet-connector

SSH 连接到 SCNet 超算集群。

## 用法
```bash
scnet-connect --user <用户名> --host <主机> [--port <端口>] [--key <密钥>] [--save]
```

## 示例
```bash
# 连接
scnet-connect -u scntwbdhgf -h cancon.hpccube.com -p 65023 -k ~/Downloads/key.txt

# 保存配置
scnet-connect -u scntwbdhgf -h cancon.hpccube.com -p 65023 -k ~/Downloads/key.txt --save
```

## 参数
| 参数 | 简写 | 说明 |
|------|------|------|
| --user | -u | SSH 用户名 |
| --host | -h | 登录节点地址 |
| --port | -p | SSH 端口 |
| --key | -k | 私钥文件路径 |
| --save | -s | 保存配置 |
