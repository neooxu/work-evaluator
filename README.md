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

在运行之前，需要创建配置文件。配置文件可以放在以下位置之一：

1. 当前目录下的 `aliyun.yaml`
2. 当前目录下的 `config/aliyun.yaml`
3. 包安装目录下的 `config/aliyun.yaml`

配置文件格式：

```yaml
domain: "openapi-rdc.aliyuncs.com"
organization_id: "你的组织ID"
access_token: "你的访问令牌"
```

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