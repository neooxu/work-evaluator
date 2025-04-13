"""
阿里云云效 Git 工作评估 MCP Server

这个MCP服务器使用阿里云云效API与Git仓库交互，用于获取团队成员的代码提交信息
并进行工作评估。
"""

import asyncio
import datetime
from datetime import timedelta
import json
import os
import ssl
from typing import Dict, List, Optional, Any, Union
import aiohttp
from pydantic import BaseModel, Field, validator

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image
from mcp.types import LoggingLevel
from mcp.server.fastmcp import Context

# 创建MCP服务器
mcp = FastMCP("Codeup 阿里云云效 Git 数据提供服务器", 
              instructions="这个服务器使用阿里云云效API提供Git仓库交互功能，用于获取团队成员的代码提交信息和代码修改。")

# 配置类
class AliyunConfig(BaseModel):
    """阿里云云效配置"""
    domain: str = "openapi-rdc.aliyuncs.com"  # API域名
    organization_id: str  # 组织ID
    access_token: str  # 访问令牌

# 数据模型
class GitCommit(BaseModel):
    """Git提交信息
    参考文档: 
    - https://help.aliyun.com/zh/yunxiao/developer-reference/listcommits-query-the-submission-list
    - https://help.aliyun.com/zh/yunxiao/developer-reference/getcommit-query-commit-information
    """
    id: str  # 提交ID
    branchName: Optional[str] = None  # 分支名称
    authorName: str  # 作者姓名
    authorEmail: str  # 作者邮箱
    authoredDate: str  # 作者提交时间
    committedDate: str  # 提交者提交时间
    committerName: str  # 提交者姓名
    committerEmail: str  # 提交者邮箱
    message: str  # 提交内容
    parentIds: List[str] = []  # 父提交ID
    shortId: str  # 短提交ID
    stats: Optional[Dict[str, int]] = None  # 变更行数统计
    webUrl: Optional[str] = None  # 页面访问地址
    repository: Optional[str] = None  # 仓库ID（非API返回字段，用于内部关联）
    
    @validator('message')
    def strip_message_newline(cls, v: str) -> str:
        """去掉提交消息末尾的换行符"""
        return v.rstrip('\n') if v else v

class Repository(BaseModel):
    """仓库信息
    参考文档: https://help.aliyun.com/zh/yunxiao/developer-reference/listrepositories-query-code-base-list
    """
    id: Optional[int] = None  # 代码库 ID
    name: str  # 代码库名称
    path: str  # 代码库路径
    description: Optional[str] = None  # 代码库描述
    visibility: Optional[str] = None  # 可见性: private(私有), internal(组织内公开), public(全平台公开)
    webUrl: Optional[str] = None  # 页面访问时的 URL
    lastActivityAt: Optional[str] = None  # 最后活跃时间
    # accessLevel: Optional[int] = None  # 当前用户在该代码库上的权限类型。20-浏览者，30-开发者，40-管理员
    # archived: Optional[bool] = False  # 代码库是否归档
    # avatarUrl: Optional[str] = None  # 头像地址
    createdAt: Optional[str] = None  # 创建时间
    # demoProject: Optional[bool] = False  # 是否是 demo 库
    # encrypted: Optional[bool] = False  # 是否加密
    namespaceId: Optional[int] = None  # 上级路径的 ID
    # nameWithNamespace: Optional[str] = None  # 代码库完整名称（含完整组名称）
    pathWithNamespace: Optional[str] = None  # 代码库完整路径（含完整组路径）
    repositorySize: Optional[str] = None  # 代码库大小(MB)
    # starCount: Optional[int] = 0  # 被收藏的数量
    # starred: Optional[bool] = False  # 是否被当前用户收藏
    updatedAt: Optional[str] = None  # 最近更新时间
    commits: Optional[List[GitCommit]] = None  # 指定时间段内的提交记录

class CommitDiff(BaseModel):
    """提交差异信息"""
    old_path: str
    new_path: str
    diff: str
    deleted_file: bool
    new_file: bool
    renamed_file: bool

class BranchCommit(BaseModel):
    """分支最近一次提交信息"""
    authorEmail: str  # 作者邮箱
    authorName: str  # 作者姓名
    authoredDate: str  # 作者提交时间
    committedDate: str  # 提交者提交时间
    committerEmail: str  # 提交者邮箱
    committerName: str  # 提交者姓名
    id: str  # 提交ID
    message: str  # 提交内容
    parentIds: List[str] = []  # 父提交ID
    shortId: str  # 短提交ID
    stats: Optional[Dict[str, int]] = None  # 提交变更行统计
    webUrl: Optional[str] = None  # 页面访问地址
    
    @validator('message')
    def strip_message_newline(cls, v: str) -> str:
        """去掉提交消息末尾的换行符"""
        return v.rstrip('\n') if v else v

class Branch(BaseModel):
    """分支信息
    参考文档: https://help.aliyun.com/zh/yunxiao/developer-reference/listbranches-query-the-list-of-branches
    """
    commit: BranchCommit  # 分支最近一次提交信息
    defaultBranch: bool = False  # 是否是默认分支
    name: str  # 分支名称
    protected: bool = False  # 是否是保护分支
    webUrl: Optional[str] = None  # 页面访问URL

# 全局配置 - 直接在代码中定义，而不是从YAML文件加载
config = AliyunConfig(
    domain="openapi-rdc.aliyuncs.com",  # 阿里云云效API域名
    organization_id="619f45cc99ee2b7b75a76352",  # 组织ID
    access_token="pt-4xSRBHj0OUNA1sVyUZsTeCDZ_0b926bbd-45fd-4c2c-bf87-aef3192e8b52"  # 访问令牌
)

# API客户端类
class AliyunGitClient:
    """阿里云云效API客户端"""
    def __init__(self, config: AliyunConfig, debug_mode: bool = False, ctx: Optional[Context] = None):
        self.config = config
        self.debug_mode = debug_mode
        self.ctx = ctx
        self.base_url = f"https://{config.domain}/oapi/v1/codeup/organizations/{config.organization_id}"
        self.headers = {
            "Content-Type": "application/json",
            "x-yunxiao-token": config.access_token
        }
        # 创建SSL上下文
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
    async def _log(self, level: str, message: str) -> None:
        """统一的日志处理方法"""
        if self.ctx is not None:
            log_method = getattr(self.ctx, level, None)
            if log_method:
                await log_method(message)
        else:
            print(f"{level}: {message}")
            
    async def _make_request(self, method: str, path: str, params: Optional[Dict] = None) -> Any:
        """发送API请求"""
        url = f"{self.base_url}{path}"
        conn = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.request(method, url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    if self.ctx:
                        await self.ctx.error(f"API请求失败: HTTP {response.status}")
                        await self.ctx.error(f"响应内容: {error_text}")
                    raise Exception(f"API请求失败: {response.status} - {error_text}")

    async def get_repositories(self, days: int = 7) -> List[Repository]:
        """获取指定时间段内的活跃代码库列表
        
        Args:
            days: 向前推算的天数，例如7表示最近7天
            
        Returns:
            List[Repository]: 活跃仓库列表，每个仓库对象包含指定时间段内的提交记录
            
        Note:
            活跃仓库需要同时满足两个条件：
            1. 在指定时间段内有提交记录
            2. 仓库的 lastActivityAt 时间在指定时间段内
            
            由于返回的仓库列表按 lastActivityAt 降序排序，
            一旦发现某个仓库的 lastActivityAt 不在范围内，
            后续仓库也一定不在范围内，可以提前结束检查。
        """
        all_active_repos = []
        page = 1
        per_page = 20  # 每页固定20条记录
        
        # 计算时间范围
        since_date = datetime.datetime.now() - timedelta(days=days)
        since = since_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        while True:
            params = {
                "page": page,
                "perPage": per_page,
                "orderBy": "last_activity_at",
                "sort": "desc"  # 按最后活动时间降序排序
            }
            
            data = await self._make_request("GET", "/repositories", params)
            
            # 调试信息：打印第一页第一个仓库的数据
            if self.debug_mode and page == 1 and data and len(data) > 0:
                await self._log("info", "API返回的原始数据示例（第一个仓库）:")
                await self._log("info", json.dumps(data[0], indent=2, ensure_ascii=False))
            
            if not data:
                break
                
            try:
                repos = [Repository(**repo) for repo in data]
                
                # 检查每个仓库是否活跃
                for repo in repos:
                    try:
                        # 检查 lastActivityAt 时间
                        is_recently_active = False
                        if repo.lastActivityAt:
                            try:
                                last_activity = datetime.datetime.strptime(
                                    repo.lastActivityAt.split('+')[0] if '+' in repo.lastActivityAt 
                                    else repo.lastActivityAt.rstrip('Z'),
                                    "%Y-%m-%dT%H:%M:%S"
                                )
                                is_recently_active = last_activity >= since_date
                            except ValueError as e:
                                await self._log("error", f"解析仓库 {repo.name} 的 lastActivityAt 时间失败: {str(e)}")
                                continue
                        
                        if not is_recently_active:
                            if self.debug_mode:
                                await self._log("debug", f"仓库 {repo.name} 的最后活动时间不在指定时间范围内")
                                await self._log("debug", "由于仓库按最后活动时间降序排序，后续仓库也不在范围内，提前结束检查")
                            return all_active_repos
                            
                        # 获取仓库的提交记录
                        commits = await self.get_commits(str(repo.id), days=days)
                        if commits:
                            # 将提交记录添加到仓库对象中
                            repo.commits = commits
                            all_active_repos.append(repo)
                            if self.debug_mode:
                                await self._log("debug", f"仓库 {repo.name} 在最近 {days} 天内有 {len(commits)} 条提交记录")
                        elif self.debug_mode:
                            await self._log("debug", f"仓库 {repo.name} 在最近 {days} 天内没有提交记录")
                            
                    except Exception as e:
                        if "404 Not Found" in str(e):
                            if self.debug_mode:
                                await self._log("debug", f"仓库 {repo.name} 不存在或无访问权限")
                        else:
                            await self._log("error", f"检查仓库 {repo.name} 的提交记录时出错: {str(e)}")
                        continue
                
                # 如果返回的数据少于每页数量，说明已经是最后一页
                if len(data) < per_page:
                    break
                    
                # 继续查询下一页
                page += 1
                
            except Exception as e:
                await self._log("error", f"处理仓库数据时出错: {str(e)}")
                await self._log("error", f"问题数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                raise

        if self.ctx:
            await self.ctx.report_progress(len(all_active_repos), len(all_active_repos))
        
        return all_active_repos

    async def get_repository(self, repo_id: str) -> Repository:
        """获取单个代码库信息"""
        data = await self._make_request("GET", f"/repositories/{repo_id}")
        return Repository(**data)

    async def get_commits(self, repo_id: str, ref_name: Optional[str] = None, 
                     days: Optional[int] = 7) -> List[GitCommit]:
        """获取提交列表
        
        Args:
            repo_id: 仓库ID
            ref_name: 分支名称，如果不指定则获取所有分支的提交
            days: 获取最近几天的提交记录，默认为7天
            
        Returns:
            List[GitCommit]: 提交记录列表，按时间降序排序
            
        Note:
            1. ListCommits API 返回的数据中不包含有效的 stats 信息，
               如需获取具体的代码变更统计信息，请使用 get_commit 方法获取单个提交的详细信息。
            2. 当不指定 ref_name 时，会获取所有分支上的提交记录，
               并按提交时间降序排序，去重后返回。
        """
        all_commits = []
        commit_ids = set()  # 用于去重
        
        # 如果没有指定分支，则获取所有分支
        if ref_name is None:
            try:
                # 传递 days 参数给 get_branches，这样只获取最近活跃的分支
                branches = await self.get_branches(repo_id, days=days)
                if self.debug_mode:
                    await self._log("debug", f"获取到 {len(branches)} 个分支")
                for branch in branches:
                    try:
                        branch_commits = await self._get_branch_commits(repo_id, branch.name, days)
                        # 去重添加
                        for commit in branch_commits:
                            if commit.id not in commit_ids:
                                commit_ids.add(commit.id)
                                all_commits.append(commit)
                        if self.debug_mode:
                            await self._log("debug", f"分支 {branch.name} 获取到 {len(branch_commits)} 条提交记录")
                    except Exception as e:
                        await self._log("error", f"获取分支 {branch.name} 的提交记录失败: {str(e)}")
                        continue
            except Exception as e:
                await self._log("error", f"获取仓库 {repo_id} 的分支列表失败: {str(e)}")
                return []
        else:
            # 获取指定分支的提交
            all_commits = await self._get_branch_commits(repo_id, ref_name, days)
            
        # 按提交时间降序排序
        all_commits.sort(key=lambda x: x.authoredDate, reverse=True)
        return all_commits
        
    async def _get_branch_commits(self, repo_id: str, ref_name: str, 
                              days: Optional[int] = None) -> List[GitCommit]:
        """获取单个分支的提交记录"""
        branch_commits = []
        page = 1
        per_page = 20  # 每页固定20条记录
        
        # 计算时间范围
        since = None
        if days is not None:
            since = (datetime.datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        while True:
            params = {
                "refName": ref_name,
                "page": page,
                "perPage": per_page
            }
            if since:
                params["since"] = since
            
            try:
                data = await self._make_request("GET", f"/repositories/{repo_id}/commits", params)
                if not data:
                    break
                
                # 调试信息：打印第一页第一个提交的数据
                if self.debug_mode and page == 1 and len(data) > 0:
                    await self._log("debug", "API返回的原始数据示例（第一个提交）:")
                    await self._log("debug", json.dumps(data[0], indent=2, ensure_ascii=False))
                
                for commit_data in data:
                    try:
                        commit = GitCommit(
                            id=commit_data["id"],
                            authorName=commit_data["authorName"],
                            authorEmail=commit_data["authorEmail"],
                            authoredDate=commit_data["authoredDate"],
                            committedDate=commit_data["committedDate"],
                            committerName=commit_data["committerName"],
                            committerEmail=commit_data["committerEmail"],
                            message=commit_data["message"],
                            parentIds=commit_data["parentIds"],
                            shortId=commit_data["shortId"],
                            stats=commit_data["stats"],
                            webUrl=commit_data["webUrl"],
                            repository=repo_id,
                            branchName=ref_name
                        )
                        
                        # 检查提交时间是否在指定范围内
                        if since:
                            commit_date = datetime.datetime.strptime(
                                commit.authoredDate.split('+')[0] if '+' in commit.authoredDate else commit.authoredDate.rstrip('Z'),
                                "%Y-%m-%dT%H:%M:%S"
                            )
                            since_date = datetime.datetime.strptime(
                                since.rstrip('Z'),
                                "%Y-%m-%dT%H:%M:%S"
                            )
                            if commit_date < since_date:
                                return branch_commits
                        
                        branch_commits.append(commit)
                        
                    except KeyError as e:
                        await self._log("error", f"提交数据缺少必要字段: {e}")
                        await self._log("error", f"问题数据: {json.dumps(commit_data, indent=2, ensure_ascii=False)}")
                        continue
                    except Exception as e:
                        await self._log("error", f"处理提交数据时出错: {e}")
                        await self._log("error", f"问题数据: {json.dumps(commit_data, indent=2, ensure_ascii=False)}")
                        continue
                
                # 如果返回的数据少于每页数量，说明已经是最后一页
                if len(data) < per_page:
                    break
                    
                page += 1
                
            except Exception as e:
                if "404 Not Found" in str(e):
                    await self._log("error", f"仓库 {repo_id} 不存在或无访问权限")
                else:
                    await self._log("error", f"获取仓库 {repo_id} 的提交记录失败: {str(e)}")
                break
        
        return branch_commits

    async def get_commit(self, repo_id: str, commit_sha: str) -> GitCommit:
        """获取单个提交信息
        
        Args:
            repo_id: 仓库ID
            commit_sha: 提交的SHA值
            
        Returns:
            GitCommit: 提交信息，包含完整的代码变更统计
            
        Note:
            GetCommit API 返回的数据中包含有效的 stats 信息，
            可以获取到具体的代码变更行数统计。
        """
        data = await self._make_request("GET", f"/repositories/{repo_id}/commits/{commit_sha}")
        
        # 调试信息：打印API返回的原始数据
        if self.debug_mode:
            await self._log("debug", "GetCommit API返回的原始数据:")
            await self._log("debug", json.dumps(data, indent=2, ensure_ascii=False))
            
        return GitCommit(
            id=data["id"],
            authorName=data["authorName"],
            authorEmail=data["authorEmail"],
            authoredDate=data["authoredDate"],
            committedDate=data["committedDate"],
            committerName=data["committerName"],
            committerEmail=data["committerEmail"],
            message=data["message"],
            parentIds=data["parentIds"],
            shortId=data["shortId"],
            stats=data["stats"],
            webUrl=data["webUrl"],
            repository=repo_id
        )

    async def get_commit_diff(self, repo_id: str, from_sha: str, to_sha: str) -> List[CommitDiff]:
        """获取提交差异"""
        params = {
            "from": from_sha,
            "to": to_sha
        }
        data = await self._make_request("GET", f"/repositories/{repo_id}/compares", params)
        return [CommitDiff(
            old_path=diff["oldPath"],
            new_path=diff["newPath"],
            diff=diff["diff"],
            deleted_file=diff["deletedFile"],
            new_file=diff["newFile"],
            renamed_file=diff["renamedFile"]
        ) for diff in data.get("diffs", [])]

    async def get_branches(self, repo_id: str, days: Optional[int] = None) -> List[Branch]:
        """获取代码库的分支列表，按更新时间降序排序
        
        Args:
            repo_id: 代码库ID
            days: 可选参数，获取最近几天内有更新的分支，默认不过滤
        
        Returns:
            List[Branch]: 分支列表
        """
        all_branches = []
        page = 1
        per_page = 20  # 每页固定20条记录
        
        # 计算时间范围
        since_date = None
        if days is not None:
            since_date = datetime.datetime.now() - timedelta(days=days)
        
        while True:
            params = {
                "page": page,
                "perPage": per_page,
                "sort": "updated_desc"  # 固定使用更新时间降序排序
            }
                
            try:
                data = await self._make_request("GET", f"/repositories/{repo_id}/branches", params)
                
                if not data:
                    break
                    
                # 调试信息：打印第一页第一个分支的数据
                if self.debug_mode and page == 1 and len(data) > 0:
                    await self._log("debug", "API返回的原始数据示例（第一个分支）:")
                    await self._log("debug", json.dumps(data[0], indent=2, ensure_ascii=False))
                
                branches = []
                for branch_data in data:
                    branch = Branch(**branch_data)
                    
                    # 如果指定了时间范围，检查分支最后提交时间是否在范围内
                    if since_date is not None:
                        try:
                            last_commit_date = datetime.datetime.strptime(
                                branch.commit.committedDate.split('+')[0] if '+' in branch.commit.committedDate 
                                else branch.commit.committedDate.rstrip('Z'),
                                "%Y-%m-%dT%H:%M:%S"
                            )
                            if last_commit_date < since_date:
                                # 由于分支按更新时间降序排序，如果当前分支不在时间范围内
                                # 后续分支也一定不在范围内，可以提前结束
                                if self.debug_mode:
                                    await self._log("debug", f"分支 {branch.name} 的最后提交时间不在指定时间范围内")
                                    await self._log("debug", "由于分支按更新时间降序排序，后续分支也不在范围内，提前结束检查")
                                return all_branches
                        except ValueError as e:
                            await self._log("error", f"解析分支 {branch.name} 的提交时间失败: {str(e)}")
                            continue
                            
                    # 将符合条件的分支添加到当前页的分支列表中
                    branches.append(branch)
                    # 同时直接添加到总结果中，这样即使提前返回也不会丢失数据
                    all_branches.append(branch)
                    
                if self.debug_mode:
                    await self._log("debug", f"获取到 {len(branches)} 个分支")
                
                # 如果返回的数据少于每页数量，说明已经是最后一页
                if len(data) < per_page:
                    break
                    
                page += 1
                
            except Exception as e:
                await self._log("error", f"获取分支列表失败: {str(e)}")
                if "404 Not Found" in str(e):
                    await self._log("error", f"仓库 {repo_id} 不存在或无访问权限")
                break
        
        return all_branches

# MCP工具
@mcp.tool()
async def list_repositories(ctx: Context, days: int = 7) -> str:
    """列出指定天数内的活跃代码仓库, 默认7天. 并且包含了最新提交的提交记录
    
    Args:
        days: 获取最近几天内活跃的仓库，默认7天
    """
    client = AliyunGitClient(config, debug_mode=False, ctx=ctx)
    repos = await client.get_repositories(days=days)
    return json.dumps([repo.model_dump() for repo in repos], ensure_ascii=False)

@mcp.tool()
async def get_repository_info(repository_id: str, ctx: Context) -> str:
    """获取代码仓库信息"""
    client = AliyunGitClient(config, debug_mode=False, ctx=ctx)
    repo = await client.get_repository(repository_id)
    return json.dumps(repo.model_dump(), ensure_ascii=False)

@mcp.tool()
async def get_repository_commits(ctx: Context, repository_id: str, ref_name: str = "master",
                               days: Optional[int] = 7) -> str:
    """获取代码仓库的提交记录
    
    Args:
        repository_id: 仓库ID
        ref_name: 分支名称，默认为master
        days: 获取最近几天的提交记录，默认7天
    """
    client = AliyunGitClient(config, debug_mode=False, ctx=ctx)
    commits = await client.get_commits(repository_id, ref_name=ref_name, days=days)
    return json.dumps([commit.model_dump() for commit in commits], ensure_ascii=False)

@mcp.tool()
async def get_commit_details(repository_id: str, commit_id: str, ctx: Context) -> str:
    """获取提交详情"""
    client = AliyunGitClient(config, debug_mode=False, ctx=ctx)
    commit = await client.get_commit(repository_id, commit_id)
    return json.dumps(commit.model_dump(), ensure_ascii=False)

@mcp.tool()
async def get_commit_changes(repository_id: str, from_commit: str, to_commit: str, ctx: Context) -> str:
    """获取提交变更内容"""
    client = AliyunGitClient(config, debug_mode=False, ctx=ctx)
    diffs = await client.get_commit_diff(repository_id, from_commit, to_commit)
    return json.dumps([diff.model_dump() for diff in diffs], ensure_ascii=False)

@mcp.tool()
async def list_branches(ctx: Context, repository_id: str, days: Optional[int] = 7) -> str:
    """获取代码库的分支列表，按更新时间降序排序
    
    Args:
        repository_id: 代码库ID
        days: 获取最近几天内有更新的分支，默认7天
    """
    client = AliyunGitClient(config, debug_mode=False, ctx=ctx)
    branches = await client.get_branches(repository_id, days=days)
    return json.dumps([branch.model_dump() for branch in branches], ensure_ascii=False)

@mcp.tool()
async def add(a: int, b: int, ctx: Context) -> int:
    """Add two numbers"""
    await ctx.debug(f"Adding {a} and {b}")
    return a + b

# MCP资源
@mcp.resource("repositories://list")
async def repositories_resource() -> str:
    """代码仓库列表资源"""
    client = AliyunGitClient(config, debug_mode=False)
    repos = await client.get_repositories()
    return json.dumps([repo.model_dump() for repo in repos], ensure_ascii=False)

@mcp.resource("commits://{repository_id}")
async def repository_commits_resource(repository_id: str) -> str:
    """代码仓库提交记录资源"""
    client = AliyunGitClient(config, debug_mode=False)
    commits = await client.get_commits(repository_id)
    return json.dumps([commit.model_dump() for commit in commits], ensure_ascii=False)

@mcp.resource("branches://{repository_id}")
async def repository_branches_resource(repository_id: str) -> str:
    """代码仓库分支列表资源，按更新时间降序排序"""
    client = AliyunGitClient(config, debug_mode=False)
    branches = await client.get_branches(repository_id)
    return json.dumps([branch.model_dump() for branch in branches], ensure_ascii=False)

# 主函数
# async def main():
#     """主函数"""
#     try:
#         await mcp.run()
#     except Exception as e:
#         raise

def run_server():
    """运行服务器的入口点函数"""
    mcp.settings.debug = True
    mcp.settings.log_level = "DEBUG"
    mcp.run()


if __name__ == "__main__":
    run_server() 