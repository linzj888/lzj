import os
import argparse
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
import joblib

# 简化版FNO模型类
class SimplifiedFNO:
    def __init__(self, hidden_layer_sizes=(128, 64), max_iter=1000, random_state=42):
        """
        初始化简化版FNO模型
        :param hidden_layer_sizes: 隐藏层大小
        :param max_iter: 最大迭代次数
        :param random_state: 随机种子
        """
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
            random_state=random_state,
            verbose=True
        )
    
    def train(self, X_train, y_train):
        """
        训练模型
        :param X_train: 训练特征 (num_samples * nodes_per_sample, features_dim)
        :param y_train: 训练标签 (num_samples * nodes_per_sample, labels_dim)
        """
        print(f"开始训练模型，训练数据形状: X={X_train.shape}, y={y_train.shape}")
        self.model.fit(X_train, y_train)
        print("模型训练完成")
    
    def predict(self, X):
        """
        预测
        :param X: 输入特征
        :return: 预测结果
        """
        return self.model.predict(X)
    
    def evaluate(self, X_test, y_test):
        """
        评估模型
        :param X_test: 测试特征
        :param y_test: 测试标签
        :return: MSE损失
        """
        predictions = self.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        print(f"模型评估 MSE: {mse:.6f}")
        return mse

# 加载数据集
def load_dataset(dataset_file):
    """
    加载FNO训练数据集
    :param dataset_file: 数据集文件路径
    :return: 特征、标签、弹性模量
    """
    data = np.load(dataset_file)
    features = data['features']
    labels = data['labels']
    e_moduli = data['e_moduli']
    
    print(f"加载的数据集: 特征形状={features.shape}, 标签形状={labels.shape}, 弹性模量={e_moduli}")
    
    return features, labels, e_moduli

# 训练模型
def train_fno_model(dataset_file, model_output, hidden_layers, max_iter):
    """
    训练FNO模型
    :param dataset_file: 数据集文件路径
    :param model_output: 模型输出路径
    :param hidden_layers: 隐藏层大小
    :param max_iter: 最大迭代次数
    """
    # 加载数据集
    features, labels, e_moduli = load_dataset(dataset_file)
    
    # 展平数据用于MLP训练
    num_samples, nodes_per_sample, features_dim = features.shape
    _, _, labels_dim = labels.shape
    
    X_flat = features.reshape(-1, features_dim)
    y_flat = labels.reshape(-1, labels_dim)
    
    print(f"展平后的数据: X={X_flat.shape}, y={y_flat.shape}")
    
    # 划分训练集和测试集（由于样本数少，使用前4个作为训练，最后1个作为测试）
    train_size = 4 * nodes_per_sample
    X_train, X_test = X_flat[:train_size], X_flat[train_size:]
    y_train, y_test = y_flat[:train_size], y_flat[train_size:]
    
    print(f"训练集大小: {X_train.shape}, 测试集大小: {X_test.shape}")
    
    # 创建并训练模型
    fno_model = SimplifiedFNO(
        hidden_layer_sizes=hidden_layers,
        max_iter=max_iter,
        random_state=42
    )
    
    fno_model.train(X_train, y_train)
    
    # 评估模型
    train_mse = fno_model.evaluate(X_train, y_train)
    test_mse = fno_model.evaluate(X_test, y_test)
    
    # 计算RMSE和MAE
    import numpy as np
    train_rmse = np.sqrt(train_mse)
    test_rmse = np.sqrt(test_mse)
    
    train_predictions = fno_model.predict(X_train)
    test_predictions = fno_model.predict(X_test)
    
    train_mae = np.mean(np.abs(y_train - train_predictions))
    test_mae = np.mean(np.abs(y_test - test_predictions))
    
    print(f"\n最终评估结果:")
    print(f"训练集 MSE: {train_mse:.6f}, RMSE: {train_rmse:.6f}, MAE: {train_mae:.6f}")
    print(f"测试集 MSE: {test_mse:.6f}, RMSE: {test_rmse:.6f}, MAE: {test_mae:.6f}")
    
    # 保存评估结果
    evaluation_file = os.path.splitext(model_output)[0] + "_evaluation.txt"
    with open(evaluation_file, 'w') as f:
        f.write("模型评估结果:\n")
        f.write(f"训练集 MSE: {train_mse:.6f}\n")
        f.write(f"训练集 RMSE: {train_rmse:.6f}\n")
        f.write(f"训练集 MAE: {train_mae:.6f}\n")
        f.write(f"测试集 MSE: {test_mse:.6f}\n")
        f.write(f"测试集 RMSE: {test_rmse:.6f}\n")
        f.write(f"测试集 MAE: {test_mae:.6f}\n")
        f.write(f"模型架构: {hidden_layers}\n")
        f.write(f"训练迭代次数: {max_iter}\n")
    
    print(f"评估结果已保存至: {evaluation_file}")
    
    # 保存模型
    joblib.dump(fno_model, model_output)
    print(f"模型已保存至: {model_output}")

# 主函数
def main():
    parser = argparse.ArgumentParser(description='Train FNO model')
    parser.add_argument('--dataset_file', type=str, required=True, help='FNO training dataset file')
    parser.add_argument('--model_output', type=str, default='fno_model.pkl', help='Path to save trained model')
    parser.add_argument('--hidden_layers', type=str, default='256,128,64', help='Hidden layer sizes (comma-separated)')
    parser.add_argument('--max_iter', type=int, default=2000, help='Maximum iterations for model training')
    
    args = parser.parse_args()
    
    # 解析隐藏层大小
    hidden_layers = list(map(int, args.hidden_layers.split(',')))
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.model_output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 训练模型
    train_fno_model(args.dataset_file, args.model_output, hidden_layers, args.max_iter)

if __name__ == "__main__":
    main()
