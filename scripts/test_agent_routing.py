#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 路由意图识别测试脚本

测试用户输入是否能正确匹配到对应的 Agent
"""

import json
import sys
import io
from pathlib import Path
from typing import List, Dict, Any, Tuple

# 强制使用 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_registry(filepath: str) -> Dict[str, Any]:
    """加载 agents_registry.json"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def match_agent(user_input: str, registry: Dict[str, Any]) -> List[Tuple[str, float, List[str]]]:
    """
    根据用户输入匹配 Agent

    Returns:
        [(agent_id, score, matched_patterns), ...] 按分数降序
    """
    user_input_lower = user_input.lower()
    results = []

    for agent in registry.get('agents', []):
        agent_id = agent['id']
        trigger_patterns = agent.get('triggerPatterns', [])
        matched = []

        for pattern in trigger_patterns:
            # 支持中英文匹配
            if pattern.lower() in user_input_lower:
                matched.append(pattern)

        if matched:
            score = len(matched) / len(trigger_patterns) if trigger_patterns else 0
            results.append((agent_id, score, matched))

    # 按分数降序排序
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def test_routing():
    """运行路由测试"""
    registry_path = Path(__file__).parent.parent / "agents_registry.json"
    registry = load_registry(str(registry_path))

    # 测试用例
    # (用户输入，期望的主 Agent, 期望的协同 Agent (可为 None))
    test_cases = [
        # (用户输入，期望的主 Agent)
        ("我需要设计一个新的微服务架构", "architect"),
        ("帮我写一个用户认证功能的实施计划", "planner"),
        ("这段代码有什么安全问题吗", "security-reviewer"),
        ("TypeScript 编译报错了，帮忙修复", "build-error-resolver"),
        ("审查一下这个 PR 的代码质量", "code-reviewer"),
        ("这个 SQL 查询很慢，怎么优化", "database-reviewer"),
        ("帮我清理项目中的死代码", "refactor-cleaner"),
        ("为新功能编写单元测试", "tdd-guide"),
        ("检查是否有硬编码的 API 密钥", "security-reviewer"),
        ("创建一个用户登录流程的 E2E 测试", "e2e-runner"),
        ("更新项目的 codemap 文档", "doc-updater"),
        ("Go 代码审查，检查并发问题", "go-reviewer"),
        ("Python 代码添加 type hints", "python-reviewer"),
        ("设计数据库 schema，添加 RLS 策略", "database-reviewer"),
        ("重构这个模块，提高可维护性", "refactor-cleaner"),
    ]

    print("=" * 60)
    print("Agent Routing Test Results")
    print("=" * 60)

    passed = 0
    failed = 0

    for user_input, expected_primary in test_cases:
        results = match_agent(user_input, registry)

        if not results:
            print(f"\n[FAIL] 输入：{user_input}")
            print(f"       期望：{expected_primary}, 实际：无匹配")
            failed += 1
            continue

        primary_match = results[0]
        primary_agent = primary_match[0]
        primary_score = primary_match[1]

        # 检查主要 Agent 是否匹配
        is_primary_match = primary_agent == expected_primary

        if is_primary_match:
            print(f"[PASS] {user_input[:40]:<40} -> {primary_agent} (score: {primary_score:.2f})")
            passed += 1
        else:
            print(f"\n[FAIL] 输入：{user_input}")
            print(f"       期望主 Agent: {expected_primary}, 实际：{primary_agent} (score: {primary_score:.2f})")
            print(f"       所有匹配：{[(r[0], r[1]) for r in results]}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Summary: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    import sys
    success = test_routing()
    sys.exit(0 if success else 1)
