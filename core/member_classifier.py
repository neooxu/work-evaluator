"""
成员分类器模块

负责将提交按团队成员进行分类
"""

from typing import Dict, List, Any, Optional

from core.config_manager import ConfigManager
from core.git_service import GitService


class MemberClassifier:
    """成员分类器类，负责将提交按团队成员进行分类"""
    
    def __init__(self, config_manager: ConfigManager, git_service: GitService):
        """
        初始化成员分类器
        
        Args:
            config_manager: 配置管理器实例
            git_service: Git服务实例
        """
        self.config_manager = config_manager
        self.git_service = git_service
        self.team_members = config_manager.get_team_members()
    
    async def classify_commits(self, days: int = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        将提交按团队成员进行分类
        
        Args:
            days: 要查询的天数，默认使用配置中的时间范围
        
        Returns:
            按成员分类的提交字典，键为成员用户名，值为提交列表
        """
        # 获取团队所有提交
        team_commits = await self.git_service.get_team_commits(days)
        return team_commits
    
    async def get_member_stats(self, days: int = None) -> Dict[str, Dict[str, Any]]:
        """
        获取每个成员的统计信息
        
        Args:
            days: 要查询的天数，默认使用配置中的时间范围
        
        Returns:
            成员统计信息字典，键为成员用户名，值为统计信息
        """
        classified_commits = await self.classify_commits(days)
        stats = {}
        
        for username, commits in classified_commits.items():
            # 获取成员信息
            member = next((m for m in self.team_members if m.get("username") == username), None)
            if not member:
                continue
            
            # 计算统计信息
            total_commits = len(commits)
            total_files_changed = sum(commit.get("files_changed", 0) for commit in commits)
            total_insertions = sum(commit.get("insertions", 0) for commit in commits)
            total_deletions = sum(commit.get("deletions", 0) for commit in commits)
            repositories = list(set(commit.get("repository", "") for commit in commits))
            
            stats[username] = {
                "member": member,
                "total_commits": total_commits,
                "total_files_changed": total_files_changed,
                "total_insertions": total_insertions,
                "total_deletions": total_deletions,
                "repositories": repositories,
                "commits": commits
            }
        
        return stats
    
    async def get_repository_stats(self, days: int = None) -> Dict[str, Dict[str, Any]]:
        """
        获取每个仓库的统计信息
        
        Args:
            days: 要查询的天数，默认使用配置中的时间范围
        
        Returns:
            仓库统计信息字典，键为仓库名称，值为统计信息
        """
        classified_commits = await self.classify_commits(days)
        all_commits = []
        
        for commits in classified_commits.values():
            all_commits.extend(commits)
        
        # 按仓库分组
        repo_commits = {}
        for commit in all_commits:
            repo = commit.get("repository", "")
            if repo not in repo_commits:
                repo_commits[repo] = []
            repo_commits[repo].append(commit)
        
        # 计算每个仓库的统计信息
        stats = {}
        for repo, commits in repo_commits.items():
            total_commits = len(commits)
            total_files_changed = sum(commit.get("files_changed", 0) for commit in commits)
            total_insertions = sum(commit.get("insertions", 0) for commit in commits)
            total_deletions = sum(commit.get("deletions", 0) for commit in commits)
            
            # 计算每个成员在该仓库的提交数
            member_commits = {}
            for commit in commits:
                author = commit.get("author", "")
                if author not in member_commits:
                    member_commits[author] = 0
                member_commits[author] += 1
            
            stats[repo] = {
                "total_commits": total_commits,
                "total_files_changed": total_files_changed,
                "total_insertions": total_insertions,
                "total_deletions": total_deletions,
                "member_commits": member_commits,
                "commits": commits
            }
        
        return stats


if __name__ == "__main__":
    # 测试成员分类器
    import asyncio
    
    async def test():
        config_manager = ConfigManager()
        git_service = GitService(config_manager)
        classifier = MemberClassifier(config_manager, git_service)
        
        # 测试分类提交
        classified_commits = await classifier.classify_commits()
        print("分类后的提交:", classified_commits)
        
        # 测试获取成员统计信息
        member_stats = await classifier.get_member_stats()
        print("成员统计信息:", member_stats)
        
        # 测试获取仓库统计信息
        repo_stats = await classifier.get_repository_stats()
        print("仓库统计信息:", repo_stats)
    
    asyncio.run(test())