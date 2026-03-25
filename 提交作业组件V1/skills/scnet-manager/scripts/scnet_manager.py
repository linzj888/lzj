#!/usr/bin/env python3
"""
SCNet 统一管理工具
集成上传、下载、SLURM 创建功能
"""

import argparse
import configparser
import os
import subprocess
import sys

# 配置目录和文件
CONFIG_DIR = os.path.expanduser("~/.scnet")
CONFIG_FILE = os.path.join(CONFIG_DIR, "scnet.ini")

# 默认配置
DEFAULT_CONFIG = """# SCNet 配置文件
[server]
username = scntwbdhgf
hostname = cancon.hpccube.com
port = 65023
key_file = ~/Downloads/scntwbdhgf_cancon.hpccube.com_RsaKeyExpireTime_2026-04-16_14-17-04.txt

[paths]
remote_dir = /public/home/scntwbdhgf/apprepo/abaqus/2022-null/case
local_dir = ~/Downloads
default_slurm = ~/Downloads/abaqus.slurm

[job]
default_input = tracload2d.inp
partition = kshcnormal
"""


def load_config():
    """加载配置文件"""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return config
    return None


def save_config():
    """保存配置文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        f.write(DEFAULT_CONFIG)
    print(f"[OK] 配置文件已创建: {CONFIG_FILE}")


def cmd_init(args):
    """初始化配置"""
    if os.path.exists(CONFIG_FILE):
        print(f"配置文件已存在: {CONFIG_FILE}")
        if input("是否覆盖? (y/n): ").lower() != 'y':
            return
    save_config()


def cmd_upload(args):
    """上传文件"""
    if not args.files:
        print("[ERROR] 请指定要上传的文件")
        return
    
    files = ' '.join(args.files)
    cmd = f"scnet-upload -u -f {files}"
    subprocess.run(cmd, shell=True)


def cmd_submit(args):
    """上传并提交"""
    if not args.files:
        print("❌ 请指定要上传的文件")
        return
    
    files = ' '.join(args.files)
    slurm = args.slurm or args.files[0]
    cmd = f"scnet-upload -u -s -f {files} --slurm {slurm}"
    subprocess.run(cmd, shell=True)


def cmd_download(args):
    """下载结果"""
    if args.prefix:
        cmd = f"scnet-download -p {args.prefix}"
    elif args.files:
        files = ' '.join(args.files)
        cmd = f"scnet-download -f {files}"
    elif args.all:
        cmd = "scnet-download -a"
    else:
        print("❌ 请指定 --prefix, --files 或 --all")
        return
    
    subprocess.run(cmd, shell=True)


def cmd_create(args):
    """创建 SLURM 文件"""
    template = args.template or os.path.expanduser("~/Downloads/abaqus.slurm")
    input_file = args.input
    output = args.output or "job.slurm"
    nodes = args.nodes or 1
    cores = args.cores or 20
    partition = args.partition or "kshcnormal"
    
    if not input_file:
        print("❌ 请指定输入文件 (-i)")
        return
    
    # 使用 slurm-modifier 创建
    output_path = os.path.join(os.path.dirname(template), output)
    cmd = f"slurm-modifier {template} --output {output_path} --nodes {nodes} --cores {cores}"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] 创建失败: {result.stderr}")
        return
    
    # 修改作业名和输入文件
    try:
        with open(output_path, 'r') as f:
            content = f.read()
        
        # 修改作业名
        job_name = os.path.splitext(output)[0]
        content = content.replace("#SBATCH -J abaqus_test", f"#SBATCH -J {job_name}")
        
        # 修改输入文件
        content = content.replace("INPUT_FILE=tracload2d.inp", f"INPUT_FILE={input_file}")
        
        # 修改分区
        content = content.replace("#SBATCH -p kshdnormal", f"#SBATCH -p {partition}")
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"[OK] 已创建: {output_path}")
    except Exception as e:
        print(f"[WARN] SLURM 文件已创建，但修改失败: {e}")
        print(f"   请手动修改作业名和输入文件")


def main():
    parser = argparse.ArgumentParser(description="SCNet 统一管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init 命令
    subparsers.add_parser("init", help="初始化配置文件")
    
    # upload 命令
    upload_parser = subparsers.add_parser("upload", help="上传文件")
    upload_parser.add_argument("-f", "--files", nargs="+", help="要上传的文件")
    
    # submit 命令
    submit_parser = subparsers.add_parser("submit", help="上传并提交计算")
    submit_parser.add_argument("-f", "--files", nargs="+", help="要上传的文件")
    submit_parser.add_argument("-s", "--slurm", help="SLURM 文件名")
    
    # download 命令
    download_parser = subparsers.add_parser("download", help="下载结果")
    download_parser.add_argument("-p", "--prefix", help="文件前缀")
    download_parser.add_argument("-f", "--files", nargs="+", help="指定文件")
    download_parser.add_argument("-a", "--all", action="store_true", help="下载全部")
    
    # create 命令
    create_parser = subparsers.add_parser("create", help="创建 SLURM 文件")
    create_parser.add_argument("-t", "--template", help="模板文件")
    create_parser.add_argument("-i", "--input", help="输入文件 (.inp)")
    create_parser.add_argument("-o", "--output", help="输出文件名")
    create_parser.add_argument("-n", "--nodes", type=int, help="节点数")
    create_parser.add_argument("-c", "--cores", type=int, help="每节点核心数")
    create_parser.add_argument("-q", "--partition", help="分区")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 执行对应命令
    if args.command == "init":
        cmd_init(args)
    elif args.command == "upload":
        cmd_upload(args)
    elif args.command == "submit":
        cmd_submit(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "create":
        cmd_create(args)


if __name__ == "__main__":
    main()