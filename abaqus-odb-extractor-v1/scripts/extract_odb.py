#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ABAQUS ODB Extractor Script

Function: Extract specified variables from ABAQUS .odb files and save as CSV/Excel/TXT format

Prerequisites:
- ABAQUS software installed
- ABAQUS python environment available

Run methods:
1. Run in ABAQUS python environment:
   abaqus python extract_odb.py --odb_path <odb_file_path> --variables <variable_list> --output <output_file>

2. Run with system python (requires abaqus in PATH):
   python extract_odb.py --odb_path <odb_file_path> --variables <variable_list> --output <output_file>
"""

import argparse
import sys
import os

try:
    from odbAccess import openOdb
    from abaqusConstants import *
except ImportError:
    print("Error: Cannot import abaqus modules")
    print("Please ensure you are running this script in ABAQUS python environment")
    print("You can run it with:")
    print("  abaqus python extract_odb.py [arguments...]")
    sys.exit(1)


def parse_variables(var_string):
    """Parse variable string and return list of variable codes"""
    if not var_string:
        return []
    # Support comma or space separated variable list
    variables = [v.strip() for v in var_string.replace(',', ' ').split()]
    return variables


def extract_odb_data(odb_path, variables, output_format='csv', 
                     step_name=None, frame_index=None, 
                     node_set=None, element_set=None):
    """
    Extract data from ODB file
    
    Parameters:
        odb_path: ODB file path
        variables: List of variable codes, e.g. ['S', 'E', 'U']
        output_format: Output format ('csv', 'excel', 'txt')
        step_name: Step name (None for last step)
        frame_index: Frame index (None for last frame)
        node_set: Node set name
        element_set: Element set name
    
    Returns:
        Extracted data list
    """
    print("Opening ODB file: {}".format(odb_path))
    
    try:
        odb = openOdb(path=odb_path)
    except Exception as e:
        print("Error: Cannot open ODB file - {}".format(str(e)))
        return None
    
    # Select step and frame
    if step_name is None:
        step = odb.steps.values()[-1]
        step_name = step.name
    else:
        if step_name not in odb.steps.keys():
            print("Error: Step '{}' does not exist".format(step_name))
            print("Available steps: {}".format(list(odb.steps.keys())))
            odb.close()
            return None
        step = odb.steps[step_name]
    
    print("Using step: {}".format(step_name))
    
    if frame_index is None:
        frame = step.frames[-1]
        frame_index = len(step.frames) - 1
    else:
        if frame_index >= len(step.frames):
            print("Error: Frame index {} out of range (total {} frames)".format(frame_index, len(step.frames)))
            odb.close()
            return None
        frame = step.frames[frame_index]
    
    print("Using frame: {}".format(frame_index))
    
    # Get instance
    instance = odb.rootAssembly.instances.values()[0]
    print("Using instance: {}".format(instance.name))
    
    # Extract data
    extracted_data = []
    
    # Process node variables
    node_variables = []
    field_outputs = {}
    for var in variables:
        if var in frame.fieldOutputs.keys():
            field_outputs[var] = frame.fieldOutputs[var]
    
    if not field_outputs:
        print("Warning: No specified variables found in current frame")
        print("Available variables: {}".format(frame.fieldOutputs.keys()))
        odb.close()
        return None
    
    print("Found {} variables: {}".format(len(field_outputs), list(field_outputs.keys())))
    
    # Determine nodes or elements to extract
    nodes = []
    elements = []
    
    if node_set:
        if node_set in instance.nodeSets.keys():
            nodes = instance.nodeSets[node_set].nodes
            print("Using node set: {} (total {} nodes)".format(node_set, len(nodes)))
        else:
            print("Warning: Node set '{}' does not exist".format(node_set))
            print("Available node sets: {}".format(list(instance.nodeSets.keys())))
    elif element_set:
        if element_set in instance.elementSets.keys():
            elements = instance.elementSets[element_set].elements
            print("Using element set: {} (total {} elements)".format(element_set, len(elements)))
        else:
            print("Warning: Element set '{}' does not exist".format(element_set))
            print("Available element sets: {}".format(list(instance.elementSets.keys())))
    else:
        # Default to all nodes
        nodes = instance.nodes
        print("Extracting all node data (total {} nodes)".format(len(nodes)))
    
    # Preprocess field outputs to create a lookup dictionary for faster access
    # This will significantly improve performance for large node sets
    field_output_lookups = {}
    for var_name, field_output in field_outputs.items():
        # Create a dictionary mapping node labels to values
        node_value_map = {}
        for value in field_output.values:
            if hasattr(value, 'nodeLabel'):
                node_value_map[value.nodeLabel] = value
        field_output_lookups[var_name] = node_value_map
    
    # Extract data
    data_headers = ['Node/Element_ID', 'Type']
    data_headers.extend(field_outputs.keys())
    
    # Extract node data
    if nodes:
        for node in nodes:
            row = {
                'ID': node.label,
                'Type': 'Node',
                'Coordinates': [node.coordinates[0], node.coordinates[1], node.coordinates[2]]
            }
            
            # Get each variable value using preprocessed lookup
            for var_name, field_output in field_outputs.items():
                try:
                    # Use the preprocessed lookup for faster access
                    if var_name in field_output_lookups:
                        node_value_map = field_output_lookups[var_name]
                        if node.label in node_value_map:
                            value = node_value_map[node.label]
                            row[var_name] = list(value.data)
                            # Extract Mises stress from stress tensor
                            if var_name == 'S' and hasattr(value, 'mises'):
                                row['MISES'] = value.mises
                        else:
                            row[var_name] = None
                    else:
                        # Fallback to original method if lookup fails
                        values = field_output.getSubset(region=node).values
                        if values:
                            value = values[0]
                            row[var_name] = list(value.data)
                            if var_name == 'S' and hasattr(value, 'mises'):
                                row['MISES'] = value.mises
                        else:
                            row[var_name] = None
                except Exception as e:
                    row[var_name] = None
            
            extracted_data.append(row)
    
    # Extract element data
    if elements and not nodes:
        for elem in elements:
            row = {
                'ID': elem.label,
                'Type': 'Element'
            }
            
            for var_name, field_output in field_outputs.items():
                try:
                    values = field_output.getSubset(region=elem).values
                    if values:
                        value = values[0].data
                        if hasattr(value, '__len__'):
                            row[var_name] = list(value)
                            # Extract Mises stress from stress tensor
                            if var_name == 'S' and hasattr(values[0], 'mises'):
                                row['MISES'] = values[0].mises
                        else:
                            row[var_name] = value
                    else:
                        row[var_name] = None
                except Exception as e:
                    row[var_name] = None
            
            extracted_data.append(row)
    
    odb.close()
    print("Successfully extracted {} data records".format(len(extracted_data)))
    
    return extracted_data, data_headers


def save_to_csv(data, headers, output_path):
    """Save data to CSV file"""
    import csv
    
    # Expand data (handle vectors/tensors)
    expanded_data = []
    for row in data:
        expanded_row = {}
        expanded_row['ID'] = row['ID']
        expanded_row['Type'] = row['Type']
        
        # Add coordinates (if node data)
        if 'Coordinates' in row:
            coords = row['Coordinates']
            expanded_row['X'] = coords[0]
            expanded_row['Y'] = coords[1]
            expanded_row['Z'] = coords[2] if len(coords) > 2 else 0.0
        
        # Add variable values
        for key in row.keys():
            if key not in ['ID', 'Type', 'Coordinates']:
                value = row[key]
                if value is None:
                    expanded_row[key] = 'N/A'
                elif isinstance(value, list):
                    # Handle vector/tensor data, separated by semicolons
                    expanded_row[key] = ';'.join([str(v) for v in value])
                else:
                    expanded_row[key] = str(value)
        
        expanded_data.append(expanded_row)
    
    # Write CSV - 使用文本模式兼容 Python 2.7
    import sys
    if sys.version_info[0] == 2:
        # Python 2.7 版本
        with open(output_path, 'wb') as f:
            # 收集所有可能的字段名，包括动态添加的 MISES
            all_fields = set(['ID', 'Type', 'X', 'Y', 'Z'])
            for row in expanded_data:
                all_fields.update(row.keys())
            # 确保字段顺序合理
            fieldnames = ['ID', 'Type', 'X', 'Y', 'Z']
            additional_fields = [field for field in all_fields if field not in ['ID', 'Type', 'X', 'Y', 'Z', 'Coordinates']]
            fieldnames.extend(additional_fields)
            
            # 手动写入 CSV
            # Write header
            header = ','.join(fieldnames) + '\n'
            f.write(header.encode('utf-8'))
            
            # Write data
            for row in expanded_data:
                values = []
                for field in fieldnames:
                    if field in row:
                        val = row[field]
                        # 确保值是字符串
                        if not isinstance(val, basestring):
                            val = str(val)
                        # 处理包含逗号的值
                        if ',' in val:
                            val = '"' + val.replace('"', '""') + '"'
                        values.append(val)
                line = ','.join(values) + '\n'
                f.write(line.encode('utf-8'))
    else:
        # Python 3 版本
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            # 收集所有可能的字段名，包括动态添加的 MISES
            all_fields = set(['ID', 'Type', 'X', 'Y', 'Z'])
            for row in expanded_data:
                all_fields.update(row.keys())
            # 确保字段顺序合理
            fieldnames = ['ID', 'Type', 'X', 'Y', 'Z']
            additional_fields = [field for field in all_fields if field not in ['ID', 'Type', 'X', 'Y', 'Z', 'Coordinates']]
            fieldnames.extend(additional_fields)
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(expanded_data)
    
    print("Data saved to: {}".format(output_path))


def save_to_txt(data, headers, output_path):
    """Save data to text file"""
    with open(output_path, 'wb') as f:
        # 收集所有可能的字段名，包括动态添加的 MISES
        all_fields = set(['ID', 'Type'])
        for row in data:
            all_fields.update(row.keys())
        # 确保字段顺序合理
        field_order = ['ID', 'Type']
        additional_fields = [f for f in all_fields if f not in ['ID', 'Type', 'Coordinates']]
        field_order.extend(additional_fields)
        
        # Write header
        header_line = "\t".join(field_order) + "\n"
        f.write(header_line.encode('utf-8'))
        f.write("="*80 + "\n")
        
        # Write data
        for row in data:
            values = []
            for key in field_order:
                if key in row:
                    val = row[key]
                    if isinstance(val, list):
                        values.append(str(val))
                    elif val is None:
                        values.append('N/A')
                    else:
                        values.append(str(val))
                else:
                    values.append('N/A')
            line = "\t".join(values)
            f.write((line + "\n").encode('utf-8'))
    
    print("Data saved to: {}".format(output_path))


def save_to_excel(data, headers, output_path):
    """Save data to Excel file"""
    try:
        import openpyxl
    except ImportError:
        print("Warning: openpyxl not installed, will try xlsxwriter")
        try:
            import xlsxwriter
        except ImportError:
            print("Error: Cannot import Excel library, please install openpyxl or xlsxwriter")
            print("Installation command: pip install openpyxl")
            return False
    
    # Use openpyxl
    try:
        import openpyxl
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = "ODB Data"
        
        # Write header
        headers_row = ['ID', 'Type', 'X', 'Y', 'Z'] + [h for h in headers 
                     if h not in ['ID', 'Type']]
        ws.append(headers_row)
        
        # Write data
        for row in data:
            data_row = [row['ID'], row['Type']]
            
            # Add coordinates
            if 'Coordinates' in row:
                coords = row['Coordinates']
                data_row.extend([coords[0], coords[1], coords[2] if len(coords) > 2 else 0.0])
            else:
                data_row.extend(['', '', ''])
            
            # Add variable values
            for key in headers:
                if key in row and key not in ['ID', 'Type', 'Coordinates']:
                    val = row[key]
                    if isinstance(val, list):
                        data_row.append(str(val))
                    elif val is None:
                        data_row.append('N/A')
                    else:
                        data_row.append(val)
            
            ws.append(data_row)
        
        wb.save(output_path)
        print("Data saved to: {}".format(output_path))
        return True
        
    except Exception as e:
        print("Excel save failed: {}".format(str(e)))
        return False


def save_to_md(data, headers, output_path):
    """Save data to Markdown file"""
    # Expand data (handle vectors/tensors and coordinates)
    expanded_data = []
    for row in data:
        expanded_row = {}
        expanded_row['ID'] = row['ID']
        expanded_row['Type'] = row['Type']
        
        # Add coordinates (if node data)
        if 'Coordinates' in row:
            coords = row['Coordinates']
            expanded_row['X'] = coords[0]
            expanded_row['Y'] = coords[1]
            expanded_row['Z'] = coords[2] if len(coords) > 2 else 0.0
        
        # Add variable values
        for key in row.keys():
            if key not in ['ID', 'Type', 'Coordinates']:
                value = row[key]
                if value is None:
                    expanded_row[key] = 'N/A'
                elif isinstance(value, list):
                    # Handle vector/tensor data, separated by semicolons
                    expanded_row[key] = ';'.join([str(v) for v in value])
                else:
                    expanded_row[key] = str(value)
        
        expanded_data.append(expanded_row)
    
    # 收集所有可能的字段名，包括动态添加的 MISES
    all_fields = set(['ID', 'Type', 'X', 'Y', 'Z'])
    for row in expanded_data:
        all_fields.update(row.keys())
    # 确保字段顺序合理
    fieldnames = ['ID', 'Type', 'X', 'Y', 'Z']
    additional_fields = [field for field in all_fields if field not in ['ID', 'Type', 'X', 'Y', 'Z', 'Coordinates']]
    fieldnames.extend(additional_fields)
    
    import sys
    if sys.version_info[0] == 2:
        # Python 2.7 版本
        with open(output_path, 'wb') as f:
            # Write Markdown header
            header = "# ABAQUS ODB Extraction Results\n\n"
            header += "## Extraction Info\n"
            header += "- Variables: {}\n".format(', '.join(headers))
            header += "- Data count: {} records\n\n".format(len(expanded_data))
            f.write(header.encode('utf-8'))
            
            # Write Markdown table
            f.write("## Data Table\n\n".encode('utf-8'))
            
            # Write table header
            table_header = "| " + " | ".join(fieldnames) + " |\n"
            f.write(table_header.encode('utf-8'))
            
            # Write table separator
            separator = "| " + " | ".join(["---" for _ in fieldnames]) + " |\n"
            f.write(separator.encode('utf-8'))
            
            # Write data rows
            for row in expanded_data:
                values = []
                for field in fieldnames:
                    if field in row:
                        val = row[field]
                        # 确保值是字符串
                        if not isinstance(val, basestring):
                            val_str = str(val)
                        else:
                            val_str = val
                        # 处理包含管道符的值
                        if '|' in val_str:
                            val_str = val_str.replace('|', '\\|')
                        values.append(val_str)
                    else:
                        values.append('N/A')
                table_row = "| " + " | ".join(values) + " |\n"
                f.write(table_row.encode('utf-8'))
            
            # Write footer
            footer = "\n## Notes\n"
            footer += "- Data from ABAQUS ODB file\n"
            footer += "- Coordinate units match model definition\n"
            footer += "- Stress units match model definition\n"
            f.write(footer.encode('utf-8'))
    else:
        # Python 3 版本
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write Markdown header
            header = "# ABAQUS ODB 提取结果\n\n"
            header += "## 提取信息\n"
            header += "- 提取变量: {}\n".format(', '.join(headers))
            header += "- 数据量: {} 条记录\n\n".format(len(expanded_data))
            f.write(header)
            
            # Write Markdown table
            f.write("## 数据表格\n\n")
            
            # Write table header
            table_header = "| " + " | ".join(fieldnames) + " |\n"
            f.write(table_header)
            
            # Write table separator
            separator = "| " + " | ".join(["---" for _ in fieldnames]) + " |\n"
            f.write(separator)
            
            # Write data rows
            for row in expanded_data:
                values = []
                for field in fieldnames:
                    if field in row:
                        val = row[field]
                        # 确保值是字符串
                        if not isinstance(val, str):
                            val_str = str(val)
                        else:
                            val_str = val
                        # 处理包含管道符的值
                        if '|' in val_str:
                            val_str = val_str.replace('|', '\\|')
                        values.append(val_str)
                    else:
                        values.append('N/A')
                table_row = "| " + " | ".join(values) + " |\n"
                f.write(table_row)
            
            # Write footer
            footer = "\n## 说明\n"
            footer += "- 数据来源于 ABAQUS ODB 文件\n"
            footer += "- 坐标单位与模型定义一致\n"
            footer += "- 应力单位与模型定义一致\n"
            f.write(footer)
    
    print("Data saved to: {}".format(output_path))


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Extract variable data from ABAQUS ODB file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract stress and displacement data to CSV
  abaqus python extract_odb.py --odb_path job.odb --variables S,U --output results.csv
  
  # Extract strain data from specific step to Excel
  abaqus python extract_odb.py --odb_path job.odb --variables E --output results.xlsx --step Step-1 --frame 0
  
  # Extract data from node set
  abaqus python extract_odb.py --odb_path job.odb --variables S,E,U --output results.csv --node_set SET-1
        """)
    
    parser.add_argument('--odb_path', required=True, help='ODB file path')
    parser.add_argument('--variables', required=True, 
                       help='Variable codes, comma separated (e.g.: S=stress, E=strain, U=displacement, NT=temperature)')
    parser.add_argument('--output', required=True, help='Output file path (supports .csv, .xlsx, .txt)')
    parser.add_argument('--step', default=None, help='Step name (default: last step)')
    parser.add_argument('--frame', type=int, default=None, help='Frame index (default: last frame)')
    parser.add_argument('--node_set', default=None, help='Node set name (default: all nodes)')
    parser.add_argument('--element_set', default=None, help='Element set name')
    parser.add_argument('--format', choices=['csv', 'excel', 'txt', 'markdown'], default=None,
                       help='Output format (default: auto-detect from file extension)')
    
    args = parser.parse_args()
    
    # Check if ODB file exists
    if not os.path.exists(args.odb_path):
        print("Error: ODB file does not exist: {}".format(args.odb_path))
        return 1
    
    # Parse variable list
    variables = parse_variables(args.variables)
    if not variables:
        print("Error: At least one variable must be specified")
        return 1
    
    # Determine output format
    if args.format:
        output_format = args.format
    else:
        ext = os.path.splitext(args.output)[1].lower()
        if ext == '.csv':
            output_format = 'csv'
        elif ext in ['.xlsx', '.xls']:
            output_format = 'excel'
        elif ext == '.txt':
            output_format = 'txt'
        elif ext == '.md':
            output_format = 'markdown'
        else:
            print("Warning: Unknown output file extension '{}', defaulting to CSV format".format(ext))
            output_format = 'csv'
    
    # Extract data
    result = extract_odb_data(
        args.odb_path, 
        variables, 
        output_format=output_format,
        step_name=args.step,
        frame_index=args.frame,
        node_set=args.node_set,
        element_set=args.element_set
    )
    
    if result is None:
        return 1
    
    data, headers = result
    
    # Save data
    if output_format == 'csv':
        save_to_csv(data, headers, args.output)
    elif output_format == 'txt':
        save_to_txt(data, headers, args.output)
    elif output_format == 'excel':
        save_to_excel(data, headers, args.output)
    elif output_format == 'markdown':
        save_to_md(data, headers, args.output)
    
    print("\nExtraction completed!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
