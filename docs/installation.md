# 安装指南

本文档介绍如何安装和配置工作评估系统。

## 系统要求

- Python 3.10 或更高版本
- Git
- 访问 GitHub/GitLab API 的权限

## 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/work-evaluator.git
cd work-evaluator
```

2. 创建并激活虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

## 配置

1. 复制示例配置文件：

```bash
cp config/config.yaml.example config/config.yaml
```

2. 编辑配置文件，填入您的 Git 提供者信息和团队成员信息：

```yaml
# Git提供者配置
git_providers:
  github:
    token: "your_github_token"  # 请替换为实际的GitHub API令牌
    organization: "your_organization"  # 请替换为实际的组织名称
    repositories:  # 要监控的仓库列表，留空表示监控组织下所有仓库
      - "repo1"
      - "repo2"

# 团队成员配置
team_members:
  - name: "张三"
    email: "zhangsan@example.com"
    username: "zhangsan"
  
  - name: "李四"
    email: "lisi@example.com"
    username: "lisi"
```

3. 配置 LLM API 密钥：

```yaml
# 代理配置
agents:
  llm_provider: "openai"  # 使用的LLM提供者
  model_name: "gpt-4"     # 使用的模型名称
  api_key: "your_openai_api_key"  # 请替换为实际的API密钥
```

## 验证安装

运行以下命令验证安装是否成功：

```bash
python -m server
```

如果一切正常，您应该会看到 MCP 服务器启动的消息。