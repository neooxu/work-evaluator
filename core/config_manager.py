"""
配置管理器

负责加载和管理系统配置
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConfigManager:
    """配置管理器类"""

    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 ./config/config.yaml
        """
        if config_path is None:
            # 默认配置文件路径
            self.config_path = os.path.join(os.getcwd(), "config", "config.yaml")
        else:
            self.config_path = config_path
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 返回默认配置
            return {
                "general": {
                    "project_name": "工作评估系统",
                    "time_range": 7,
                    "output_dir": "./reports"
                },
                "git_providers": {},
                "team_members": [],
                "agents": {
                    "llm_provider": "openai",
                    "model_name": "gpt-4",
                    "api_key": ""
                },
                "reports": {
                    "format": "markdown",
                    "include_metrics": True,
                    "template_dir": "./config/templates",
                    "individual_reports": True
                },
                "server": {
                    "host": "localhost",
                    "port": 8000,
                    "debug": False,
                    "allowed_origins": ["http://localhost:3000"]
                }
            }
    
    def get_general_config(self) -> Dict[str, Any]:
        """获取通用配置"""
        return self.config.get("general", {})
    
    def get_git_providers(self) -> Dict[str, Any]:
        """获取Git提供者配置"""
        return self.config.get("git_providers", {})
    
    def get_team_members(self) -> List[Dict[str, str]]:
        """获取团队成员配置"""
        return self.config.get("team_members", [])
    
    def get_agents_config(self) -> Dict[str, Any]:
        """获取代理配置"""
        return self.config.get("agents", {})
    
    def get_reports_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        return self.config.get("reports", {})
    
    def get_server_config(self) -> Dict[str, Any]:
        """获取服务器配置"""
        return self.config.get("server", {})
    
    def get_template_path(self, template_name: str) -> str:
        """
        获取模板文件路径
        
        Args:
            template_name: 模板名称
        
        Returns:
            模板文件的完整路径
        """
        template_dir = self.config.get("reports", {}).get("template_dir", "./config/templates")
        return os.path.join(template_dir, template_name)
    
    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self.config.get("general", {}).get("output_dir", "./reports")
    
    def get_time_range(self) -> int:
        """获取时间范围（天数）"""
        return self.config.get("general", {}).get("time_range", 7)
    
    def get_github_config(self) -> Optional[Dict[str, Any]]:
        """获取GitHub配置"""
        return self.config.get("git_providers", {}).get("github")
    
    def get_gitlab_config(self) -> Optional[Dict[str, Any]]:
        """获取GitLab配置"""
        return self.config.get("git_providers", {}).get("gitlab")
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置字典
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            # 更新内存中的配置
            self.config = config
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """
        更新配置的特定部分
        
        Args:
            section: 配置部分名称
            key: 配置键
            value: 新值
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self.save_config(self.config)


if __name__ == "__main__":
    # 测试配置管理器
    config_manager = ConfigManager()
    print("通用配置:", config_manager.get_general_config())
    print("团队成员:", config_manager.get_team_members())
    print("GitHub配置:", config_manager.get_github_config())