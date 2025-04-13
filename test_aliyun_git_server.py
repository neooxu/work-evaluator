"""
测试阿里云云效Git服务器功能

这个脚本用于测试 aliyun_git_server.py 中实现的各项功能，
包括仓库列表获取、提交记录查询等。
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import argparse

from mcp_server.aliyun_git_server import Repository, GitCommit, config, AliyunGitClient

# 创建一个新的客户端实例，用于测试
test_client = AliyunGitClient(config)

async def init_test_client(debug_mode: bool = False):
    """初始化测试客户端
    
    Args:
        debug_mode: 是否启用调试模式，显示API返回的原始数据
    """
    global test_client
    test_client = AliyunGitClient(config, debug_mode=debug_mode)
    print(f"测试客户端初始化完成，调试模式: {'开启' if debug_mode else '关闭'}")

async def test_list_repositories(days: int = 7):
    """测试获取仓库列表
    
    Args:
        days: 获取最近几天内活跃的仓库
    """
    print(f"\n1. 测试获取最近{days}天的活跃仓库列表（同时满足最后活动时间和有提交记录）")
    try:
        repos = await test_client.get_repositories(days=days)
        print(f"成功获取到 {len(repos)} 个活跃仓库")
        
        if repos:
            print("\n活跃仓库列表:")
            for repo in repos:
                print(f"- {repo.name}")
                print(f"  路径: {repo.path}")
                print(f"  可见性: {repo.visibility}")
                print(f"  Web地址: {repo.webUrl}")
                print(f"  最后活动时间: {repo.lastActivityAt}")
                if repo.commits:
                    print(f"  提交记录数量: {len(repo.commits)}")
                    for commit in repo.commits:  # 显示所有提交
                        print(f"    - 时间: {commit.authoredDate}")
                        print(f"      作者: {commit.authorName} <{commit.authorEmail}>")
                        print(f"      提交者: {commit.committerName} <{commit.committerEmail}>")
                        print(f"      分支: {commit.branchName}")
                        print(f"      消息: {commit.message}")
                        if commit.stats:
                            print(f"      变更: +{commit.stats.get('additions', 0)} -{commit.stats.get('deletions', 0)}")
                        print(f"      Web地址: {commit.webUrl}")
                print()
            
            print("\n第一个仓库的详细信息:")
            print(json.dumps(repos[0].model_dump(), indent=2, ensure_ascii=False))
        return repos
    except Exception as e:
        print(f"获取仓库列表失败: {str(e)}")
        return None

async def test_get_repository(repo_id: str):
    """测试获取单个仓库信息"""
    print(f"\n2. 测试获取仓库 {repo_id} 的详细信息")
    try:
        repo = await test_client.get_repository(repo_id)
        print("仓库详细信息:")
        print(json.dumps(repo.model_dump(), indent=2, ensure_ascii=False))
        return repo
    except Exception as e:
        print(f"获取仓库信息失败: {str(e)}")
        return None

async def test_get_commits(repo_id: str, days: int = 7):
    """测试获取提交记录
    
    Args:
        repo_id: 仓库ID
        days: 获取最近几天的提交记录
    """
    print(f"\n3. 测试获取仓库 {repo_id} 的最近{days}天提交记录")
    try:
        commits = await test_client.get_commits(repo_id, days=days)
        print(f"成功获取到 {len(commits)} 条提交记录")
        if commits:
            print("\n最新提交记录:")
            for commit in commits[:3]:  # 显示最新的3条提交
                print(f"  - 时间: {commit.authoredDate}")
                print(f"    作者: {commit.authorName} <{commit.authorEmail}>")
                print(f"    提交者: {commit.committerName} <{commit.committerEmail}>")
                print(f"    消息: {commit.message}")
                if commit.stats:
                    print(f"    变更: +{commit.stats.get('additions', 0)} -{commit.stats.get('deletions', 0)}")
                print(f"    Web地址: {commit.webUrl}")
        return commits
    except Exception as e:
        print(f"获取提交记录失败: {str(e)}")
        return None

async def test_get_commit_details(repo_id: str, commit_id: str):
    """测试获取提交详情"""
    print(f"\n4. 测试获取提交 {commit_id} 的详细信息")
    try:
        commit = await test_client.get_commit(repo_id, commit_id)
        print("提交详细信息:")
        print(f"  提交ID: {commit.id}")
        print(f"  短提交ID: {commit.shortId}")
        print(f"  作者: {commit.authorName} <{commit.authorEmail}>")
        print(f"  作者提交时间: {commit.authoredDate}")
        print(f"  提交者: {commit.committerName} <{commit.committerEmail}>")
        print(f"  提交时间: {commit.committedDate}")
        print(f"  消息: {commit.message}")
        if commit.stats:
            print(f"  变更: +{commit.stats.get('additions', 0)} -{commit.stats.get('deletions', 0)}")
        print(f"  Web地址: {commit.webUrl}")
        print("\n完整的提交信息:")
        print(json.dumps(commit.model_dump(), indent=2, ensure_ascii=False))
        return commit
    except Exception as e:
        print(f"获取提交详情失败: {str(e)}")
        return None

async def test_get_commit_diff(repo_id: str, from_commit: str, to_commit: str):
    """测试获取提交差异"""
    print(f"\n5. 测试获取提交差异 ({from_commit} -> {to_commit})")
    try:
        diffs = await test_client.get_commit_diff(repo_id, from_commit, to_commit)
        print(f"成功获取到 {len(diffs)} 个文件的变更")
        if diffs:
            print("第一个文件的变更信息:")
            print(json.dumps(diffs[0].model_dump(), indent=2, ensure_ascii=False))
        return diffs
    except Exception as e:
        print(f"获取提交差异失败: {str(e)}")
        return None

async def test_get_branches(repo_id: str):
    """测试获取分支列表"""
    print(f"\n测试获取仓库 {repo_id} 的分支列表")
    try:
        branches = await test_client.get_branches(repo_id)
        print(f"获取到 {len(branches)} 个分支")
        
        if branches:
            print("\n分支列表（按更新时间降序排序）:")
            for branch in branches:
                print(f"- {branch.name}")
                print(f"  是否默认分支: {'是' if branch.defaultBranch else '否'}")
                print(f"  是否保护分支: {'是' if branch.protected else '否'}")
                print(f"  最新提交: {branch.commit.shortId} - {branch.commit.message}")
                print(f"  提交者: {branch.commit.committerName} <{branch.commit.committerEmail}>")
                print(f"  提交时间: {branch.commit.committedDate}")
            
            print("\n第一个分支的详细信息:")
            print(json.dumps(branches[0].model_dump(), indent=2, ensure_ascii=False))
        
        return branches
    except Exception as e:
        print(f"获取分支列表失败: {str(e)}")
        return None

async def find_active_repository(repos: List[Repository], days: int = 7) -> Tuple[Optional[Repository], Optional[List[GitCommit]]]:
    """从已知的活跃仓库中查找有提交记录的仓库
    
    Args:
        repos: 仓库列表
        days: 获取最近几天的提交记录，默认7天
    """
    print(f"\n正在检查活跃仓库的提交记录...")
    
    for repo in repos:
        print(f"\n检查仓库: {repo.name} (ID: {repo.id})")
        try:
            commits = await test_client.get_commits(str(repo.id), days=days)  # 使用指定的天数
            if commits:
                print(f"✓ 仓库 {repo.name} 有 {len(commits)} 条提交记录")
                print("最新提交记录:")
                for commit in commits[:3]:  # 显示最新的3条提交
                    print(f"  - 时间: {commit.authoredDate}")
                    print(f"    作者: {commit.authorName} <{commit.authorEmail}>")
                    print(f"    提交者: {commit.committerName} <{commit.committerEmail}>")
                    print(f"    消息: {commit.message}")
                    if commit.stats:
                        print(f"    变更: +{commit.stats.get('additions', 0)} -{commit.stats.get('deletions', 0)}")
                    print(f"    Web地址: {commit.webUrl}")
                return repo, commits
            else:
                print(f"- 仓库 {repo.name} 没有提交记录")
        except Exception as e:
            if "404 Not Found" in str(e):
                print(f"- 仓库 {repo.name} 不存在或无访问权限")
            else:
                print(f"- 检查仓库 {repo.name} 失败: {str(e)}")
            continue
    
    print("\n未找到有提交记录的仓库")
    return None, None

async def main():
    """主测试函数"""
    print("开始测试阿里云云效Git仓库...")
    
    # 初始化测试客户端，可以通过命令行参数控制调试模式
    import sys
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='测试阿里云云效Git仓库API')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--days', type=int, default=7, help='指定获取最近几天的活跃仓库，默认7天')
    args = parser.parse_args()
    
    await init_test_client(args.debug)
    
    # 测试获取指定天数的活跃仓库列表
    repos = await test_list_repositories(days=args.days)
    if not repos:
        print("无法继续测试，因为获取仓库列表失败")
        return
    
    # 在活跃仓库中查找有提交记录的仓库，使用相同的时间段
    repo, commits = await find_active_repository(repos, args.days)
    if repo and commits and len(commits) >= 2:
        # 测试获取单个仓库信息
        await test_get_repository(str(repo.id))
        
        # 测试获取分支列表
        await test_get_branches(str(repo.id))
        
        # 测试获取提交详情
        await test_get_commit_details(str(repo.id), commits[0].id)
        
        # 测试获取提交差异
        await test_get_commit_diff(str(repo.id), commits[1].id, commits[0].id)
    
    print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(main()) 