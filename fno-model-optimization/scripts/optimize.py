import os
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
import argparse
import matplotlib.pyplot as plt

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class SimplifiedFNO:
    def __init__(self, hidden_layer_sizes=(128, 64), max_iter=1000, random_state=42):
        from sklearn.neural_network import MLPRegressor
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
            random_state=random_state,
            verbose=False
        )
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def predict(self, X):
        return self.model.predict(X)


class FNOOptimizer:
    def __init__(self, model_path, scalers_path, dataset_path):
        self.model_path = model_path
        self.scalers_path = scalers_path
        self.dataset_path = dataset_path
        
        self.model = None
        self.scaler_features = None
        self.scaler_labels = None
        self.sample_coords = None
        
        self.optimization_history = []
        self.current_var_name = None
        self.current_objective = None
        
        self._load_data()
    
    def _load_data(self):
        print("=" * 60)
        print("加载优化所需数据...")
        print("=" * 60)
        
        dataset = np.load(self.dataset_path)
        features = dataset['features']
        self.sample_coords = features[0, :, :3]
        print(f"✓ 坐标数据加载完成: {self.sample_coords.shape}")
        
        self.model = joblib.load(self.model_path)
        print(f"✓ 模型加载完成: {self.model_path}")
        
        scalers = np.load(self.scalers_path)
        self.scaler_features = StandardScaler()
        self.scaler_features.mean_ = scalers['feature_mean']
        self.scaler_features.scale_ = scalers['feature_std']
        
        self.scaler_labels = StandardScaler()
        self.scaler_labels.mean_ = scalers['label_mean']
        self.scaler_labels.scale_ = scalers['label_std']
        print("✓ 标准化器加载完成")
    
    def evaluate_design(self, var_value):
        """
        评估给定设计变量值下的响应
        """
        num_nodes = self.sample_coords.shape[0]
        
        X_input = np.zeros((num_nodes, 4))
        X_input[:, :3] = self.sample_coords
        X_input[:, 3] = var_value
        
        X_normalized = self.scaler_features.transform(X_input)
        y_pred_normalized = self.model.predict(X_normalized)
        y_pred = self.scaler_labels.inverse_transform(y_pred_normalized)
        
        total_displacement = np.sqrt(np.sum(y_pred**2, axis=1))
        
        return y_pred, total_displacement
    
    def evaluate_objective(self, var_value, objective_type):
        """
        评估目标函数值
        """
        _, total_displacement = self.evaluate_design(var_value)
        
        if objective_type == "max_displacement":
            return total_displacement.max()
        elif objective_type == "average_displacement":
            return total_displacement.mean()
        else:
            raise ValueError(f"不支持的目标函数类型: {objective_type}")
    
    def objective_function(self, var_value):
        """
        目标函数：供优化算法调用
        """
        obj_val = self.evaluate_objective(var_value[0], self.current_objective)
        self.optimization_history.append((var_value[0], obj_val))
        print(f"  {self.current_var_name}={var_value[0]:.0f}, 目标值={obj_val:.6f}")
        return obj_val
    
    def optimize_grid_search(self, var_name, var_bounds, objective, n_points=100):
        """
        使用网格搜索进行优化
        """
        print("\n" + "=" * 60)
        print("使用网格搜索进行优化...")
        print("=" * 60)
        print(f"设计变量: {var_name}")
        print(f"搜索范围: [{var_bounds[0]}, {var_bounds[1]}]")
        print(f"采样点数: {n_points}")
        print(f"优化目标: {objective}")
        
        self.current_var_name = var_name
        self.current_objective = objective
        self.optimization_history = []
        
        var_values = np.linspace(var_bounds[0], var_bounds[1], n_points)
        
        print("\n评估所有采样点:")
        for val in var_values:
            self.objective_function([val])
        
        best_idx = np.argmin([h[1] for h in self.optimization_history])
        best_var = self.optimization_history[best_idx][0]
        best_obj = self.optimization_history[best_idx][1]
        
        return best_var, best_obj
    
    def optimize_scipy(self, var_name, var_bounds, objective, n_initial_points=10):
        """
        使用SciPy进行优化
        """
        if not SCIPY_AVAILABLE:
            print("SciPy不可用，使用网格搜索代替")
            return self.optimize_grid_search(var_name, var_bounds, objective, n_points=50)
        
        print("\n" + "=" * 60)
        print("使用SciPy L-BFGS-B进行优化...")
        print("=" * 60)
        print(f"设计变量: {var_name}")
        print(f"搜索范围: [{var_bounds[0]}, {var_bounds[1]}]")
        print(f"优化目标: {objective}")
        
        self.current_var_name = var_name
        self.current_objective = objective
        self.optimization_history = []
        
        print("\n初始采样点:")
        initial_points = np.linspace(var_bounds[0], var_bounds[1], n_initial_points)
        for val in initial_points:
            self.objective_function([val])
        
        print("\n使用L-BFGS-B进行局部优化:")
        best_initial_idx = np.argmin([h[1] for h in self.optimization_history])
        x0 = [self.optimization_history[best_initial_idx][0]]
        
        result = minimize(
            self.objective_function,
            x0=x0,
            bounds=[var_bounds],
            method='L-BFGS-B',
            options={'maxiter': 50}
        )
        
        return result.x[0], result.fun
    
    def optimize(self, var_name, var_bounds, objective="max_displacement", method="grid", n_points=100):
        """
        主优化接口
        """
        if method == "grid":
            return self.optimize_grid_search(var_name, var_bounds, objective, n_points)
        elif method == "scipy":
            return self.optimize_scipy(var_name, var_bounds, objective)
        else:
            raise ValueError(f"不支持的优化方法: {method}")
    
    def save_results(self, best_var, best_obj, output_dir="."):
        """
        保存优化结果
        """
        os.makedirs(output_dir, exist_ok=True)
        
        result_file = os.path.join(output_dir, 'optimization_results.txt')
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("FNO模型优化结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"优化目标: 最小化{self._get_objective_description(self.current_objective)}\n")
            f.write(f"设计变量: {self.current_var_name}\n")
            f.write(f"搜索范围: [{min([h[0] for h in self.optimization_history]):.0f}, {max([h[0] for h in self.optimization_history]):.0f}]\n\n")
            f.write(f"最优{self.current_var_name}: {best_var:.0f}\n")
            f.write(f"最优目标值: {best_obj:.6f}\n\n")
            f.write("=" * 60 + "\n")
            f.write("优化历史:\n")
            f.write("=" * 60 + "\n")
            for i, (var, obj) in enumerate(self.optimization_history):
                f.write(f"迭代 {i+1}: {self.current_var_name}={var:.0f}, 目标值={obj:.6f}\n")
        
        print(f"✓ 优化结果已保存: {result_file}")
    
    def _get_objective_description(self, objective):
        """获取目标函数描述"""
        if objective == "max_displacement":
            return "最大位移"
        elif objective == "average_displacement":
            return "平均位移"
        else:
            return objective
    
    def plot_optimization_history(self, output_dir=".", best_var=None, best_obj=None):
        """
        绘制优化历史
        """
        if len(self.optimization_history) < 2:
            print("优化历史数据不足，跳过绘图")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        history = np.array(self.optimization_history)
        var_values = history[:, 0]
        obj_values = history[:, 1]
        
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.scatter(var_values, obj_values, c='blue', alpha=0.6, s=50)
        if best_var is not None and best_obj is not None:
            plt.scatter(best_var, best_obj, c='red', s=100, marker='*', 
                       label=f'最优解\n{self.current_var_name}={best_var:.0f}\n目标值={best_obj:.6f}')
        plt.xlabel(self.current_var_name, fontsize=12)
        plt.ylabel(self._get_objective_description(self.current_objective), fontsize=12)
        plt.title('优化历史', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        sorted_idx = np.argsort(var_values)
        plt.plot(var_values[sorted_idx], obj_values[sorted_idx], 'b-', linewidth=2, marker='o', markersize=4)
        if best_var is not None and best_obj is not None:
            plt.axvline(x=best_var, color='red', linestyle='--', alpha=0.7)
            plt.axhline(y=best_obj, color='red', linestyle='--', alpha=0.7)
        plt.xlabel(self.current_var_name, fontsize=12)
        plt.ylabel(self._get_objective_description(self.current_objective), fontsize=12)
        plt.title('设计变量-目标响应曲线', fontsize=14)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = os.path.join(output_dir, 'optimization_history.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ 优化历史图已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='FNO模型优化工具')
    parser.add_argument('--model_path', type=str, required=True, help='FNO模型文件路径')
    parser.add_argument('--scalers_path', type=str, required=True, help='标准化器文件路径')
    parser.add_argument('--dataset_path', type=str, required=True, help='数据集文件路径')
    parser.add_argument('--output_dir', type=str, default='.', help='输出目录')
    parser.add_argument('--var_name', type=str, default='e_modulus', help='设计变量名称')
    parser.add_argument('--var_min', type=float, default=50000, help='设计变量最小值')
    parser.add_argument('--var_max', type=float, default=250000, help='设计变量最大值')
    parser.add_argument('--objective', type=str, default='max_displacement', 
                       choices=['max_displacement', 'average_displacement'], help='优化目标')
    parser.add_argument('--method', type=str, default='grid', choices=['grid', 'scipy'], 
                       help='优化方法')
    parser.add_argument('--n_points', type=int, default=100, help='网格搜索采样点数')
    
    args = parser.parse_args()
    
    try:
        optimizer = FNOOptimizer(
            model_path=args.model_path,
            scalers_path=args.scalers_path,
            dataset_path=args.dataset_path
        )
        
        var_bounds = (args.var_min, args.var_max)
        best_var, best_obj = optimizer.optimize(
            var_name=args.var_name,
            var_bounds=var_bounds,
            objective=args.objective,
            method=args.method,
            n_points=args.n_points
        )
        
        print("\n" + "=" * 60)
        print("优化完成！")
        print("=" * 60)
        print(f"最优{args.var_name}: {best_var:.0f}")
        print(f"最优目标值: {best_obj:.6f}")
        
        optimizer.save_results(best_var, best_obj, output_dir=args.output_dir)
        optimizer.plot_optimization_history(output_dir=args.output_dir, best_var=best_var, best_obj=best_obj)
        
        print("\n" + "=" * 60)
        print("所有任务完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
