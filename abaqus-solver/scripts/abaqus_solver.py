import subprocess
import sys
import os
import time
import platform

# 全局变量
ABAQUS_PATH = None


def check_abaqus_installed():
    """检查ABAQUS是否已安装"""
    global ABAQUS_PATH
    
    print("开始检测ABAQUS安装...")
    
    # 方法1：检查用户提供的路径（C:\SIMULIA\Commands\abaqus.bat）
    print("\n方法1: 检查C:/SIMULIA/Commands/abaqus.bat...")
    try:
        abaqus_bat_path = "C:\\SIMULIA\\Commands\\abaqus.bat"
        if os.path.exists(abaqus_bat_path):
            print(f"[SUCCESS] 找到ABAQUS命令脚本: {abaqus_bat_path}")
            ABAQUS_PATH = abaqus_bat_path
            return True
        else:
            print("[ERROR] 未找到C:\\SIMULIA\\Commands\\abaqus.bat")
    except Exception as e:
        print(f"方法1出错: {e}")
    
    # 方法2：检查其他常见的ABAQUS安装路径
    print("\n方法2: 检查其他常见ABAQUS安装路径...")
    try:
        common_paths = []
        if platform.system() == 'Windows':
            # Windows常见安装路径
            common_paths.extend([
                "D:\\SIMULIA\\Commands\\abaqus.bat",
                "C:\\Program Files\\Dassault Systemes\\Commands\\abaqus.bat",
                "D:\\Program Files\\Dassault Systemes\\Commands\\abaqus.bat",
            ])
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"[SUCCESS] 找到ABAQUS命令脚本: {path}")
                ABAQUS_PATH = path
                return True
    except Exception as e:
        print(f"方法2出错: {e}")
    
    # 方法3：尝试运行abaqus命令
    print("\n方法3: 尝试直接运行abaqus命令...")
    try:
        if platform.system() == 'Windows':
            result = subprocess.run('abaqus information=version', 
                                  capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(['abaqus', 'information=version'], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[SUCCESS] ABAQUS命令执行成功")
            ABAQUS_PATH = 'abaqus'  # 使用系统PATH中的abaqus命令
            return True
        else:
            print("[ERROR] ABAQUS命令执行失败")
    except Exception as e:
        print(f"方法3出错: {e}")
    
    # 所有方法都失败
    print("\n[ERROR] ABAQUS未找到，请确保已安装并存在C:/SIMULIA/Commands/abaqus.bat")
    return False


def get_inp_files(path):
    """获取路径中的所有.inp文件"""
    inp_files = []
    
    if os.path.isfile(path):
        # 单个文件
        if path.lower().endswith('.inp'):
            inp_files.append(path)
    elif os.path.isdir(path):
        # 文件夹，查找所有.inp文件
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.inp'):
                    inp_files.append(os.path.join(root, file))
    
    return inp_files


def run_abaqus_job(inp_file):
    """运行单个ABAQUS作业"""
    try:
        # 获取文件名（不含扩展名）作为作业名
        job_name = os.path.splitext(os.path.basename(inp_file))[0]
        # 获取文件目录
        work_dir = os.path.dirname(inp_file)
        
        print(f"正在启动ABAQUS求解器处理: {os.path.basename(inp_file)}")
        print(f"作业名: {job_name}")
        print(f"工作目录: {work_dir}")
        
        # 获取ABAQUS命令路径
        abaqus_cmd = ABAQUS_PATH if ABAQUS_PATH else 'abaqus'
        print(f"使用的ABAQUS命令: {abaqus_cmd}")
        
        if platform.system() == 'Windows':
            # 在Windows系统上，采用先写.bat脚本，再运行.bat脚本的方式
            bat_filename = f"run_abaqus_{job_name}.bat"
            bat_path = os.path.join(work_dir, bat_filename)
            
            # 构建ABAQUS命令
            cmd = f'"{abaqus_cmd}" job={job_name} input={os.path.basename(inp_file)}'
            
            # 写入.bat脚本
            with open(bat_path, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'echo 正在执行ABAQUS计算...\n')
                f.write(f'{cmd}\n')
                f.write(f'echo 计算完成!\n')
            
            print(f"[SUCCESS] 创建了批处理脚本: {bat_path}")
            print(f"执行命令: {cmd}")
            
            # 执行批处理脚本
            process = subprocess.Popen(bat_path, shell=True, cwd=work_dir, 
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     text=True)
        else:
            # 在Linux系统上，直接执行命令
            cmd = f'{abaqus_cmd} job={job_name} input={os.path.basename(inp_file)}'
            print(f"执行命令: {cmd}")
            
            # 执行命令并监控输出
            process = subprocess.Popen(cmd, shell=True, cwd=work_dir, 
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     text=True)
        
        # 监控执行状态
        start_time = time.time()
        output_lines = []
        
        print("计算开始...")
        
        # 读取输出
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                output_lines.append(line)
                print(line)
                # 检查是否有错误信息
                if 'ERROR' in line.upper() or 'WARNING' in line.upper():
                    print(f"注意: {line}")
        
        # 等待进程结束
        process.wait()
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        if process.returncode == 0:
            print(f"计算完成！执行时间: {execution_time:.2f} 秒")
            print(f"结果已保存到: {work_dir}")
            return True, f"计算完成！结果已保存到: {work_dir}"
        else:
            error_msg = "计算失败，请检查输入文件和ABAQUS安装"
            print(error_msg)
            # 打印最后几行输出以便调试
            if output_lines:
                print("最后几行输出:")
                for line in output_lines[-10:]:
                    print(line)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"运行ABAQUS作业时出错: {str(e)}"
        print(error_msg)
        return False, error_msg


def run_abaqus_solver(input_path, skip_check=False, abaqus_path=None):
    """
    运行ABAQUS求解器
    
    Args:
        input_path: .inp文件路径、包含.inp文件的文件夹路径或仿真脚本文件路径
        skip_check: 是否跳过ABAQUS安装检查
        abaqus_path: ABAQUS可执行文件的完整路径（可选）
        
    Returns:
        tuple: (success, message)
    """
    global ABAQUS_PATH
    
    # 保存用户指定的ABAQUS路径
    if abaqus_path:
        ABAQUS_PATH = abaqus_path
        print(f"使用用户指定的ABAQUS路径: {abaqus_path}")
    
    # 检查ABAQUS是否安装（可选）
    if not skip_check:
        if not check_abaqus_installed():
            # 即使检测失败，也尝试继续运行，因为用户可能已经配置好了
            print("\n⚠️  ABAQUS检测失败，但将尝试继续运行...")
    
    print(f"当前ABAQUS_PATH: {ABAQUS_PATH}")
    
    # 检查输入路径是否存在
    if not os.path.exists(input_path):
        return False, f"输入路径不存在: {input_path}"
    
    # 获取.inp文件列表
    inp_files = get_inp_files(input_path)
    
    if not inp_files:
        # 检查是否是脚本文件
        if os.path.isfile(input_path):
            file_ext = os.path.splitext(input_path)[1].lower()
            if file_ext in ['.py', '.bat', '.sh']:
                print(f"检测到脚本文件: {os.path.basename(input_path)}")
                print("正在执行脚本...")
                
                try:
                    # 执行脚本
                    if platform.system() == 'Windows':
                        result = subprocess.run(input_path, shell=True, 
                                              capture_output=True, text=True)
                    else:
                        # 对于Linux，需要确保脚本有执行权限
                        os.chmod(input_path, 0o755)
                        result = subprocess.run(['bash', input_path], 
                                              capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print("脚本执行完成！")
                        return True, "脚本执行完成！"
                    else:
                        error_msg = f"脚本执行失败: {result.stderr}"
                        print(error_msg)
                        return False, error_msg
                        
                except Exception as e:
                    error_msg = f"执行脚本时出错: {str(e)}"
                    print(error_msg)
                    return False, error_msg
        
        return False, "未找到.inp文件或支持的脚本文件"
    
    # 处理找到的.inp文件
    print(f"找到 {len(inp_files)} 个.inp文件")
    
    all_success = True
    messages = []
    
    for i, inp_file in enumerate(inp_files, 1):
        print(f"\n=== 处理第 {i} 个文件 (共 {len(inp_files)} 个) ===")
        success, message = run_abaqus_job(inp_file)
        messages.append(message)
        if not success:
            all_success = False
    
    if all_success:
        if len(inp_files) == 1:
            return True, messages[0]
        else:
            return True, f"所有 {len(inp_files)} 个模型计算完成！"
    else:
        return False, "部分或全部模型计算失败"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python abaqus_solver.py <input_path> [--skip-check] [--abaqus-path <path>]")
        print("其中 input_path 可以是：")
        print("  - 单个.inp文件路径")
        print("  - 包含多个.inp文件的文件夹路径")
        print("  - 仿真脚本文件路径")
        print("可选参数：")
        print("  --skip-check: 跳过ABAQUS安装检查")
        print("  --abaqus-path <path>: 指定ABAQUS可执行文件的完整路径")
        sys.exit(1)
    
    input_path = sys.argv[1]
    skip_check = "--skip-check" in sys.argv
    abaqus_path = None
    
    # 检查是否指定了ABAQUS路径
    if "--abaqus-path" in sys.argv:
        idx = sys.argv.index("--abaqus-path")
        if idx + 1 < len(sys.argv):
            abaqus_path = sys.argv[idx + 1]
            print(f"指定的ABAQUS路径: {abaqus_path}")
    
    print(f"输入路径: {input_path}")
    if skip_check:
        print("跳过ABAQUS安装检查")
    
    success, message = run_abaqus_solver(input_path, skip_check=skip_check, abaqus_path=abaqus_path)
    
    if success:
        print(f"[SUCCESS] {message}")
    else:
        print(f"[ERROR] {message}")
        sys.exit(1)
