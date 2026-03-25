import os
import argparse
import numpy as np
from sklearn.preprocessing import StandardScaler

# 创建FNO数据集
def create_fno_dataset(input_file, output_dir):
    """
    将处理后的数据转换为标准化的FNO训练数据集
    :param input_file: 处理后的数据文件
    :param output_dir: 输出目录
    """
    # 加载处理后的数据
    data = np.load(input_file, allow_pickle=True)
    
    print(f"加载的数据包含 {len(data)} 个样本")
    
    # 提取所有数据
    coordinates_list = []
    displacements_list = []
    e_moduli_list = []
    
    for item in data:
        coordinates = item['coordinates']
        displacements = item['displacements']
        e_modulus = item['e_modulus']
        
        coordinates_list.append(coordinates)
        displacements_list.append(displacements)
        e_moduli_list.append(e_modulus)

    # 转换为numpy数组
    coordinates_array = np.vstack(coordinates_list)
    displacements_array = np.vstack(displacements_list)
    e_moduli_array = np.array(e_moduli_list)

    # 数据标准化
    scaler_features = StandardScaler()
    scaler_labels = StandardScaler()

    # 标准化特征
    features_normalized = scaler_features.fit_transform(coordinates_array)

    # 标准化标签
    displacements_normalized = scaler_labels.fit_transform(displacements_array)

    # 重塑数据为FNO模型所需的格式
    # 将数据按弹性模量分组
    num_samples = len(data)
    nodes_per_sample = coordinates_list[0].shape[0]

    # 重塑为 (num_samples, nodes_per_sample, features_dim)
    features_reshaped = features_normalized.reshape(num_samples, nodes_per_sample, -1)
    labels_reshaped = displacements_normalized.reshape(num_samples, nodes_per_sample, -1)

    # 保存数据集
    output_file = os.path.join(output_dir, 'fno_dataset.npz')
    np.savez(output_file,
             features=features_reshaped,
             labels=labels_reshaped,
             e_moduli=e_moduli_array,
             nodes_per_sample=nodes_per_sample)

    # 保存标准化器参数
    scalers_file = os.path.join(output_dir, 'scalers.npz')
    np.savez(scalers_file,
             feature_mean=scaler_features.mean_,
             feature_std=scaler_features.scale_,
             label_mean=scaler_labels.mean_,
             label_std=scaler_labels.scale_)

    # 保存处理信息
    info_file = os.path.join(output_dir, 'fno_dataset_info.txt')
    with open(info_file, 'w') as f:
        f.write(f"数据集信息:\n")
        f.write(f"样本数量: {num_samples}\n")
        f.write(f"每个样本的节点数: {nodes_per_sample}\n")
        f.write(f"特征维度: {features_reshaped.shape[2]}\n")
        f.write(f"标签维度: {labels_reshaped.shape[2]}\n")
        f.write(f"弹性模量值: {e_moduli_array}\n")
        f.write(f"特征标准化均值: {scaler_features.mean_}\n")
        f.write(f"特征标准化标准差: {scaler_features.scale_}\n")
        f.write(f"标签标准化均值: {scaler_labels.mean_}\n")
        f.write(f"标签标准化标准差: {scaler_labels.scale_}\n")

    print(f"数据集准备完成")
    print(f"样本数量: {num_samples}")
    print(f"每个样本的节点数: {nodes_per_sample}")
    print(f"特征形状: {features_reshaped.shape}")
    print(f"标签形状: {labels_reshaped.shape}")
    print(f"弹性模量值: {e_moduli_array}")

    # 验证数据
    print(f"\n数据验证:")
    print(f"特征范围: [{features_normalized.min():.4f}, {features_normalized.max():.4f}]")
    print(f"标签范围: [{displacements_normalized.min():.4f}, {displacements_normalized.max():.4f}]")

    print(f"\n输出文件:")
    print(f"- {output_file}")
    print(f"- {scalers_file}")
    print(f"- {info_file}")

# 主函数
def main():
    parser = argparse.ArgumentParser(description='Create FNO training dataset')
    parser.add_argument('--input_file', type=str, default='fno_training_data.npy', help='Processed data file')
    parser.add_argument('--output_dir', type=str, default='.', help='Directory to save dataset')
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 创建FNO数据集
    create_fno_dataset(args.input_file, args.output_dir)

if __name__ == "__main__":
    main()
