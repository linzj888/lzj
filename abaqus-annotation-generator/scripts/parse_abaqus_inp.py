#!/usr/bin/env python3
"""
Abaqus .inp 文件解析与标注生成器（优化版）

功能：
- 解析 Abaqus 输入文件，提取关键信息
- 生成结构化的 Markdown 标注报告
- 统计材料、单元、边界、载荷、接触等要素

参数：
    --input: 输入的 .inp 文件路径（必需）
    --output: 输出的 .md 文件路径（可选，默认为同名 .md）
"""

import argparse
import re
import os
from pathlib import Path


class AbaqusINPParser:
    """Abaqus .inp 文件解析器"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.info = {
            'filename': os.path.basename(filepath),
            'heading': '',
            'analysis_type': '未知',
            'materials': [],
            'element_types': {},
            'boundaries': [],
            'loads': [],
            'contact_pairs': [],
            'node_count': 0,
            'element_count': 0,
            'parts': [],
            'assemblies': [],
        }

    def _parse_material(self, data_lines):
        """解析材料属性参数"""
        material_info = {
            'type': '未知',
            'parameters': []
        }

        i = 0
        while i < len(data_lines):
            line = data_lines[i].strip()

            # 识别材料类型
            if line.startswith('*Elastic'):
                material_info['type'] = '弹性材料'
                # 解析弹性参数（弹性模量、泊松比）
                param_lines = []
                j = i + 1
                while j < len(data_lines) and not data_lines[j].strip().startswith('*'):
                    values = [v.strip() for v in data_lines[j].split(',') if v.strip()]
                    if values:
                        # 弹性参数：弹性模量、泊松比
                        E = values[0] if len(values) > 0 else ''
                        nu = values[1] if len(values) > 1 else ''
                        if E and nu:
                            param_lines.append(f"弹性模量 E = {E} MPa")
                            param_lines.append(f"泊松比 ν = {nu}")
                        break
                    j += 1
                material_info['parameters'].extend(param_lines)
                i = j

            elif line.startswith('*Plastic'):
                material_info['type'] = '弹塑性材料'
                # 解析塑性参数（屈服应力、塑性应变）
                param_lines = []
                j = i + 1
                while j < len(data_lines) and not data_lines[j].strip().startswith('*'):
                    values = [v.strip() for v in data_lines[j].split(',') if v.strip()]
                    if values and len(values) >= 2:
                        # 第一组参数：屈服应力、初始塑性应变
                        yield_stress = values[0] if len(values) > 0 else ''
                        plastic_strain = values[1] if len(values) > 1 else ''
                        if yield_stress:
                            param_lines.append(f"屈服强度 σ_y = {yield_stress} MPa")
                        break
                    j += 1
                material_info['parameters'].extend(param_lines)
                i = j

            elif line.startswith('*Expansion'):
                # 热膨胀系数
                param_lines = []
                j = i + 1
                while j < len(data_lines) and not data_lines[j].strip().startswith('*'):
                    values = [v.strip() for v in data_lines[j].split(',') if v.strip()]
                    if values:
                        alpha = values[0] if len(values) > 0 else ''
                        if alpha:
                            param_lines.append(f"热膨胀系数 α = {alpha}")
                        break
                    j += 1
                material_info['parameters'].extend(param_lines)
                i = j

            elif line.startswith('*Conductivity'):
                # 热传导率
                param_lines = []
                j = i + 1
                while j < len(data_lines) and not data_lines[j].strip().startswith('*'):
                    values = [v.strip() for v in data_lines[j].split(',') if v.strip()]
                    if values:
                        k = values[0] if len(values) > 0 else ''
                        if k:
                            param_lines.append(f"热传导率 k = {k} W/(m·K)")
                        break
                    j += 1
                material_info['parameters'].extend(param_lines)
                i = j

            elif line.startswith('*Specific Heat'):
                # 比热容
                param_lines = []
                j = i + 1
                while j < len(data_lines) and not data_lines[j].strip().startswith('*'):
                    values = [v.strip() for v in data_lines[j].split(',') if v.strip()]
                    if values:
                        cp = values[0] if len(values) > 0 else ''
                        if cp:
                            param_lines.append(f"比热容 c_p = {cp} J/(kg·K)")
                        break
                    j += 1
                material_info['parameters'].extend(param_lines)
                i = j

            elif line.startswith('*Density'):
                # 密度
                param_lines = []
                j = i + 1
                while j < len(data_lines) and not data_lines[j].strip().startswith('*'):
                    values = [v.strip() for v in data_lines[j].split(',') if v.strip()]
                    if values:
                        rho = values[0] if len(values) > 0 else ''
                        if rho:
                            param_lines.append(f"密度 ρ = {rho} kg/m³")
                        break
                    j += 1
                material_info['parameters'].extend(param_lines)
                i = j

            elif line.startswith('*Hyperelastic'):
                material_info['type'] = '超弹性材料'
                model = '未知'
                match = re.search(r'material\s*=\s*(\w+)', line, re.IGNORECASE)
                if match:
                    model = match.group(1)
                material_info['parameters'].append(f"超弹性模型: {model}")
                i += 1

            elif line.startswith('*Viscoelastic'):
                material_info['type'] = '粘弹性材料'
                material_info['parameters'].append("粘弹性参数")
                i += 1

            elif line.startswith('*Damping'):
                # 阻尼系数
                param_lines = []
                j = i + 1
                while j < len(data_lines) and not data_lines[j].strip().startswith('*'):
                    values = [v.strip() for v in data_lines[j].split(',') if v.strip()]
                    if values:
                        alpha = values[0] if len(values) > 0 else ''
                        beta = values[1] if len(values) > 1 else ''
                        if alpha:
                            param_lines.append(f"质量比例阻尼 α = {alpha}")
                        if beta:
                            param_lines.append(f"刚度比例阻尼 β = {beta}")
                        break
                    j += 1
                material_info['parameters'].extend(param_lines)
                i = j

            elif line.startswith('*Failure Criteria'):
                material_info['parameters'].append("失效准则")
                i += 1

            elif line.startswith('*'):
                # 其他关键字，跳过
                i += 1
            else:
                i += 1

        return material_info

    def _parse_file(self):
        """逐行解析 .inp 文件"""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                current_block = None
                block_data = []
                in_material_block = False
                material_block_data = []

                for line in f:
                    stripped_line = line.strip()

                    # 检测关键字行
                    if stripped_line.startswith('*'):
                        # 如果在材料块内，收集所有子关键字
                        if in_material_block and stripped_line.startswith('*'):
                            material_block_data.append(line)
                            # 遇到下一个非材料子关键字时结束材料块
                            if not any(kw in stripped_line for kw in [
                                '*Elastic', '*Plastic', '*Hyperelastic', '*Viscoelastic',
                                '*Density', '*Expansion', '*Conductivity', '*Specific Heat',
                                '*Damping', '*Failure Criteria'
                            ]):
                                # 结束材料块
                                in_material_block = False
                                if current_block and 'Material' in current_block:
                                    self._process_block(current_block, material_block_data)
                                # 处理新的关键字
                                current_block = stripped_line
                                block_data = []
                            continue

                        # 检测材料块开始
                        if 'Material' in stripped_line and 'name=' in stripped_line:
                            in_material_block = True
                            current_block = stripped_line
                            material_block_data = [line]
                            continue

                        # 处理前一个块
                        if current_block:
                            self._process_block(current_block, block_data)

                        # 解析新的关键字
                        current_block = stripped_line
                        block_data = []
                    else:
                        # 数据行（非注释且非空）
                        if stripped_line and not stripped_line.startswith('**'):
                            if in_material_block:
                                material_block_data.append(line)
                            else:
                                block_data.append(line)

                # 处理最后一个块
                if in_material_block:
                    self._process_block(current_block, material_block_data)
                elif current_block:
                    self._process_block(current_block, block_data)

        except Exception as e:
            raise Exception(f"读取文件失败: {str(e)}")

    def _process_block(self, keyword, data_lines):
        """处理单个关键字块"""
        # 提取分析类型（全局搜索）
        if 'Heading' in keyword and not self.info['heading']:
            self.info['heading'] = '\n'.join(data_lines[:5]).strip()

        # 提取部件信息
        elif 'Part' in keyword and 'name=' in keyword:
            match = re.search(r'name\s*=\s*"?([^",\s]+)"?', keyword)
            if match:
                self.info['parts'].append(match.group(1))

        # 提取装配信息
        elif 'Assembly' in keyword and 'name=' in keyword:
            match = re.search(r'name\s*=\s*"?([^",\s]+)"?', keyword)
            if match:
                self.info['assemblies'].append(match.group(1))

        # 提取材料信息
        elif 'Material' in keyword and 'name=' in keyword:
            match = re.search(r'name\s*=\s*"?([^",\s]+)"?', keyword)
            if match:
                material_name = match.group(1)
                material_info = self._parse_material(data_lines)
                material_info['name'] = material_name
                self.info['materials'].append(material_info)

        # 提取单元类型
        elif 'Element' in keyword and 'type=' in keyword:
            match = re.search(r'type\s*=\s*(\w+)', keyword, re.IGNORECASE)
            if match:
                etype = match.group(1)
                self.info['element_types'][etype] = self.info['element_types'].get(etype, 0) + 1
                # 统计单元数量
                self.info['element_count'] += len(data_lines)

        # 提取节点数量
        elif keyword.startswith('*Node'):
            self.info['node_count'] += len(data_lines)

        # 提取边界条件
        elif keyword.startswith('*Boundary'):
            for line in data_lines:
                parts = [p.strip() for p in line.split(',') if p.strip()]
                if len(parts) >= 3:
                    boundary_type = parts[2] if parts[2].isdigit() or parts[2] in ['ENCASTRE', 'PINNED', 'XSYMM', 'YSYMM', 'ZSYMM'] else '未知'
                    self.info['boundaries'].append(boundary_type)

        # 提取载荷信息
        elif any(kw in keyword for kw in ['*Cload', '*Dload', '*Dsload', '*Temperature', '*Pressure']):
            load_type_map = {
                '*Cload': '集中载荷',
                '*Dload': '分布载荷',
                '*Dsload': '表面载荷',
                '*Temperature': '温度载荷',
                '*Pressure': '压力载荷'
            }
            for kw, name in load_type_map.items():
                if kw in keyword:
                    self.info['loads'].extend([name] * len(data_lines))
                    break

        # 提取接触信息
        elif 'Contact Pair' in keyword or 'Surface Contact' in keyword:
            match = re.search(r'interaction\s*=\s*"?([^",\s]+)"?', keyword, re.IGNORECASE)
            if match:
                contact_type = 'Contact Pair' if 'Contact Pair' in keyword else 'Surface Contact'
                self.info['contact_pairs'].append({
                    'type': contact_type,
                    'interaction': match.group(1)
                })

    def _determine_analysis_type(self):
        """根据关键字推断分析类型"""
        # 重新读取文件内容进行全局搜索（仅用于分析类型判断）
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            analysis_keywords = {
                '*Static,': '静态分析',
                '*Dynamic': '动力学分析',
                '*Heat Transfer': '热分析',
                '*Frequency': '频率分析',
                '*Buckle': '屈曲分析',
                '*Steady State Transport': '稳态传输分析',
                '*Dynamic, Temp-disp': '热力耦合分析',
                '*Coupled Temp-displacement': '热力耦合分析'
            }

            for keyword, name in analysis_keywords.items():
                if keyword in content:
                    self.info['analysis_type'] = name
                    break
        except:
            pass

    def parse(self):
        """执行完整解析"""
        print("正在解析文件...")
        self._parse_file()
        self._determine_analysis_type()
        print(f"解析完成！发现 {self.info['node_count']} 个节点，{self.info['element_count']} 个单元")
        return self.info


class MarkdownGenerator:
    """Markdown 标注生成器"""

    def __init__(self, info):
        self.info = info

    def generate(self):
        """生成 Markdown 报告"""
        md_content = f"""# Abaqus 模型标注报告

## 基本信息
- **文件名**: {self.info['filename']}
- **标题**: {self.info['heading'][:100] if self.info['heading'] else '未提供'}
- **分析类型**: {self.info['analysis_type']}

## 模型规模
- **节点数**: {self.info['node_count']}
- **单元数**: {self.info['element_count']}
- **部件数**: {len(self.info['parts'])}
- **装配数**: {len(self.info['assemblies'])}

"""

        # 材料信息
        if self.info['materials']:
            md_content += "## 材料信息\n\n"
            for material in self.info['materials']:
                md_content += f"### {material['name']}\n\n"
                md_content += f"- **材料类型**: {material['type']}\n"

                # 详细参数列表
                if material.get('parameters'):
                    md_content += "- **材料参数**:\n"
                    for param in material['parameters']:
                        md_content += f"  - {param}\n"

                md_content += "\n"

        # 单元信息
        if self.info['element_types']:
            md_content += "## 单元类型\n\n"
            for etype, count in self.info['element_types'].items():
                md_content += f"- **{etype}**: {count} 个定义\n"
            md_content += "\n"

        # 边界条件
        if self.info['boundaries']:
            # 统计各类型边界条件
            boundary_summary = {}
            for btype in self.info['boundaries']:
                boundary_summary[btype] = boundary_summary.get(btype, 0) + 1

            md_content += "## 边界条件\n\n"
            for btype, count in sorted(boundary_summary.items()):
                md_content += f"- **{btype}**: {count} 处\n"
            md_content += "\n"

        # 载荷信息
        if self.info['loads']:
            load_summary = {}
            for load_type in self.info['loads']:
                load_summary[load_type] = load_summary.get(load_type, 0) + 1

            md_content += "## 载荷信息\n\n"
            for load_type, count in sorted(load_summary.items()):
                md_content += f"- **{load_type}**: {load_type}, {count} 个\n"
            md_content += "\n"

        # 接触信息
        if self.info['contact_pairs']:
            md_content += "## 接触信息\n\n"
            for contact in self.info['contact_pairs']:
                md_content += f"- **{contact['type']}**: 交互属性 `{contact['interaction']}`\n"
            md_content += "\n"

        # 部件列表
        if self.info['parts']:
            md_content += "## 部件列表\n\n"
            for part in self.info['parts']:
                md_content += f"- {part}\n"
            md_content += "\n"

        # 装配列表
        if self.info['assemblies']:
            md_content += "## 装配列表\n\n"
            for assembly in self.info['assemblies']:
                md_content += f"- {assembly}\n"
            md_content += "\n"

        md_content += """---
*此报告由 Abaqus .inp 文件标注生成器自动生成*
"""

        return md_content


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='解析 Abaqus .inp 文件并生成标注报告')
    parser.add_argument('--input', required=True, help='输入的 .inp 文件路径')
    parser.add_argument('--output', help='输出的 .md 文件路径（默认为同名 .md）')

    args = parser.parse_args()

    # 验证输入文件
    if not os.path.exists(args.input):
        raise Exception(f"输入文件不存在: {args.input}")

    # 确定输出文件路径
    if args.output:
        output_path = args.output
    else:
        input_path = Path(args.input)
        output_path = str(input_path.with_suffix('.md'))

    # 解析 .inp 文件
    inp_parser = AbaqusINPParser(args.input)
    info = inp_parser.parse()

    # 生成 Markdown 报告
    print("正在生成标注报告...")
    md_generator = MarkdownGenerator(info)
    md_content = md_generator.generate()

    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"标注报告已生成: {output_path}")


if __name__ == '__main__':
    main()
