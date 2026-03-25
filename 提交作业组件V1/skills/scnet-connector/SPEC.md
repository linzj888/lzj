# SCNet Connector Skill Specification

## 1. Purpose
SSH connect to SCNet HPC system with customizable parameters.

## 2. Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| username | string | Yes | - | SSH username |
| hostname | string | Yes | - | Login node hostname |
| port | integer | No | 22 | SSH port |
| key_file | string | No | ~/.ssh/id_rsa | Path to private key |

## 3. Usage
```
scnet-connect --user <username> --host <hostname> [--port <port>] [--key <key_file>]
```

## 4. Configuration File
Optional config file at `~/.scnet/config.json`:
```json
{
  "username": "scntwbdhgf",
  "hostname": "cancon.hpccube.com",
  "port": 65023,
  "key_file": "~/Downloads/scntwbdhgf_cancon.hpccube.com_RsaKeyExpireTime_2026-04-16_14-17-04.txt"
}
```

## 5. Output
Establish SSH connection to SCNet HPC system.