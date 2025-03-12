"""
工作评估系统主程序

使用AutoGen框架和MCP服务器实现的工作评估系统，用于从Git仓库获取团队成员的代码提交信息
并进行工作评估。
"""

import argparse
import asyncio
import os
import sys
import multiprocessing
from typing import Dict, List, Any, Optional

import autogen
from autogen_ext_mcp.tools import mcp_server

from core.config_manager import ConfigManager
from core.git_service import GitService
from core.member_classifier import MemberClassifier
from core.code_analyzer import CodeAnalyzer
from core.report_generator import ReportGenerator


def run_mcp_server():
    """启动MCP服务器"""
    # 导入MCP服务器模块
    from mcp_server.git_server import mcp
    
    print("MCP服务器启动中...")
    # 启动服务器
    mcp.run()


def run_autogen_agents(config_manager: ConfigManager):
    """
    运行AutoGen代理
    
    Args:
        config_manager: 配置管理器实例
    """
    print("AutoGen代理启动中...")
    
    # 获取配置
    agents_config = config_manager.get_agents_config()
    llm_config = {
        "config_list": [{"model": agents_config.get("model_name", "gpt-4"), "api_key": agents_config.get("api_key", "")}],
    }
    
    # 连接到MCP服务器
    tools = mcp_server("http://localhost:8000")
    
    # 创建用户代理
    user_proxy = autogen.UserProxyAgent(
        name="用户",
        system_message="你是用户，需要获取团队成员的代码提交信息并进行工作评估。",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
    )
    
    # 创建助手代理
    assistant = autogen.AssistantAgent(
        name="助手",
        system_message="""你是一个工作评估助手，负责帮助用户获取团队成员的代码提交信息并进行工作评估。
你可以使用以下工具：
1. get_team_members - 获取团队所有成员的列表
2. get_active_repositories - 获取最近活跃的仓库列表
3. get_member_commits - 获取指定团队成员的提交记录
4. get_commit_details - 获取指定提交的详细信息，包括代码修改
""",
        llm_config={"config_list": [{"model": agents_config.get("model_name", "gpt-4"), "api_key": agents_config.get("api_key", "")}]},
        tools=tools,
    )
    
    # 创建代码审查代理
    code_reviewer = autogen.AssistantAgent(
        name="代码审查员",
        system_message="""你是一个专业的代码审查员，负责分析代码提交并评估其质量。
你擅长识别代码中的问题、评估代码质量和提供改进建议。
""",
        llm_config={"config_list": [{"model": agents_config.get("model_name", "gpt-4"), "api_key": agents_config.get("api_key", "")}]},
    )
    
    # 创建效率评估代理
    efficiency_evaluator = autogen.AssistantAgent(
        name="效率评估师",
        system_message="""你是一个专业的效率评估师，负责评估团队成员的工作效率。
你擅长分析工作模式、识别效率瓶颈和提供提高效率的建议。
""",
        llm_config={"config_list": [{"model": agents_config.get("model_name", "gpt-4"), "api_key": agents_config.get("api_key", "")}]},
    )
    
    # 创建代理组
    groupchat = autogen.GroupChat(
        agents=[user_proxy, assistant, code_reviewer, efficiency_evaluator],
        messages=[],
        max_round=50,
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    # 启动对话
    user_proxy.initiate_chat(
        manager,
        message="""
我需要评估我的团队在最近一周的工作情况。请帮我完成以下任务：
1. 获取团队成员列表
2. 获取最近活跃的仓库
3. 获取每个成员的提交记录
4. 分析提交并评估代码质量
5. 为每个成员生成工作报表
6. 评估整个团队的工作效率
""",
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="工作评估系统")
    parser.add_argument("--server-only", action="store_true", help="仅启动MCP服务器")
    parser.add_argument("--agents-only", action="store_true", help="仅运行AutoGen代理")
    parser.add_argument("--config", type=str, default=None, help="配置文件路径")
    args = parser.parse_args()
    
    # 创建配置管理器
    config_manager = ConfigManager(args.config)
    
    if args.server_only:
        # 仅启动MCP服务器
        run_mcp_server()
    elif args.agents_only:
        # 仅运行AutoGen代理
        run_autogen_agents(config_manager)
    else:
        # 同时启动服务器和代理，使用多进程
        print("同时启动MCP服务器和AutoGen代理...")
        
        # 创建MCP服务器进程
        server_process = multiprocessing.Process(target=run_mcp_server)
        server_process.start()
        
        # 等待服务器启动（给服务器一些启动时间）
        print("等待MCP服务器启动...")
        import time
        time.sleep(5)  # 等待5秒，确保服务器已启动
        
        try:
            # 运行AutoGen代理
            run_autogen_agents(config_manager)
        except KeyboardInterrupt:
            print("接收到中断信号，正在关闭...")
        finally:
            # 关闭服务器进程
            if server_process.is_alive():
                print("正在关闭MCP服务器...")
                server_process.terminate()
                server_process.join()
                print("MCP服务器已关闭")


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Windows支持
    main()