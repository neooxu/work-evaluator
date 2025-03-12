"""
报告生成器模块

负责生成工作报表
"""

import datetime
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.config_manager import ConfigManager
from core.code_analyzer import CodeAnalyzer


class ReportGenerator:
    """报告生成器类，负责生成工作报表"""
    
    def __init__(self, config_manager: ConfigManager, code_analyzer: CodeAnalyzer):
        """
        初始化报告生成器
        
        Args:
            config_manager: 配置管理器实例
            code_analyzer: 代码分析器实例
        """
        self.config_manager = config_manager
        self.code_analyzer = code_analyzer
        self.reports_config = config_manager.get_reports_config()
        self.output_dir = config_manager.get_output_dir()
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _format_score(self, score: float) -> str:
        """格式化分数为百分比"""
        return f"{score * 100:.1f}%"
    
    def _format_number(self, number: float) -> str:
        """格式化数字，保留一位小数"""
        return f"{number:.1f}"
    
    async def generate_member_report(self, username: str, days: int = None) -> Dict[str, Any]:
        """
        生成成员工作报表
        
        Args:
            username: 成员用户名
            days: 要分析的天数，默认使用配置中的时间范围
        
        Returns:
            报表数据
        """
        # 分析成员提交
        analysis = await self.code_analyzer.analyze_member_commits(username, days)
        if "error" in analysis:
            return analysis
        
        # 准备报表数据
        now = datetime.datetime.now()
        time_range = days or self.config_manager.get_time_range()
        start_date = (now - datetime.timedelta(days=time_range)).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        
        report_data = {
            "member": analysis["member"],
            "time_period": f"{start_date} 至 {end_date}",
            "total_commits": analysis["total_commits"],
            "total_files_changed": analysis["total_files_changed"],
            "total_insertions": analysis["total_insertions"],
            "total_deletions": analysis["total_deletions"],
            "repositories": analysis["repositories"],
            "productivity_score": analysis["productivity_score"],
            "code_quality_score": analysis["code_quality_score"],
            "commit_frequency": analysis["commit_frequency"],
            "strengths": analysis["strengths"],
            "improvement_areas": analysis["improvement_areas"],
            "recommendations": analysis["recommendations"],
            "commits": analysis.get("commits", []),
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "format_score": self._format_score,
            "format_number": self._format_number
        }
        
        # 保存报表数据
        if self.reports_config.get("individual_reports", True):
            output_path = os.path.join(self.output_dir, f"{username}_report.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_data
    
    async def generate_team_report(self, days: int = None) -> Dict[str, Any]:
        """
        生成团队工作报表
        
        Args:
            days: 要分析的天数，默认使用配置中的时间范围
        
        Returns:
            报表数据
        """
        # 分析团队
        analysis = await self.code_analyzer.analyze_team(days)
        
        # 准备报表数据
        now = datetime.datetime.now()
        
        report_data = {
            "time_period": analysis["time_period"],
            "team_size": analysis["team_size"],
            "total_commits": analysis["total_commits"],
            "average_productivity_score": analysis["average_productivity_score"],
            "average_code_quality_score": analysis["average_code_quality_score"],
            "commit_distribution": analysis["commit_distribution"],
            "top_active_repositories": analysis["top_active_repositories"],
            "team_strengths": analysis["team_strengths"],
            "improvement_suggestions": analysis["improvement_suggestions"],
            "member_reports": [analysis["member_analyses"][username] for username in analysis["member_analyses"]],
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "format_score": self._format_score,
            "format_number": self._format_number
        }
        
        # 保存报表数据
        output_path = os.path.join(self.output_dir, "team_report.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_data
    
    async def render_member_report(self, username: str, days: int = None, format: str = None) -> str:
        """
        渲染成员工作报表
        
        Args:
            username: 成员用户名
            days: 要分析的天数，默认使用配置中的时间范围
            format: 报表格式，默认使用配置中的格式
        
        Returns:
            渲染后的报表内容
        """
        # 获取报表数据
        report_data = await self.generate_member_report(username, days)
        if "error" in report_data:
            return f"生成报表失败: {report_data['error']}"
        
        # 确定报表格式
        if format is None:
            format = self.reports_config.get("format", "markdown")
        
        # 渲染报表
        if format == "markdown":
            template_path = self.config_manager.get_template_path("member_report_template.md")
            if not os.path.exists(template_path):
                return f"找不到模板文件: {template_path}"
            
            # 在实际实现中，这里应该使用模板引擎渲染报表
            # 目前返回模拟数据
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            # 简单替换一些变量
            report = template
            report = report.replace("{{member.name}}", report_data["member"]["name"])
            report = report.replace("{{time_period}}", report_data["time_period"])
            report = report.replace("{{total_commits}}", str(report_data["total_commits"]))
            report = report.replace("{{total_files_changed}}", str(report_data["total_files_changed"]))
            report = report.replace("{{total_insertions}}", str(report_data["total_insertions"]))
            report = report.replace("{{total_deletions}}", str(report_data["total_deletions"]))
            report = report.replace("{{repositories|join(', ')}}", ", ".join(report_data["repositories"]))
            report = report.replace("{{productivity_score|format_score}}", self._format_score(report_data["productivity_score"]))
            report = report.replace("{{code_quality_score|format_score}}", self._format_score(report_data["code_quality_score"]))
            report = report.replace("{{commit_frequency|format_number}}", self._format_number(report_data["commit_frequency"]))
            report = report.replace("{{generated_at}}", report_data["generated_at"])
            
            # 保存渲染后的报表
            output_path = os.path.join(self.output_dir, f"{username}_report.md")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            
            return report
        else:
            return f"不支持的报表格式: {format}"
    
    async def render_team_report(self, days: int = None, format: str = None) -> str:
        """
        渲染团队工作报表
        
        Args:
            days: 要分析的天数，默认使用配置中的时间范围
            format: 报表格式，默认使用配置中的格式
        
        Returns:
            渲染后的报表内容
        """
        # 获取报表数据
        report_data = await self.generate_team_report(days)
        
        # 确定报表格式
        if format is None:
            format = self.reports_config.get("format", "markdown")
        
        # 渲染报表
        if format == "markdown":
            template_path = self.config_manager.get_template_path("team_report_template.md")
            if not os.path.exists(template_path):
                return f"找不到模板文件: {template_path}"
            
            # 在实际实现中，这里应该使用模板引擎渲染报表
            # 目前返回模拟数据
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            # 简单替换一些变量
            report = template
            report = report.replace("{{time_period}}", report_data["time_period"])
            report = report.replace("{{team_size}}", str(report_data["team_size"]))
            report = report.replace("{{total_commits}}", str(report_data["total_commits"]))
            report = report.replace("{{average_productivity_score|format_score}}", self._format_score(report_data["average_productivity_score"]))
            report = report.replace("{{average_code_quality_score|format_score}}", self._format_score(report_data["average_code_quality_score"]))
            report = report.replace("{{generated_at}}", report_data["generated_at"])
            
            # 保存渲染后的报表
            output_path = os.path.join(self.output_dir, "team_report.md")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            
            return report
        else:
            return f"不支持的报表格式: {format}"


if __name__ == "__main__":
    # 测试报告生成器
    import asyncio
    from core.git_service import GitService
    from core.member_classifier import MemberClassifier
    
    async def test():
        config_manager = ConfigManager()
        git_service = GitService(config_manager)
        classifier = MemberClassifier(config_manager, git_service)
        analyzer = CodeAnalyzer(config_manager, git_service, classifier)
        generator = ReportGenerator(config_manager, analyzer)
        
        # 测试生成成员报表
        member_report = await generator.render_member_report("zhangsan")
        print("成员报表:", member_report[:500] + "...")  # 只打印前500个字符
        
        # 测试生成团队报表
        team_report = await generator.render_team_report()
        print("团队报表:", team_report[:500] + "...")  # 只打印前500个字符
    
    asyncio.run(test())