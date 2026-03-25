#!/usr/bin/env python
"""
FNO模型优化交互式界面
通过对话方式配置优化参数
"""

import os
import sys


def get_input(prompt, default=None):
    """获取用户输入，带默认值"""
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    user_input = input(prompt).strip()
    
    if not user_input and default is not None:
        return default
    return user_input


def get_float_input(prompt, default=None, min_val=None, max_val=None):
    """获取浮点数输入"""
    while True:
        user_input = get_input(prompt, default)
        
        if user_input == "":
            return default
        
        try:
            val = float(user_input)
            
            if min_val is not None and val < min_val:
                print(f"  错误：值不能小于 {min_val}")
                continue
            
            if max_val is not None and val > max_val:
                print(f"  错误：值不能大于 {max_val}")
                continue
            
            return val
        except ValueError:
            print("  错误：请输入有效的数字")


def get_choice_input(prompt, choices, default=None):
    """获取选择输入"""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        if choice == default:
            print(f"  {i}. {choice} [默认]")
        else:
            print(f"  {i}. {choice}")
    
    while True:
        user_input = get_input("请选择", str(choices.index(default) + 1) if default else None)
        
        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            if user_input in choices:
                return user_input
        
        print("  错误：请选择有效的选项")


def confirm(prompt, default=True):
    """确认提示"""
    default_str = "Y/n" if default else "y/N"
    user_input = get_input(f"{prompt} [{default_str}]", "y" if default else "n").lower()
    
    return user_input in ["y", "yes", ""]


def main():
    print("=" * 60)
    print("FNO模型优化工具 - 交互式配置")
    print("=" * 60)
    print("\n本工具将引导您配置优化参数。")
    print("按Enter键可使用方括号[]中的默认值。\n")
    
    # 1. 模型文件路径
    print("-" * 60)
    print("第1步：配置模型文件")
    print("-" * 60)
    
    model_path = get_input("请输入FNO模型文件路径(.pkl)", "D:\\test\\20260303\\fno_model.pkl")
    
    while not os.path.exists(model_path):
        print(f"  错误：文件不存在：{model_path}")
        model_path = get_input("请输入FNO模型文件路径(.pkl)")
    
    print(f"  ✓ 模型文件：{model_path}")
    
    # 2. 标准化器文件路径
    print("\n" + "-" * 60)
    print("第2步：配置标准化器文件")
    print("-" * 60)
    
    default_scalers = os.path.join(os.path.dirname(model_path), "scalers.npz")
    scalers_path = get_input("请输入标准化器文件路径(.npz)", default_scalers)
    
    while not os.path.exists(scalers_path):
        print(f"  错误：文件不存在：{scalers_path}")
        scalers_path = get_input("请输入标准化器文件路径(.npz)")
    
    print(f"  ✓ 标准化器文件：{scalers_path}")
    
    # 3. 数据集文件路径
    print("\n" + "-" * 60)
    print("第3步：配置数据集文件")
    print("-" * 60)
    
    default_dataset = os.path.join(os.path.dirname(model_path), "fno_dataset.npz")
    dataset_path = get_input("请输入数据集文件路径(.npz)", default_dataset)
    
    while not os.path.exists(dataset_path):
        print(f"  错误：文件不存在：{dataset_path}")
        dataset_path = get_input("请输入数据集文件路径(.npz)")
    
    print(f"  ✓ 数据集文件：{dataset_path}")
    
    # 4. 设计变量配置
    print("\n" + "-" * 60)
    print("第4步：配置设计变量")
    print("-" * 60)
    
    var_name = get_input("请输入设计变量名称", "e_modulus")
    var_min = get_float_input("请输入设计变量最小值", 50000.0)
    var_max = get_float_input("请输入设计变量最大值", 250000.0, min_val=var_min)
    
    print(f"  ✓ 设计变量：{var_name}")
    print(f"  ✓ 变量范围：[{var_min}, {var_max}]")
    
    # 5. 优化目标
    print("\n" + "-" * 60)
    print("第5步：选择优化目标")
    print("-" * 60)
    
    objectives = [
        "max_displacement - 最小化最大位移",
        "average_displacement - 最小化平均位移"
    ]
    
    objective_choice = get_choice_input("请选择优化目标", objectives, objectives[0])
    objective = objective_choice.split(" - ")[0]
    
    print(f"  ✓ 优化目标：{objective_choice}")
    
    # 6. 优化算法
    print("\n" + "-" * 60)
    print("第6步：选择优化算法")
    print("-" * 60)
    
    methods = [
        "grid - 网格搜索（推荐，鲁棒性强）",
        "scipy - SciPy L-BFGS-B（快速局部优化）"
    ]
    
    method_choice = get_choice_input("请选择优化算法", methods, methods[0])
    method = method_choice.split(" - ")[0]
    
    print(f"  ✓ 优化算法：{method_choice}")
    
    # 7. 网格搜索参数（如果选择了网格搜索）
    n_points = 100
    if method == "grid":
        print("\n" + "-" * 60)
        print("第7步：配置网格搜索参数")
        print("-" * 60)
        n_points = int(get_float_input("请输入网格搜索采样点数", 100.0, min_val=10.0, max_val=500.0))
        print(f"  ✓ 采样点数：{n_points}")
    
    # 8. 输出目录
    print("\n" + "-" * 60)
    print("第8步：配置输出目录")
    print("-" * 60)
    
    default_output = os.path.dirname(model_path)
    output_dir = get_input("请输入输出目录", default_output)
    
    print(f"  ✓ 输出目录：{output_dir}")
    
    # 总结配置
    print("\n" + "=" * 60)
    print("配置总结")
    print("=" * 60)
    print(f"  模型文件：{model_path}")
    print(f"  标准化器：{scalers_path}")
    print(f"  数据集：{dataset_path}")
    print(f"  设计变量：{var_name}")
    print(f"  变量范围：[{var_min}, {var_max}]")
    print(f"  优化目标：{objective_choice}")
    print(f"  优化算法：{method_choice}")
    if method == "grid":
        print(f"  采样点数：{n_points}")
    print(f"  输出目录：{output_dir}")
    print("=" * 60)
    
    if not confirm("\n确认以上配置并开始优化？"):
        print("\n已取消优化。")
        return 0
    
    # 导入优化模块并运行
    print("\n" + "=" * 60)
    print("开始优化...")
    print("=" * 60)
    
    try:
        # 添加scripts目录到路径
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, scripts_dir)
        
        from optimize import FNOOptimizer
        
        optimizer = FNOOptimizer(
            model_path=model_path,
            scalers_path=scalers_path,
            dataset_path=dataset_path
        )
        
        var_bounds = (var_min, var_max)
        best_var, best_obj = optimizer.optimize(
            var_name=var_name,
            var_bounds=var_bounds,
            objective=objective,
            method=method,
            n_points=n_points
        )
        
        print("\n" + "=" * 60)
        print("优化完成！")
        print("=" * 60)
        print(f"最优{var_name}: {best_var:.0f}")
        print(f"最优目标值: {best_obj:.6f}")
        
        optimizer.save_results(best_var, best_obj, output_dir=output_dir)
        optimizer.plot_optimization_history(output_dir=output_dir, best_var=best_var, best_obj=best_obj)
        
        print("\n" + "=" * 60)
        print("所有任务完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
