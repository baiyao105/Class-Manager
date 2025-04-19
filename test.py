import os
import subprocess
import argparse

def run_pylint(filepath: str):
    print(f"\n🔍 [Pylint] 分析中: {filepath}")
    #result = subprocess.run(["pylint", filepath], capture_output=True, text=True)
    #print(result.stdout)

def clean_python_file(filepath: str, dry_run=False):
    print(f"\n🧹 正在处理: {filepath}")

    if dry_run:
        run_pylint(filepath)
        print("🚫 dry-run 模式，不进行实际修改")
    else:
        # 清理未使用的导入和变量
        subprocess.run([
            "autoflake",
            "--in-place",
            "--remove-unused-variables",
            "--remove-all-unused-imports",
            filepath
        ])
        # 格式化代码风格
        subprocess.run(["black", filepath])
        run_pylint(filepath)

def clean_directory(directory: str, dry_run=False):
    print(f"📁 处理目录：{directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                clean_python_file(os.path.join(root, file), dry_run=dry_run)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🐍 自动清理 + 分析 Python 代码的小工具")
    parser.add_argument("path", help="Python 文件或目录")
    parser.add_argument("--dry-run", action="store_true", help="🧪 只运行分析，不修改文件")
    args = parser.parse_args()

    if os.path.isdir(args.path):
        clean_directory(args.path, dry_run=args.dry_run)
    elif os.path.isfile(args.path) and args.path.endswith(".py"):
        clean_python_file(args.path, dry_run=args.dry_run)
    else:
        print("❌ 无效路径，请输入 Python 文件或目录")
