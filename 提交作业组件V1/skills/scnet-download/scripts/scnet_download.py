#!/usr/bin/env python3
"""
SCNet 下载计算结果文件
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
DEFAULT_LOCAL_DIR = "D:/skills/scnet-manager"


def list_remote_files(pattern=None):
    """列出远程文件"""
    if pattern:
        ssh_cmd = [
            "ssh", "-p", str(PORT), "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-i", KEY_FILE,
            f"{USERNAME}@{HOSTNAME}",
            f"ls -1 {REMOTE_DIR}/{pattern}*"
        ]
    else:
        ssh_cmd = [
            "ssh", "-p", str(PORT), "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-i", KEY_FILE,
            f"{USERNAME}@{HOSTNAME}",
            f"ls -1 {REMOTE_DIR}"
        ]
    
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    
    files = [os.path.basename(f) for f in result.stdout.strip().split('\n') if f]
    return files


def download_files(file_list, local_dir):
    """下载文件到本地"""
    if not file_list:
        print("[ERROR] 没有文件可下载")
        return False
    
    print(f"[DOWNLOAD] 下载文件到: {local_dir}")
    
    for filename in file_list:
        remote_path = f"{REMOTE_DIR}/{filename}"
        local_path = os.path.join(local_dir, filename)
        
        scp_cmd = [
            "scp", "-P", str(PORT), "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-i", KEY_FILE,
            f"{USERNAME}@{HOSTNAME}:{remote_path}",
            local_path
        ]
        result = subprocess.run(scp_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  [ERROR] {filename}: {result.stderr}")
        else:
            print(f"  [OK] {filename}")
    
    print("[OK] 下载完成!")
    return True


def main():
    parser = argparse.ArgumentParser(description="SCNet 下载计算结果文件")
    parser.add_argument("-p", "--prefix", type=str, help="按文件前缀下载（如 vshape）")
    parser.add_argument("-f", "--files", nargs="+", help="指定具体文件名（可多个）")
    parser.add_argument("-a", "--all", action="store_true", help="下载远程目录所有文件")
    parser.add_argument("-l", "--local", type=str, default=DEFAULT_LOCAL_DIR, help="本地保存目录")
    
    args = parser.parse_args()
    
    # 确定要下载的文件
    file_list = []
    
    if args.prefix:
        file_list = list_remote_files(args.prefix)
    elif args.files:
        file_list = args.files
    elif args.all:
        file_list = list_remote_files()
    else:
        print("请指定 --prefix, --files 或 --all")
        sys.exit(1)
    
    if not file_list:
        print("[ERROR] 没有找到可下载的文件")
        sys.exit(1)
    
    # 执行下载
    success = download_files(file_list, args.local)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()