"""
代码分析器模块

负责分析代码变更，评估代码质量和复杂度
"""

import json
from typing import Dict, List, Any, Optional

from core.config_manager import ConfigManager
from core.git_service import GitService
from core.member_classifier import MemberClassifier


class CodeAnalyzer:
    """代码分析器类，负责分析代码变更"""
    
    def __init__(self, config_manager: ConfigManager, git_service: GitService, classifier: MemberClassifier):
        """
        初始化代码分析器
        
        Args:
            config_manager: 配置管理器实例
            git_service: Git服务实例
            classifier: 成员分类器实例
        """
        self.config_manager = config_manager
        self.git_service = git_service
        self.classifier = classifier
        self.llm_config = config_manager.get_agents_config()
    
    async def analyze_commit(self, commit_id: str) -> Dict[str, Any]:
        """
        分析单个提交
        
        Args:
            commit_id: 提交ID
        
        Returns:
            分析结果
        """
        # 获取提交详情
        commit_details = await self.git_service.get_commit_details(commit_id)
        if not commit_details:
            return {
                "commit_id": commit_id,
                "error": "找不到提交详情"
            }
        
        # 在实际实现中，这里应该调用LLM分析代码变更
        # 目前返回模拟数据
        return {
            "commit_id": commit_id,
            "quality_score": 0.85,
            "complexity_score": 0.65,
            "impact_score": 0.75,
            "comments": [
                "代码结构清晰",
                "变量命名规范",
                "缺少单元测试",
                "有潜在的性能问题"
            ]
        }
    
    async def analyze_member_commits(self, username: str, days: int = None) -> Dict[str, Any]:
        """
        分析成员的所有提交
        
        Args:
            username: 成员用户名
            days: 要分析的天数，默认使用配置中的时间范围
        
        Returns:
            分析结果
        """
        # 获取成员统计信息
        member_stats = await self.classifier.get_member_stats(days)
        if username not in member_stats:
            return {
                "username": username,
                "error": "找不到成员信息或该成员没有提交"
            }
        
        stats = member_stats[username]
        commits = stats["commits"]
        
        # 分析每个提交
        commit_analyses = []
        for commit in commits:
            commit_id = commit.get("commit_id", "")
            analysis = await self.analyze_commit(commit_id)
            commit_analyses.append(analysis)
        
        # 计算平均分数
        avg_quality = sum(analysis.get("quality_score", 0) for analysis in commit_analyses) / len(commit_analyses) if commit_analyses else 0
        avg_complexity = sum(analysis.get("complexity_score", 0) for analysis in commit_analyses) / len(commit_analyses) if commit_analyses else 0
        avg_impact = sum(analysis.get("impact_score", 0) for analysis in commit_analyses) / len(commit_analyses) if commit_analyses else 0
        
        # 在实际实现中，这里应该调用LLM生成整体评估
        # 目前返回模拟数据
        return {
            "username": username,
            "member": stats["member"],
            "total_commits": stats["total_commits"],
            "total_files_changed": stats["total_files_changed"],
            "total_insertions": stats["total_insertions"],
            "total_deletions": stats["total_deletions"],
            "repositories": stats["repositories"],
            "avg_quality_score": avg_quality,
            "avg_complexity_score": avg_complexity,
            "avg_impact_score": avg_impact,
            "productivity_score": 0.78,  # 模拟数据
            "code_quality_score": avg_quality,
            "commit_frequency": stats["total_commits"] / (days or self.config_manager.get_time_range()),
            "strengths": [
                "代码质量高",
                "提交信息清晰",
                "解决问题速度快"
            ],
            "improvement_areas": [
                "可以增加单元测试覆盖率",
                "部分代码可以进一步优化"
            ],
            "recommendations": [
                "建议参加代码审查培训",
                "可以尝试使用更多设计模式",
                "考虑编写更详细的文档"
            ],
            "commit_analyses": commit_analyses
        }
    
    async def analyze_team(self, days: int = None) -> Dict[str, Any]:
        """
        分析整个团队
        
        Args:
            days: 要分析的天数，默认使用配置中的时间范围
        
        Returns:
            分析结果
        """
        # 获取所有成员的统计信息
        member_stats = await self.classifier.get_member_stats(days)
        
        # 获取所有仓库的统计信息
        repo_stats = await self.classifier.get_repository_stats(days)
        
        # 分析每个成员
        member_analyses = {}
        for username in member_stats:
            analysis = await self.analyze_member_commits(username, days)
            member_analyses[username] = analysis
        
        # 计算团队整体指标
        total_commits = sum(stats["total_commits"] for stats in member_stats.values())
        avg_productivity = sum(analysis.get("productivity_score", 0) for analysis in member_analyses.values()) / len(member_analyses) if member_analyses else 0
        avg_quality = sum(analysis.get("code_quality_score", 0) for analysis in member_analyses.values()) / len(member_analyses) if member_analyses else 0
        
        # 在实际实现中，这里应该调用LLM生成团队评估
        # 目前返回模拟数据
        return {
            "time_period": f"最近{days or self.config_manager.get_time_range()}天",
            "team_size": len(member_stats),
            "total_commits": total_commits,
            "average_productivity_score": avg_productivity,
            "average_code_quality_score": avg_quality,
            "commit_distribution": {username: stats["total_commits"] for username, stats in member_stats.items()},
            "top_active_repositories": sorted(repo_stats.keys(), key=lambda r: repo_stats[r]["total_commits"], reverse=True),
            "team_strengths": [
                "协作效率高",
                "代码质量整体良好",
                "问题解决速度快"
            ],
            "improvement_suggestions": [
                "可以增加代码审查频率",
                "建议统一编码规范",
                "考虑引入更多自动化测试"
            ],
            "member_analyses": member_analyses,
            "repository_stats": repo_stats
        }


if __name__ == "__main__":
    # 测试代码分析器
    import asyncio
    
    async def test():
        config_manager = ConfigManager()
        git_service = GitService(config_manager)
        classifier = MemberClassifier(config_manager, git_service)
        analyzer = CodeAnalyzer(config_manager, git_service, classifier)
        
        # 测试分析提交
        commit_analysis = await analyzer.analyze_commit("commit_zhangsan_0")
        print("提交分析:", json.dumps(commit_analysis, ensure_ascii=False, indent=2))
        
        # 测试分析成员
        member_analysis = await analyzer.analyze_member_commits("zhangsan")
        print("成员分析:", json.dumps(member_analysis, ensure_ascii=False, indent=2))
        
        # 测试分析团队
        team_analysis = await analyzer.analyze_team()
        print("团队分析:", json.dumps(team_analysis, ensure_ascii=False, indent=2))
    
    asyncio.run(test())