"""
测试 git_server.py 中的 MCP 服务器

这个脚本演示如何使用 MCP 客户端连接到 git_server.py 提供的 MCP 服务器，
并调用其提供的工具和资源。
"""

import asyncio
import json
from mcp.client import Client

async def main():
    # 连接到 MCP 服务器
    print("正在连接到 MCP 服务器...")
    client = Client("http://localhost:8000")
    
    # 获取服务器信息
    info = await client.get_info()
    print(f"服务器名称: {info.name}")
    print(f"服务器说明: {info.instructions}")
    
    # 获取可用工具列表
    tools = await client.list_tools()
    print("\n可用工具:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # 获取可用资源列表
    resources = await client.list_resources()
    print("\n可用资源:")
    for resource in resources:
        print(f"- {resource}")
    
    # 测试获取团队成员信息
    print("\n获取团队成员信息:")
    team_members = await client.get_resource("team://members")
    members = json.loads(team_members)
    for member in members:
        print(f"- {member['name']} ({member['email']})")
    
    # 测试获取仓库信息
    print("\n获取仓库信息:")
    repositories = await client.get_resource("repositories://active")
    repos = json.loads(repositories)
    for repo in repos:
        print(f"- {repo['name']}: {repo['url']}")
    
    # 测试获取成员提交信息
    print("\n获取成员提交信息:")
    try:
        # 假设有一个用户名为 'developer1'
        commits = await client.get_resource("commits://developer1")
        commits_data = json.loads(commits)
        for commit in commits_data:
            print(f"- {commit['commit_id'][:7]}: {commit['message']} ({commit['date']})")
    except Exception as e:
        print(f"获取提交信息时出错: {e}")
    
    # 测试获取提交详情
    print("\n获取提交详情:")
    try:
        # 调用 get_commit_details 工具
        commit_details = await client.invoke_tool(
            "get_commit_details",
            {"commit_id": "abc123", "repository": "project1"}
        )
        print(f"提交详情: {commit_details}")
    except Exception as e:
        print(f"获取提交详情时出错: {e}")
    
    # 测试获取成员工作评估
    print("\n获取成员工作评估:")
    try:
        # 调用 evaluate_member_work 工具
        evaluation = await client.invoke_tool(
            "evaluate_member_work",
            {"username": "developer1", "days": 7}
        )
        print(f"工作评估: {evaluation}")
    except Exception as e:
        print(f"获取工作评估时出错: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 