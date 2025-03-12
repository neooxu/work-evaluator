"""
MCP服务器启动脚本

用于独立启动MCP服务器，该服务器仅提供Git数据，不进行分析。
MCP服务器提供以下功能：
1. 获取团队所有成员
2. 获取最近一段时间有更新的仓库列表
3. 获取成员在指定时间段内的所有提交，包括代码修改

这些数据将提供给AutoGen框架，由AutoGen调用LLM分析代码更改和提交记录，
从而生成每个人的工作报表和工作效率评估。
"""

import os
import sys

# 确保可以导入项目模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入MCP服务器模块
from mcp_server.git_server import mcp

if __name__ == "__main__":
    print("启动Git数据提供服务器...")
    print("提供以下功能：")
    print("1. 获取团队所有成员")
    print("2. 获取最近一段时间有更新的仓库列表")
    print("3. 获取成员在指定时间段内的所有提交，包括代码修改")
    print("\n服务器启动中，请稍候...\n")
    
    # 启动服务器
    mcp.run()