"""
MCP服务器测试模块
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入MCP服务器模块
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_server"))
from mcp_server.git_server import mcp


class TestMCPServer(unittest.TestCase):
    """MCP服务器测试类"""
    
    def test_server_name(self):
        """测试服务器名称"""
        self.assertEqual(mcp.name, "Git数据提供服务器")
    
    def test_server_instructions(self):
        """测试服务器说明"""
        self.assertEqual(mcp.instructions, "这个服务器提供了与Git仓库交互的工具，用于获取团队成员的代码提交信息和代码修改。它不进行任何分析，只提供原始数据。")
    
    @patch("mcp_server.git_server.get_team_members")
    async def test_get_team_members_tool(self, mock_get_team_members):
        """测试获取团队成员工具"""
        # 设置模拟返回值
        mock_get_team_members.return_value = [
            {"name": "张三", "email": "zhangsan@example.com", "username": "zhangsan"},
            {"name": "李四", "email": "lisi@example.com", "username": "lisi"}
        ]
        
        # 调用工具
        result = await mcp._tool_manager.call_tool("get_team_members", {})
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "张三")
        self.assertEqual(result[1]["name"], "李四")
    
    @patch("mcp_server.git_server.get_active_repositories")
    async def test_get_active_repositories_tool(self, mock_get_active_repositories):
        """测试获取活跃仓库工具"""
        # 设置模拟返回值
        mock_get_active_repositories.return_value = [
            {"name": "repo1", "url": "https://github.com/org/repo1"},
            {"name": "repo2", "url": "https://github.com/org/repo2"}
        ]
        
        # 调用工具
        result = await mcp._tool_manager.call_tool("get_active_repositories", {"days": 7})
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "repo1")
        self.assertEqual(result[1]["name"], "repo2")
    
    @patch("mcp_server.git_server.get_member_commits")
    async def test_get_member_commits_tool(self, mock_get_member_commits):
        """测试获取成员提交工具"""
        # 设置模拟返回值
        mock_get_member_commits.return_value = [
            {"commit_id": "commit1", "message": "Fix bug", "code_changes": [{"file": "test.js", "changes": "@@ -1,1 +1,1 @@\n-old\n+new"}]},
            {"commit_id": "commit2", "message": "Add feature", "code_changes": [{"file": "main.js", "changes": "@@ -5,1 +5,3 @@\n line\n+new line 1\n+new line 2"}]}
        ]
        
        # 调用工具
        result = await mcp._tool_manager.call_tool("get_member_commits", {"username": "zhangsan", "days": 7})
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["commit_id"], "commit1")
        self.assertEqual(result[1]["commit_id"], "commit2")
        self.assertIn("code_changes", result[0])
        self.assertIn("code_changes", result[1])
    
    @patch("mcp_server.git_server.get_commit_details")
    async def test_get_commit_details_tool(self, mock_get_commit_details):
        """测试获取提交详情工具"""
        # 设置模拟返回值
        mock_get_commit_details.return_value = {
            "commit_id": "commit1",
            "author": "张三",
            "message": "Fix bug in module",
            "code_changes": [
                {"file": "src/main.py", "changes": "@@ -10,7 +10,7 @@\n-old\n+new"}
            ]
        }
        
        # 调用工具
        result = await mcp._tool_manager.call_tool("get_commit_details", {"commit_id": "commit1"})
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertEqual(result["commit_id"], "commit1")
        self.assertEqual(result["author"], "张三")
        self.assertIn("code_changes", result)
        self.assertEqual(len(result["code_changes"]), 1)
        self.assertEqual(result["code_changes"][0]["file"], "src/main.py")


def run_async_test(test_case):
    """运行异步测试"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_case)


if __name__ == "__main__":
    unittest.main()