# API 参考

本文档介绍工作评估系统的 API。

## MCP 服务器 API

MCP 服务器遵循 [Model Context Protocol](https://modelcontextprotocol.io/) 规范，提供以下 API：

### 工具 API

#### `get_team_members()`

获取团队所有成员的列表。

**参数**：无

**返回值**：团队成员列表，每个成员包含 `name`、`email` 和 `username` 字段。

#### `get_active_repositories(days: int = 7)`

获取最近活跃的仓库列表。

**参数**：
- `days`：要查询的天数，默认为 7 天

**返回值**：活跃仓库列表，每个仓库包含 `name`、`url`、`description` 和 `last_activity` 字段。

#### `get_member_commits(username: str, days: int = 7)`

获取指定团队成员的提交记录。

**参数**：
- `username`：成员用户名
- `days`：要查询的天数，默认为 7 天

**返回值**：提交记录列表，每个提交包含 `commit_id`、`author`、`author_email`、`date`、`message`、`files_changed`、`insertions`、`deletions` 和 `repository` 字段。

#### `analyze_commit(commit_id: str)`

分析指定的代码提交。

**参数**：
- `commit_id`：提交 ID

**返回值**：分析结果，包含 `commit_id`、`quality_score`、`complexity_score`、`impact_score` 和 `comments` 字段。

#### `generate_member_report(username: str, days: int = 7)`

为指定团队成员生成工作报表。

**参数**：
- `username`：成员用户名
- `days`：要分析的天数，默认为 7 天

**返回值**：工作报表，包含成员信息、时间段、提交统计、效率指标、优势、改进领域和建议等字段。

#### `evaluate_team_efficiency(days: int = 7)`

评估整个团队的工作效率。

**参数**：
- `days`：要分析的天数，默认为 7 天

**返回值**：团队效率评估结果，包含时间段、团队规模、提交统计、效率指标、提交分布、活跃仓库、团队优势和改进建议等字段。

### 资源 API

#### `team://members`

团队成员信息资源。

**返回值**：JSON 格式的团队成员列表。

#### `repositories://active`

活跃仓库信息资源。

**返回值**：JSON 格式的活跃仓库列表。

#### `commits://{username}`

指定成员的提交信息资源。

**参数**：
- `username`：成员用户名

**返回值**：JSON 格式的提交记录列表。

#### `report://{username}`

指定成员的工作报表资源。

**参数**：
- `username`：成员用户名

**返回值**：JSON 格式的工作报表。

### 提示 API

#### `analyze_member_work(username: str)`

创建分析成员工作的提示。

**参数**：
- `username`：成员用户名

**返回值**：提示消息列表。

#### `evaluate_team_prompt()`

创建团队效率评估的提示。

**返回值**：提示消息列表。

## 核心模块 API

### ConfigManager

配置管理器类，负责加载和管理配置。

#### `__init__(config_path: str = None)`

初始化配置管理器。

**参数**：
- `config_path`：配置文件路径，默认为 `./config/config.yaml`

#### `get_general_config() -> Dict[str, Any]`

获取通用配置。

#### `get_git_providers() -> Dict[str, Any]`

获取 Git 提供者配置。

#### `get_team_members() -> List[Dict[str, str]]`

获取团队成员配置。

#### `get_agents_config() -> Dict[str, Any]`

获取代理配置。

#### `get_reports_config() -> Dict[str, Any]`

获取报告配置。

#### `get_server_config() -> Dict[str, Any]`

获取服务器配置。

### GitService

Git 服务类，负责与 Git 仓库交互。

#### `__init__(config_manager: ConfigManager)`

初始化 Git 服务。

**参数**：
- `config_manager`：配置管理器实例

#### `async get_active_repositories(days: int = None) -> List[Dict[str, Any]]`

获取最近活跃的仓库列表。

**参数**：
- `days`：要查询的天数，默认使用配置中的时间范围

**返回值**：活跃仓库列表。

#### `async get_member_commits(username: str, days: int = None) -> List[Dict[str, Any]]`

获取团队成员的提交记录。

**参数**：
- `username`：成员用户名
- `days`：要查询的天数，默认使用配置中的时间范围

**返回值**：提交记录列表。

### MemberClassifier

成员分类器类，负责将提交按团队成员进行分类。

#### `__init__(config_manager: ConfigManager, git_service: GitService)`

初始化成员分类器。

**参数**：
- `config_manager`：配置管理器实例
- `git_service`：Git 服务实例

#### `async classify_commits(days: int = None) -> Dict[str, List[Dict[str, Any]]]`

将提交按团队成员进行分类。

**参数**：
- `days`：要查询的天数，默认使用配置中的时间范围

**返回值**：按成员分类的提交字典，键为成员用户名，值为提交列表。

### CodeAnalyzer

代码分析器类，负责分析代码变更。

#### `__init__(config_manager: ConfigManager, git_service: GitService, classifier: MemberClassifier)`

初始化代码分析器。

**参数**：
- `config_manager`：配置管理器实例
- `git_service`：Git 服务实例
- `classifier`：成员分类器实例

#### `async analyze_commit(commit_id: str) -> Dict[str, Any]`

分析单个提交。

**参数**：
- `commit_id`：提交 ID

**返回值**：分析结果。

#### `async analyze_member_commits(username: str, days: int = None) -> Dict[str, Any]`

分析成员的所有提交。

**参数**：
- `username`：成员用户名
- `days`：要分析的天数，默认使用配置中的时间范围

**返回值**：分析结果。

#### `async analyze_team(days: int = None) -> Dict[str, Any]`

分析整个团队。

**参数**：
- `days`：要分析的天数，默认使用配置中的时间范围

**返回值**：分析结果。

### ReportGenerator

报告生成器类，负责生成工作报表。

#### `__init__(config_manager: ConfigManager, code_analyzer: CodeAnalyzer)`

初始化报告生成器。

**参数**：
- `config_manager`：配置管理器实例
- `code_analyzer`：代码分析器实例

#### `async generate_member_report(username: str, days: int = None) -> Dict[str, Any]`

生成成员工作报表。

**参数**：
- `username`：成员用户名
- `days`：要分析的天数，默认使用配置中的时间范围

**返回值**：报表数据。

#### `async generate_team_report(days: int = None) -> Dict[str, Any]`

生成团队工作报表。

**参数**：
- `days`：要分析的天数，默认使用配置中的时间范围

**返回值**：报表数据。

#### `async render_member_report(username: str, days: int = None, format: str = None) -> str`

渲染成员工作报表。

**参数**：
- `username`：成员用户名
- `days`：要分析的天数，默认使用配置中的时间范围
- `format`：报表格式，默认使用配置中的格式

**返回值**：渲染后的报表内容。

#### `async render_team_report(days: int = None, format: str = None) -> str`

渲染团队工作报表。

**参数**：
- `days`：要分析的天数，默认使用配置中的时间范围
- `format`：报表格式，默认使用配置中的格式

**返回值**：渲染后的报表内容。