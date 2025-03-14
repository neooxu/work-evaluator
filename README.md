# 阿里云云效Git工作评估工具

这是一个基于阿里云云效API的Git仓库工作评估工具，用于获取和分析团队成员的代码提交信息。

## 功能特性

- 获取活跃仓库列表
- 查询代码提交记录
- 分析代码变更统计
- 支持分支管理
- 提交差异比较

## 安装

使用 uv 安装：

```bash
uv pip install -e .
```

## 配置

配置信息已直接在代码中定义，位于 `mcp_server/aliyun_git_server.py` 文件中：

```python
# 全局配置 - 直接在代码中定义
config = AliyunConfig(
    domain="openapi-rdc.aliyuncs.com",  # 阿里云云效API域名
    organization_id="619f45cc99ee2b7b75a76352",  # 组织ID
    access_token="pt-4xSRBHj0OUNA1sVyUZsTeCDZ_0b926bbd-45fd-4c2c-bf87-aef3192e8b52"  # 访问令牌
)
```

如需修改配置，请直接编辑该文件中的配置值。

## 使用方法

启动服务器：

```bash
uv run aliyun_git_server
```

## 开发

1. 克隆仓库：
```bash
git clone https://github.com/你的用户名/work-evaluator.git
cd work-evaluator
```

2. 安装依赖：
```bash
uv pip install -e .
```

3. 运行测试：
```bash
python test_aliyun_git_server.py
```

## 许可证

MIT