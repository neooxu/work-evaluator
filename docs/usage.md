# 使用指南

本文档介绍如何使用工作评估系统。

## 启动服务器

有两种方式启动系统：

### 1. 仅启动 MCP 服务器

```bash
python server.py
```

这将启动 MCP 服务器，您可以通过 MCP 兼容的客户端（如 Cursor 编辑器）连接到它。

### 2. 启动完整系统

```bash
python main.py
```

这将启动 MCP 服务器并运行 AutoGen 代理。

### 3. 仅运行 AutoGen 代理

```bash
python main.py --agents-only
```

这将仅运行 AutoGen 代理，假设 MCP 服务器已经在运行。

## 使用 MCP 服务器

MCP 服务器提供以下工具和资源：

### 工具

1. `get_team_members` - 获取团队所有成员的列表
2. `get_active_repositories` - 获取最近活跃的仓库列表
3. `get_member_commits` - 获取指定团队成员的提交记录
4. `analyze_commit` - 分析指定的代码提交
5. `generate_member_report` - 为指定团队成员生成工作报表
6. `evaluate_team_efficiency` - 评估整个团队的工作效率

### 资源

1. `team://members` - 团队成员信息
2. `repositories://active` - 活跃仓库信息
3. `commits://{username}` - 指定成员的提交信息
4. `report://{username}` - 指定成员的工作报表

### 提示

1. `analyze_member_work` - 分析成员工作的提示
2. `evaluate_team_prompt` - 团队效率评估的提示

## 使用 AutoGen 代理

AutoGen 代理系统包含以下代理：

1. 用户代理 - 代表用户发起请求
2. 助手代理 - 协调整个工作流程
3. 代码审查代理 - 专门负责代码审查
4. 效率评估代理 - 专门负责效率评估

启动 AutoGen 代理后，系统会自动执行以下任务：

1. 获取团队成员列表
2. 获取最近活跃的仓库
3. 获取每个成员的提交记录
4. 分析提交并评估代码质量
5. 为每个成员生成工作报表
6. 评估整个团队的工作效率

## 查看报告

报告将保存在配置文件中指定的输出目录（默认为 `./reports`）。

每个成员的报告将保存为 `{username}_report.md` 和 `{username}_report.json`。

团队报告将保存为 `team_report.md` 和 `team_report.json`。