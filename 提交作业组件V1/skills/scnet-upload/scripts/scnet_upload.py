#!/usr/bin/env python3
"""
SCNet 上传并提交 Abaqus 计算作业
"""

import argparse
import os
import subprocess
import sys

# 预设配置
USERNAME = "scntwbdhgf"
HOSTNAME = "cancon.hpccube.com"
PORT = 65023
KEY_FILE = "D:/skills/scnet-manager/scntwbdhgf_cancon.hpccube.com_RsaKeyExpireTime_2026-04-16_14-17-04.txt"
REMOTE_DIR = "/public/home/scntwbdhgf/apprepo/abaqus/2022-null/case"

# 默认文件
DEFAULT_LOCAL_SLURM = "/home/openclaw/Downloads/abaqus.mod.slurm"
DEFAULT_SLURM_FILE = "abaqus.slurm"


def upload_files(local_files):
    """上传文件到远程服务器"""
    print(f"[UPLOAD] 上传文件: {local_files}")
    print(f"[TARGET] 目标目录: {REMOTE_DIR}")
    
    # 确保远程目录存在
    ssh_cmd = [
        "ssh", "-p", str(PORT), "-i", KEY_FILE,
        f"{USERNAME}@{HOSTNAME}",
        f"mkdir -p {REMOTE_DIR}"
    ]
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] 创建远程目录失败: {result.stderr}")
        return False
    
    # 上传所有文件
    for local_file in local_files:
        if not os.path.exists(local_file):
            print(f"[ERROR] 文件不存在: {local_file}")
            return False
        
        scp_cmd = [
            "scp", "-P", str(PORT), "-i", KEY_FILE,
            local_file,
            f"{USERNAME}@{HOSTNAME}:{REMOTE_DIR}/"
        ]
        result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] 上传失败: {result.stderr}")
            return False
        print(f"  [OK] {os.path.basename(local_file)}")
    
    print("[OK] 全部文件上传成功!")
    return True


def submit_job(slurm_file):
    """提交 SLURM 作业"""
    print(f"[SUBMIT] 提交计算作业: {slurm_file}")
    
    ssh_cmd = [
        "ssh", "-p", str(PORT), "-i", KEY_FILE,
        f"{USERNAME}@{HOSTNAME}",
        f"cd {REMOTE_DIR} && sbatch {slurm_file}"
    ]
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] 提交失败: {result.stderr}")
        return False
    
    print(f"[OK] {result.stdout}")
    return True


def main():
    parser = argparse.ArgumentParser(description="SCNet 上传并提交 Abaqus 计算作业")
    parser.add_argument("-u", "--upload", action="store_true", help="上传文件到远程目录")
    parser.add_argument("-s", "--submit", action="store_true", help="上传后提交计算作业")
    parser.add_argument("-f", "--files", nargs="+", help="指定要上传的文件路径")
    parser.add_argument("--slurm", type=str, help="指定 SLURM 文件名（用于提交）")
    
    args = parser.parse_args()
    
    # 确定要上传的文件
    if args.files:
        local_files = args.files
    else:
        local_files = [DEFAULT_LOCAL_SLURM]
    
    # 确定 SLURM 文件名
    slurm_file = args.slurm if args.slurm else DEFAULT_SLURM_FILE
    
    # 如果没有指定参数，默认执行全部功能
    if not args.upload and not args.submit:
        args.upload = True
        args.submit = True
    
    success = True
    
    if args.upload:
        success = upload_files(local_files) and success
    
    if args.submit:
        success = submit_job(slurm_file) and success
    
    if success:
        print("\n[SUCCESS] 全部任务完成!")
        sys.exit(0)
    else:
        print("\n[ERROR] 任务失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()