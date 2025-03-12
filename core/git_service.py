"""
Git服务模块

负责与Git仓库交互，获取提交信息
"""

import datetime
from datetime import timedelta
from typing import Dict, List, Optional, Any, Union

from core.config_manager import ConfigManager


class GitService:
    """Git服务类，负责与Git仓库交互"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化Git服务
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.github_config = config_manager.get_github_config()
        self.gitlab_config = config_manager.get_gitlab_config()
    
    async def get_active_repositories(self, days: int = None) -> List[Dict[str, Any]]:
        """
        获取最近活跃的仓库列表
        
        Args:
            days: 要查询的天数，默认使用配置中的时间范围
        
        Returns:
            活跃仓库列表
        """
        if days is None:
            days = self.config_manager.get_time_range()
        
        # 这里应该实现实际的API调用
        # 目前返回模拟数据
        return [
            {
                "name": "frontend-app",
                "url": "https://github.com/company/frontend-app",
                "description": "前端应用",
                "last_activity": (datetime.datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                "name": "backend-api",
                "url": "https://github.com/company/backend-api",
                "description": "后端API",
                "last_activity": (datetime.datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                "name": "data-service",
                "url": "https://github.com/company/data-service",
                "description": "数据服务",
                "last_activity": (datetime.datetime.now() - timedelta(days=3)).isoformat()
            }
        ]
    
    async def get_member_commits(self, username: str, days: int = None) -> List[Dict[str, Any]]:
        """
        获取团队成员的提交记录
        
        Args:
            username: 成员用户名
            days: 要查询的天数，默认使用配置中的时间范围
        
        Returns:
            提交记录列表
        """
        if days is None:
            days = self.config_manager.get_time_range()
        
        # 获取成员信息
        team_members = self.config_manager.get_team_members()
        member = next((m for m in team_members if m.get("username") == username), None)
        
        if not member:
            return []
        
        # 这里应该实现实际的API调用
        # 目前返回模拟数据
        now = datetime.datetime.now()
        commits = []
        
        repositories = ["frontend-app", "backend-api", "data-service"]
        
        for i in range(5):  # 模拟5个提交
            date = now - timedelta(days=i % days)
            commits.append({
                "commit_id": f"commit_{username}_{i}",
                "author": member.get("name", username),
                "author_email": member.get("email", f"{username}@example.com"),
                "date": date.isoformat(),
                "message": f"Fix bug #{i+100} in module {i%3}",
                "files_changed": i+1,
                "insertions": i*10+5,
                "deletions": i*2,
                "repository": repositories[i % len(repositories)]
            })
        
        return commits
    
    async def get_team_commits(self, days: int = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取整个团队的提交记录
        
        Args:
            days: 要查询的天数，默认使用配置中的时间范围
        
        Returns:
            按成员分组的提交记录字典
        """
        if days is None:
            days = self.config_manager.get_time_range()
        
        team_members = self.config_manager.get_team_members()
        result = {}
        
        for member in team_members:
            username = member.get("username")
            if username:
                commits = await self.get_member_commits(username, days)
                result[username] = commits
        
        return result
    
    async def get_commit_details(self, commit_id: str) -> Optional[Dict[str, Any]]:
        """
        获取提交的详细信息
        
        Args:
            commit_id: 提交ID
        
        Returns:
            提交详情，如果找不到则返回None
        """
        # 这里应该实现实际的API调用
        # 目前返回模拟数据
        return {
            "commit_id": commit_id,
            "author": "张三",
            "author_email": "zhangsan@example.com",
            "date": datetime.datetime.now().isoformat(),
            "message": "修复登录功能的bug",
            "files_changed": 3,
            "insertions": 25,
            "deletions": 10,
            "repository": "frontend-app",
            "diff": "diff --git a/login.js b/login.js\nindex 1234567..abcdefg 100644\n--- a/login.js\n+++ b/login.js\n@@ -10,7 +10,7 @@\n function validateLogin() {\n-  if (username === '') {\n+  if (username === '' || username === null) {\n     return false;\n   }\n   return true;\n"
        }
    
    async def get_file_content(self, repository: str, path: str, ref: str = "main") -> Optional[str]:
        """
        获取文件内容
        
        Args:
            repository: 仓库名称
            path: 文件路径
            ref: 分支或提交引用
        
        Returns:
            文件内容，如果找不到则返回None
        """
        # 这里应该实现实际的API调用
        # 目前返回模拟数据
        if repository == "frontend-app" and path == "login.js":
            return """
            function login(username, password) {
                if (validateLogin(username, password)) {
                    return authenticateUser(username, password);
                }
                return false;
            }
            
            function validateLogin(username, password) {
                if (username === '' || username === null) {
                    return false;
                }
                return true;
            }
            """
        return None


if __name__ == "__main__":
    # 测试Git服务
    import asyncio
    
    async def test():
        config_manager = ConfigManager()
        git_service = GitService(config_manager)
        
        # 测试获取活跃仓库
        repositories = await git_service.get_active_repositories()
        print("活跃仓库:", repositories)
        
        # 测试获取成员提交
        commits = await git_service.get_member_commits("zhangsan")
        print("张三的提交:", commits)
        
        # 测试获取团队提交
        team_commits = await git_service.get_team_commits()
        print("团队提交:", team_commits)
    
    asyncio.run(test())