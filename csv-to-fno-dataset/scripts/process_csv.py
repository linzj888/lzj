import os
import argparse
import numpy as np
import pandas as pd

# 处理CSV数据
def process_csv_data(data_dir, output_dir):
    """
    处理CSV数据，提取坐标和位移信息
    :param data_dir: CSV文件目录
    :param output_dir: 输出目录
    :return: 处理后的数据
    """
    # 查找CSV文件
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and 'extracted_U_' in f]
    csv_files.sort()
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    for csv_file in csv_files:
        print(f"- {csv_file}")
    
    # 存储所有数据
    all_data = []
    
    for csv_file in csv_files:
        # 从文件名提取弹性模量值
        try:
            e_modulus_str = csv_file.split('_U_')[1].split('.')[0]
            e_modulus = float(e_modulus_str)
        except (IndexError, ValueError):
            print(f"无法从文件名 {csv_file} 提取弹性模量，跳过")
            continue
        
        # 读取CSV文件
        csv_path = os.path.join(data_dir, csv_file)
        df = pd.read_csv(csv_path)
        
        # 提取坐标和位移数据
        coordinates = df[['X', 'Y', 'Z']].values
        displacements = []
        
        for u_str in df['U']:
            # 解析位移分量
            u_components = list(map(float, u_str.split(';')))
            displacements.append(u_components)
        
        displacements = np.array(displacements)
        
        # 存储数据
        data = {
            'e_modulus': e_modulus,
            'coordinates': coordinates,
            'displacements': displacements,
            'filename': csv_file
        }
        
        all_data.append(data)
        print(f"处理完成: {csv_file}, 节点数: {len(df)}, 弹性模量: {e_modulus}")
    
    # 保存处理后的数据
    output_file = os.path.join(output_dir, 'fno_training_data.npy')
    np.save(output_file, all_data)
    print(f"数据处理完成，共处理 {len(all_data)} 个文件")
    print(f"处理后的数据已保存至: {output_file}")
    
    # 统计信息
    if all_data:
        print(f"第一个文件的坐标形状: {all_data[0]['coordinates'].shape}")
        print(f"第一个文件的位移形状: {all_data[0]['displacements'].shape}")
        print(f"弹性模量值: {[d['e_modulus'] for d in all_data]}")
    
    return all_data

# 主函数
def main():
    parser = argparse.ArgumentParser(description='Process CSV data for FNO model training')
    parser.add_argument('--data_dir', type=str, required=True, help='Directory containing CSV files')
    parser.add_argument('--output_dir', type=str, default='.', help='Directory to save processed datasets')
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 处理CSV数据
    process_csv_data(args.data_dir, args.output_dir)

if __name__ == "__main__":
    main()
