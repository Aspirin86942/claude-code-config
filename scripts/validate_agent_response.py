#!/usr/bin/env python3
"""
JSON Schema 验证器 for Agent Registry

验证子代理返回的 JSON 是否符合 agents_registry.json 中定义的 outputContract.schema
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_json_file(filepath: str) -> Dict[str, Any]:
    """加载 JSON 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_schema(data: Any, schema: Dict[str, Any], path: str = "") -> List[str]:
    """
    递归验证数据是否符合 JSON Schema

    Args:
        data: 待验证的数据
        schema: JSON Schema 定义
        path: 当前字段路径 (用于错误报告)

    Returns:
        错误消息列表
    """
    errors = []

    # 处理 type 关键字
    if "type" in schema:
        expected_type = schema["type"]

        # JSON Schema type 到 Python type 映射
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }

        python_type = type_map.get(expected_type)
        if python_type and not isinstance(data, python_type):
            errors.append(f"{path or 'root'}: 期望类型 '{expected_type}',实际 '{type(data).__name__}'")
            return errors  # 类型不匹配，停止进一步验证

    # 处理 enum 关键字
    if "enum" in schema:
        if data not in schema["enum"]:
            errors.append(f"{path or 'root'}: 值 '{data}' 不在允许的枚举 {schema['enum']} 中")

    # 处理 object 类型
    if schema.get("type") == "object" and isinstance(data, dict):
        # 验证 required 字段
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"{path}.{field}: 必填字段缺失")

        # 验证 properties
        properties = schema.get("properties", {})
        for key, value in data.items():
            if key in properties:
                sub_path = f"{path}.{key}" if path else key
                errors.extend(validate_schema(value, properties[key], sub_path))
            # 注意：没有处理 additionalFields，允许额外字段

    # 处理 array 类型
    if schema.get("type") == "array" and isinstance(data, list):
        items_schema = schema.get("items", {})
        for i, item in enumerate(data):
            sub_path = f"{path}[{i}]"
            errors.extend(validate_schema(item, items_schema, sub_path))

        # 验证 minItems/maxItems
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(f"{path}: 数组长度 {len(data)} 小于最小值 {schema['minItems']}")
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(f"{path}: 数组长度 {len(data)} 大于最大值 {schema['maxItems']}")

    # 处理 minimum/maximum (number 类型)
    if isinstance(data, (int, float)):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: 值 {data} 小于最小值 {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: 值 {data} 大于最大值 {schema['maximum']}")

    return errors


def validate_agent_response(
    response: Dict[str, Any],
    registry: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    验证 Agent 返回的响应是否符合注册表中定义的 outputContract

    Args:
        response: Agent 返回的 JSON 响应
        registry: agents_registry.json 加载的内容

    Returns:
        (是否通过验证，错误消息列表)
    """
    errors = []

    # 1. 验证根级别必填字段
    required_root_fields = ["agentId", "requestId", "status", "data"]
    for field in required_root_fields:
        if field not in response:
            errors.append(f"根级别：必填字段 '{field}' 缺失")

    if errors:
        return False, errors

    # 2. 验证 status 字段
    valid_statuses = ["SUCCESS", "FAILED", "PARTIAL", "BLOCKED"]
    if response["status"] not in valid_statuses:
        errors.append(f"status: 值 '{response['status']}' 无效，必须是 {valid_statuses} 之一")

    # 3. 根据 agentId 查找对应的 outputContract
    agent_id = response["agentId"]
    agent_def = None
    for agent in registry.get("agents", []):
        if agent["id"] == agent_id:
            agent_def = agent
            break

    if not agent_def:
        errors.append(f"agentId: 未知的 Agent '{agent_id}'")
        return False, errors

    # 4. 验证 outputContract 的 requiredFields
    output_contract = agent_def.get("outputContract", {})
    required_fields = output_contract.get("requiredFields", [])
    data = response.get("data", {})

    for field in required_fields:
        if field not in data:
            errors.append(f"data: 必填字段 '{field}' 缺失 (根据 {agent_id} 的 outputContract)")

    # 5. 验证 outputContract 的 schema
    output_schema = output_contract.get("schema", {})
    if output_schema:
        schema_errors = validate_schema(data, {"type": "object", "properties": output_schema}, "data")
        errors.extend(schema_errors)

    return len(errors) == 0, errors


def validate_example_response(agent_id: str, registry: Dict[str, Any]) -> None:
    """验证示例响应"""
    example = {
        "agentId": agent_id,
        "requestId": "test-uuid-123",
        "status": "SUCCESS",
        "data": {
            "summary": "测试摘要",
            "details": {}
        },
        "metadata": {
            "processingTimeMs": 100,
            "tokensUsed": 500
        },
        "errors": [],
        "warnings": []
    }

    valid, errors = validate_agent_response(example, registry)
    return valid, errors


def main():
    """主函数"""
    # 支持两种运行方式：直接从 scripts 目录或从父目录
    registry_path = Path(__file__).parent.parent / "agents_registry.json"

    if not registry_path.exists():
        print(f"错误：找不到注册表文件 {registry_path}")
        sys.exit(1)

    registry = load_json_file(str(registry_path))
    print(f"已加载注册表：{len(registry.get('agents', []))} 个 Agent")

    # 测试每个 Agent 的示例响应
    print("\n=== Validating Example Response ===\n")

    all_passed = True
    for agent in registry.get("agents", []):
        agent_id = agent["id"]
        valid, errors = validate_example_response(agent_id, registry)

        status = "PASS" if valid else "FAIL"
        print(f"[{status}] {agent_id}")

        if errors:
            all_passed = False
            for error in errors:
                print(f"       - {error}")

    print("\n=== Validating Agent Definition Completeness ===\n")

    # 验证每个 Agent 都有必要的定义
    for agent in registry.get("agents", []):
        agent_id = agent["id"]
        issues = []

        if not agent.get("inputContract"):
            issues.append("缺少 inputContract")
        if not agent.get("outputContract"):
            issues.append("缺少 outputContract")
        if not agent.get("triggerPatterns"):
            issues.append("缺少 triggerPatterns")
        if "outOfScope" not in agent:
            issues.append("缺少 outOfScope")
        if "errorHandling" not in agent:
            issues.append("缺少 errorHandling")

        if issues:
            print(f"[WARN] {agent_id}: {', '.join(issues)}")
        else:
            print(f"[PASS] {agent_id}: 定义完整")

    print("\n=== Summary ===\n")
    if all_passed:
        print("All validation passed")
        return 0
    else:
        print("Some validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
