"""
Git服务测试模块
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_manager import ConfigManager
from core.git_service import GitService


class TestGitService(unittest.TestCase):
    """Git服务测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建模拟的配置管理器
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.get_time_range.return_value = 7
        self.config_manager.get_github_config.return_value = {
            "token": "mock_token",
            "organization": "mock_org",
            "repositories": ["repo1", "repo2"]
        }
        self.config_manager.get_gitlab_config.return_value = None
        self.config_manager.get_team_members.return_value = [
            {"name": "张三", "email": "zhangsan@example.com", "username": "zhangsan"},
            {"name": "李四", "email": "lisi@example.com", "username": "lisi"}
        ]
        
        # 创建Git服务实例
        self.git_service = GitService(self.config_manager)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.git_service.config_manager, self.config_manager)
        self.assertEqual(self.git_service.github_config, self.config_manager.get_github_config())
        self.assertEqual(self.git_service.gitlab_config, self.config_manager.get_gitlab_config())
    
    def test_get_active_repositories(self):
        """测试获取活跃仓库"""
        # 运行异步测试
        repositories = asyncio.run(self.git_service.get_active_repositories())
        
        # 验证结果
        self.assertIsInstance(repositories, list)
        self.assertTrue(len(repositories) > 0)
        for repo in repositories:
            self.assertIn("name", repo)
            self.assertIn("url", repo)
            self.assertIn("description", repo)
            self.assertIn("last_activity", repo)
    
    def test_get_member_commits(self):
        """测试获取成员提交"""
        # 运行异步测试
        commits = asyncio.run(self.git_service.get_member_commits("zhangsan"))
        
        # 验证结果
        self.assertIsInstance(commits, list)
        self.assertTrue(len(commits) > 0)
        for commit in commits:
            self.assertIn("commit_id", commit)
            self.assertIn("author", commit)
            self.assertIn("author_email", commit)
            self.assertIn("date", commit)
            self.assertIn("message", commit)
            self.assertIn("files_changed", commit)
            self.assertIn("insertions", commit)
            self.assertIn("deletions", commit)
            self.assertIn("repository", commit)
    
    def test_get_team_commits(self):
        """测试获取团队提交"""
        # 运行异步测试
        team_commits = asyncio.run(self.git_service.get_team_commits())
        
        # 验证结果
        self.assertIsInstance(team_commits, dict)
        self.assertIn("zhangsan", team_commits)
        self.assertIn("lisi", team_commits)
        self.assertIsInstance(team_commits["zhangsan"], list)
        self.assertIsInstance(team_commits["lisi"], list)
    
    def test_get_commit_details(self):
        """测试获取提交详情"""
        # 运行异步测试
        commit_details = asyncio.run(self.git_service.get_commit_details("commit_id"))
        
        # 验证结果
        self.assertIsInstance(commit_details, dict)
        self.assertIn("commit_id", commit_details)
        self.assertIn("author", commit_details)
        self.assertIn("author_email", commit_details)
        self.assertIn("date", commit_details)
        self.assertIn("message", commit_details)
        self.assertIn("files_changed", commit_details)
        self.assertIn("insertions", commit_details)
        self.assertIn("deletions", commit_details)
        self.assertIn("repository", commit_details)
        self.assertIn("diff", commit_details)
    
    def test_get_file_content(self):
        """测试获取文件内容"""
        # 运行异步测试
        content = asyncio.run(self.git_service.get_file_content("frontend-app", "login.js"))
        
        # 验证结果
        self.assertIsInstance(content, str)
        self.assertIn("function login", content)
        
        # 测试找不到的文件
        content = asyncio.run(self.git_service.get_file_content("unknown-repo", "unknown-file"))
        self.assertIsNone(content)


if __name__ == "__main__":
    unittest.main()