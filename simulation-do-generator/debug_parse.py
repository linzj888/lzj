#!/usr/bin/env python3
# 调试脚本：查看解析过程
import sys
sys.path.insert(0, 'scripts')
from parse_simulation_input import SimulationParser
import json

inp_file = r'D:\temp\tennis\tennis_surfcav.inp'

print(f"正在解析文件: {inp_file}")
parser = SimulationParser(inp_file, 'abaqus')

# 手动读取文件并检查结构
with open(inp_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.read().split('\n')
    print("\n文件内容（相关部分）:")
    for i, line in enumerate(lines[210:230]):
        print(f"{i+211}: {line}")

print("\n开始解析...")
try:
    result = parser.parse()
    print(f"\n找到 {result['total_variables']} 个变量")
    for var in result['variables']:
        print(f"\n- {var['name']}: {var['current_value']} ({var['description']})")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()