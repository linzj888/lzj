import os
import argparse
import numpy as np
import joblib

# 加载模型
def load_model(model_file):
    """
    加载训练好的FNO模型
    :param model_file: 模型文件路径
    :return: 加载的模型
    """
    try:
        model = joblib.load(model_file)
        print(f"成功加载模型: {model_file}")
        return model
    except Exception as e:
        print(f"加载模型时出错: {e}")
        return None

# 验证模型
def validate_model(model_file, dataset_file):
    """
    验证FNO模型性能
    :param model_file: 模型文件路径
    :param dataset_file: 数据集文件路径
    """
    # 加载模型
    model = load_model(model_file)
    if model is None:
        print("无法加载模型，验证失败")
        return
    
    # 加载数据集
    data = np.load(dataset_file)
    features = data['features']
    labels = data['labels']
    e_moduli = data['e_moduli']
    
    print(f"加载的数据集: 特征形状={features.shape}, 标签形状={labels.shape}, 弹性模量={e_moduli}")
    
    # 使用最后一个样本作为测试数据
    test_index = -1
    X_test = features[test_index]
    y_true = labels[test_index]
    test_e_modulus = e_moduli[test_index]
    
    print(f"\n测试样本: 弹性模量={test_e_modulus}")
    print(f"测试数据形状: X={X_test.shape}, y_true={y_true.shape}")
    
    # 进行预测
    y_pred = model.predict(X_test)
    print(f"预测结果形状: y_pred={y_pred.shape}")
    
    # 计算误差
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_true - y_pred))
    
    print(f"\n模型验证结果:")
    print(f"MSE: {mse:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"MAE: {mae:.6f}")
    
    # 计算每个位移分量的误差
    for i in range(3):
        comp_mse = np.mean((y_true[:, i] - y_pred[:, i]) ** 2)
        comp_rmse = np.sqrt(comp_mse)
        comp_mae = np.mean(np.abs(y_true[:, i] - y_pred[:, i]))
        print(f"位移分量 {i+1} - MSE: {comp_mse:.6f}, RMSE: {comp_rmse:.6f}, MAE: {comp_mae:.6f}")
    
    # 保存验证结果
    validation_file = os.path.splitext(model_file)[0] + "_validation.txt"
    with open(validation_file, 'w') as f:
        f.write("模型验证结果:\n")
        f.write(f"测试样本弹性模量: {test_e_modulus}\n")
        f.write(f"MSE: {mse:.6f}\n")
        f.write(f"RMSE: {rmse:.6f}\n")
        f.write(f"MAE: {mae:.6f}\n")
        for i in range(3):
            comp_mse = np.mean((y_true[:, i] - y_pred[:, i]) ** 2)
            f.write(f"位移分量 {i+1} MSE: {comp_mse:.6f}\n")
    
    print(f"验证结果已保存至: {validation_file}")

# 主函数
def main():
    parser = argparse.ArgumentParser(description='Validate FNO model')
    parser.add_argument('--model_file', type=str, required=True, help='Trained FNO model file')
    parser.add_argument('--dataset_file', type=str, required=True, help='FNO training dataset file')
    
    args = parser.parse_args()
    
    # 验证模型
    validate_model(args.model_file, args.dataset_file)

if __name__ == "__main__":
    main()
