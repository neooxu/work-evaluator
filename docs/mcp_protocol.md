# MCP 协议说明

本文档介绍 Model Context Protocol (MCP) 及其在工作评估系统中的应用。

## 什么是 MCP？

Model Context Protocol (MCP) 是一个开放协议，用于在大型语言模型 (LLM) 应用程序和外部数据源、工具之间实现无缝集成。它类似于 Web API，但专为 LLM 交互设计。

MCP 允许 LLM 应用程序（如 Cursor 编辑器）与外部服务器（如我们的工作评估系统）进行通信，以获取数据和执行操作。

## MCP 的核心概念

MCP 定义了三种核心原语：

1. **资源 (Resources)**：由应用程序控制的上下文数据，如文件内容、API 响应等。
2. **工具 (Tools)**：由模型控制的函数，用于执行操作，如 API 调用、数据更新等。
3. **提示 (Prompts)**：由用户控制的交互式模板，如斜杠命令、菜单选项等。

## MCP 在工作评估系统中的应用

我们的工作评估系统使用 MCP 协议提供以下功能：

### 资源

- `team://members`：团队成员信息
- `repositories://active`：活跃仓库信息
- `commits://{username}`：指定成员的提交信息
- `report://{username}`：指定成员的工作报表

这些资源可以被 LLM 应用程序（如 Cursor 编辑器）直接访问，以获取相关数据。

### 工具

- `get_team_members`：获取团队所有成员的列表
- `get_active_repositories`：获取最近活跃的仓库列表
- `get_member_commits`：获取指定团队成员的提交记录
- `analyze_commit`：分析指定的代码提交
- `generate_member_report`：为指定团队成员生成工作报表
- `evaluate_team_efficiency`：评估整个团队的工作效率

这些工具可以被 LLM 调用，以执行特定操作。

### 提示

- `analyze_member_work`：分析成员工作的提示
- `evaluate_team_prompt`：团队效率评估的提示

这些提示可以被用户通过 LLM 应用程序调用，以启动特定的交互流程。

## MCP 通信流程

MCP 使用 WebSocket 进行通信，流程如下：

1. 客户端（如 Cursor 编辑器）与 MCP 服务器建立 WebSocket 连接
2. 服务器向客户端发送可用的工具、资源和提示列表
3. 客户端可以：
   - 请求读取资源
   - 调用工具
   - 使用提示
4. 服务器处理请求并返回结果
5. 客户端显示结果或将结果传递给 LLM

## 与 AutoGen 的集成

我们使用 `autogen-ext-mcp` 模块将 AutoGen 框架与 MCP 服务器集成。这使得 AutoGen 代理可以直接调用 MCP 服务器提供的工具和资源。

集成方式如下：

```python
from autogen_ext_mcp.tools import mcp_server

# 连接到 MCP 服务器
tools = mcp_server("http://localhost:8000")

# 创建使用 MCP 工具的代理
assistant = autogen.AssistantAgent(
    name="助手",
    system_message="你是一个工作评估助手...",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "your_api_key"}]},
    tools=tools,
)
```

## 如何连接到 MCP 服务器

任何符合 MCP 协议的客户端都可以连接到我们的 MCP 服务器。以下是一些常见的连接方式：

### Cursor 编辑器

Cursor 编辑器内置了 MCP 客户端，可以直接连接到 MCP 服务器。

1. 启动 MCP 服务器：`python server.py`
2. 在 Cursor 编辑器中，打开设置 > MCP
3. 添加服务器地址：`http://localhost:8000`
4. 连接到服务器

### 自定义 MCP 客户端

您也可以使用 MCP SDK 创建自己的客户端：

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 创建服务器参数
server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            # 列出可用工具
            tools = await session.list_tools()
            
            # 调用工具
            result = await session.call_tool("get_team_members")
            print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
```

## 参考资料

- [Model Context Protocol 文档](https://modelcontextprotocol.io/)
- [Model Context Protocol 规范](https://modelcontextprotocol.io/specification)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)