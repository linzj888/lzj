#!/usr/bin/env python3
"""
SLURM Modifier - 修改 SLURM 任务脚本的节点和核心数
"""

import argparse
import re
import sys
import os

def parse_args():
    parser = argparse.ArgumentParser(description='修改 SLURM 任务脚本参数')
    parser.add_argument('input_file', help='源 SLURM 文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径（可选）')
    parser.add_argument('--nodes', '-n', required=True, help='节点数（如 4 或 2-10）')
    parser.add_argument('--cores', '-c', type=int, required=True, help='每节点核心数')
    return parser.parse_args()

def modify_slurm(content, nodes, cores):
    """修改 SLURM 内容"""
    
    # 处理节点数（可能是范围或单个值）
    if '-' in str(nodes):
        node_spec = f"-N {nodes}"
    else:
        node_spec = f"-N {nodes}"
    
    # 修改 #SBATCH -N 行
    content = re.sub(
        r'#SBATCH\s+-N\s+\S+',
        f'#SBATCH {node_spec}',
        content
    )
    
    # 修改 #SBATCH --ntasks-per-node 行
    content = re.sub(
        r'#SBATCH\s+--ntasks-per-node=\d+',
        f'#SBATCH --ntasks-per-node={cores}',
        content
    )
    
    # 如果没有 ntasks-per-node，添加它
    if '--ntasks-per-node' not in content:
        # 在第一个 #SBATCH 行后添加
        content = re.sub(
            r'(#SBATCH.*\n)',
            rf'\1#SBATCH --ntasks-per-node={cores}\n',
            content,
            count=1
        )
    
    return content

def main():
    args = parse_args()
    
    # 读取输入文件
    if not os.path.exists(args.input_file):
        print(f"错误: 文件不存在: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(args.input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改内容
    modified_content = modify_slurm(content, args.nodes, args.cores)
    
    # 确定输出文件
    output_file = args.output
    if not output_file:
        base, ext = os.path.splitext(args.input_file)
        output_file = f"{base}.mod{ext}"
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"✓ 已修改 SLURM 文件: {output_file}")
    print(f"  节点数: {args.nodes}")
    print(f"  每节点核心数: {args.cores}")
    print(f"  总核心数: {args.cores if isinstance(args.nodes, int) else '范围'}")

if __name__ == '__main__':
    main()