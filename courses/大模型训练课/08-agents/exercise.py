"""
============================================================
第八课练习：构建一个迷你 Agent
============================================================

Agent = 大模型 + 工具调用 + 循环执行。
模型负责"决策"（调什么工具、怎么用结果），工具负责"执行"。

在这个练习中，你将亲手实现一个能调用工具的迷你 Agent：
  解析工具调用 → 执行工具 → 决策判断 → 上下文构建 → 完整循环

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过 ✅

难度：⭐⭐⭐ (逻辑清晰，主要是字符串处理和流程控制)
预计用时：30-45 分钟
"""

import json
import math
import random

random.seed(42)


# ============================================================
# 模拟工具集（已实现，不需要修改）
# ============================================================

def tool_calculator(expression: str) -> str:
    """计算数学表达式。"""
    try:
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return json.dumps({"result": result, "status": "success"})
    except Exception as e:
        return json.dumps({"error": str(e), "status": "failed"})


def tool_weather(city: str) -> str:
    """模拟天气查询。"""
    weather_data = {
        "北京": {"temp": "5°C", "weather": "晴", "humidity": "30%"},
        "上海": {"temp": "12°C", "weather": "多云", "humidity": "65%"},
        "广州": {"temp": "20°C", "weather": "小雨", "humidity": "80%"},
        "杭州": {"temp": "10°C", "weather": "阴", "humidity": "70%"},
    }
    if city in weather_data:
        return json.dumps({"city": city, **weather_data[city], "status": "success"})
    return json.dumps({"error": f"未找到城市: {city}", "status": "failed"})


def tool_search(query: str) -> str:
    """模拟搜索引擎。"""
    search_db = {
        "python": "Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。",
        "transformer": "Transformer 是 2017 年提出的神经网络架构，基于 Self-Attention 机制。",
        "lora": "LoRA (Low-Rank Adaptation) 是一种参数高效的模型微调方法，由微软于 2021 年提出。",
    }
    for key, value in search_db.items():
        if key in query.lower():
            return json.dumps({"result": value, "source": "知识库", "status": "success"})
    return json.dumps({"result": "未找到相关结果", "status": "no_results"})


AVAILABLE_TOOLS = {
    "calculator": {
        "function": tool_calculator,
        "description": "计算数学表达式",
        "parameters": {"expression": "要计算的数学表达式"},
    },
    "weather": {
        "function": tool_weather,
        "description": "查询城市天气",
        "parameters": {"city": "城市名称"},
    },
    "search": {
        "function": tool_search,
        "description": "搜索知识库",
        "parameters": {"query": "搜索关键词"},
    },
}


# ============================================================
# 🧱 Part 1: 解析工具调用
# ============================================================
#
# Agent 的第一步是"听懂"模型的输出——当模型决定调用工具时，
# 它会输出特定格式的文本。我们需要解析它。
#
# 格式：{"tool": "工具名", "args": {"参数名": "参数值"}}
#

def parse_tool_call(model_output: str) -> dict | None:
    """从模型的输出文本中解析工具调用。

    Args:
        model_output: 模型的输出文本

    Returns:
        如果包含工具调用，返回 {"tool": str, "args": dict}
        如果不包含工具调用（普通文本回答），返回 None

    示例：
        输入: '{"tool": "weather", "args": {"city": "北京"}}'
        输出: {"tool": "weather", "args": {"city": "北京"}}

        输入: '今天天气很好！'
        输出: None
    """
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：
    #   1. 尝试用 json.loads(model_output) 解析文本
    #   2. 如果解析成功，检查结果是否包含 "tool" 和 "args" 两个键
    #   3. 如果都满足，返回解析后的字典
    #   4. 如果 json.loads 抛出异常（不是 JSON），或缺少必要的键，返回 None
    #
    # 用 try/except 来处理非 JSON 文本

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 1 ========


# ============================================================
# 🔧 Part 2: 执行工具
# ============================================================
#
# 解析出工具调用后，需要实际执行对应的工具函数。
#

def execute_tool(tool_name: str, args: dict) -> str:
    """根据工具名称和参数执行工具。

    Args:
        tool_name: 工具名称（如 "calculator", "weather", "search"）
        args: 参数字典

    Returns:
        工具的返回结果（JSON 字符串）
        如果工具不存在，返回错误信息的 JSON
    """
    # ======== TODO 2: 在这里写你的代码 ========
    # 提示：
    #   1. 检查 tool_name 是否在 AVAILABLE_TOOLS 中
    #   2. 如果不在，返回 json.dumps({"error": "未知工具: {tool_name}", "status": "failed"})
    #   3. 如果存在，获取工具的函数：func = AVAILABLE_TOOLS[tool_name]["function"]
    #   4. 调用函数并传入参数：result = func(**args)
    #   5. 返回 result
    #
    # 注意：**args 会把字典展开为关键字参数
    # 例：args = {"city": "北京"} → func(city="北京")

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 2 ========


# ============================================================
# 🧠 Part 3: 决策——是否需要工具
# ============================================================
#
# Agent 需要判断用户的问题是"直接能答的"还是"需要查工具的"。
# 这里用一个简单的规则模拟模型的决策能力。
#

def should_use_tool(user_query: str) -> dict | None:
    """判断是否需要调用工具，如果需要返回工具调用信息。

    Args:
        user_query: 用户的问题

    Returns:
        如果需要工具，返回 {"tool": str, "args": dict}
        如果不需要工具（可以直接回答），返回 None

    决策规则（模拟模型的判断）：
        - 包含"计算"或数学运算符(+,-,*,/,^)→ 用 calculator
        - 包含"天气"→ 用 weather（从问题中提取城市名）
        - 包含"什么是"或"搜索"→ 用 search
        - 其他 → 不需要工具
    """
    # ======== TODO 3: 在这里写你的代码 ========
    # 提示：
    #   1. 检查 user_query 是否包含"天气"：
    #      - 如果是，从 ["北京","上海","广州","杭州"] 中找哪个城市名出现在 query 中
    #      - 返回 {"tool": "weather", "args": {"city": 找到的城市}}
    #      - 如果没找到具体城市，默认用 "北京"
    #
    #   2. 检查是否包含计算相关关键词：
    #      - "计算" 在 query 中，或者 query 中包含 +, -, *, / 中的任一字符
    #      - 提取计算表达式：简单起见，把 query 中"计算"之后的部分作为表达式
    #        或者如果包含运算符，尝试提取数字和运算符部分
    #      - 返回 {"tool": "calculator", "args": {"expression": 表达式}}
    #      - 简化处理：如果难以提取表达式，用整个 query 去掉"计算"后的文本
    #
    #   3. 检查是否包含"什么是"或"搜索"：
    #      - 提取搜索关键词（"什么是"后面的内容，或"搜索"后面的内容）
    #      - 返回 {"tool": "search", "args": {"query": 关键词}}
    #
    #   4. 都不满足 → 返回 None

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 3 ========


# ============================================================
# 📝 Part 4: 构建上下文
# ============================================================
#
# 工具返回结果后，需要把它格式化为模型能理解的上下文，
# 让模型基于这些信息生成最终回答。
#

def format_context(
    user_query: str,
    tool_name: str,
    tool_args: dict,
    tool_result: str,
) -> str:
    """把工具调用的结果格式化为上下文 prompt。

    Args:
        user_query: 用户的原始问题
        tool_name: 调用的工具名称
        tool_args: 工具参数
        tool_result: 工具返回的 JSON 字符串

    Returns:
        格式化的上下文字符串，包含：
        - 用户问题
        - 使用了什么工具
        - 工具返回了什么结果
        - 请模型基于结果回答的指令
    """
    # ======== TODO 4: 在这里写你的代码 ========
    # 提示：
    #   构建一个多行字符串，格式如下：
    #
    #   "用户问题：{user_query}\n"
    #   "使用工具：{tool_name}({tool_args})\n"
    #   "工具结果：{tool_result}\n"
    #   "\n请基于以上工具结果，用自然语言回答用户的问题。"
    #
    #   返回这个字符串

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 4 ========


# ============================================================
# 🚀 Part 5: 完整的 Agent 循环
# ============================================================
#
# 把所有组件串起来：
#   1. 接收用户问题
#   2. 判断是否需要工具
#   3. 如果需要→调用工具→构建上下文→生成回答
#   4. 如果不需要→直接回答
#

def agent_loop(user_query: str, max_steps: int = 3) -> dict:
    """执行完整的 Agent 循环。

    Args:
        user_query: 用户的问题
        max_steps: 最大工具调用步数（防止无限循环）

    Returns:
        {
            'answer': 最终回答文本,
            'tool_calls': 使用的工具调用列表 [{"tool": str, "args": dict, "result": str}],
            'steps': 总步骤数,
        }
    """
    # ======== TODO 5: 在这里写你的代码 ========
    # 提示：
    #   1. 创建 tool_calls 列表记录所有工具调用
    #   2. 调用 should_use_tool(user_query) 判断是否需要工具
    #   3. 如果不需要工具（返回 None）：
    #      - answer = f"关于「{user_query}」，这是一个通用问题，我可以直接回答。"
    #      - 返回结果字典（tool_calls 为空列表，steps=0）
    #   4. 如果需要工具：
    #      - 获取 tool_name 和 args
    #      - 调用 execute_tool(tool_name, args) 获取结果
    #      - 记录到 tool_calls 列表
    #      - 调用 format_context() 构建上下文
    #      - 生成回答：简单地用 "根据查询结果：" + 工具结果的关键信息
    #        （真实 Agent 这里会再调用一次大模型来生成自然语言回答）
    #      - 解析 tool_result (json.loads)，提取关键信息作为回答
    #   5. 返回结果字典
    #
    # 简化版：我们只做一步工具调用（真实 Agent 会循环多步）

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 5 ========


# ============================================================
# 🧪 测试 — 运行 python exercise.py 来检查你的实现
# ============================================================

def test_parse_tool_call():
    print("=" * 55)
    print("测试 Part 1: parse_tool_call()")
    print("=" * 55)

    # 测试正常的工具调用
    input1 = '{"tool": "weather", "args": {"city": "北京"}}'
    result1 = parse_tool_call(input1)

    if result1 is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if result1.get("tool") == "weather" and result1.get("args", {}).get("city") == "北京":
        print(f"  ✅ 正确解析工具调用: tool=weather, city=北京")
    else:
        print(f"  ❌ 解析错误，期望 tool=weather, city=北京，得到 {result1}")
        return False

    # 测试普通文本（不是工具调用）
    input2 = "今天天气真好，适合出去走走！"
    result2 = parse_tool_call(input2)
    if result2 is None:
        print(f"  ✅ 普通文本正确返回 None")
    else:
        print(f"  ❌ 普通文本应返回 None，得到 {result2}")
        return False

    # 测试不完整的 JSON
    input3 = '{"tool": "weather"}'  # 缺少 args
    result3 = parse_tool_call(input3)
    if result3 is None:
        print(f"  ✅ 不完整的 JSON 正确返回 None")
        return True
    else:
        print(f"  ⚠️  不完整的 JSON 也被接受了（缺少 args）")
        return True  # 不算硬失败


def test_execute_tool():
    print("\n" + "=" * 55)
    print("测试 Part 2: execute_tool()")
    print("=" * 55)

    # 测试天气工具
    result1 = execute_tool("weather", {"city": "上海"})
    if result1 is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    parsed1 = json.loads(result1)
    if parsed1.get("status") == "success" and "temp" in parsed1:
        print(f"  ✅ weather(上海) → 温度={parsed1['temp']}, 天气={parsed1['weather']}")
    else:
        print(f"  ❌ weather 工具返回异常: {result1}")
        return False

    # 测试计算器
    result2 = execute_tool("calculator", {"expression": "2 + 3 * 4"})
    parsed2 = json.loads(result2)
    if parsed2.get("result") == 14:
        print(f"  ✅ calculator(2+3*4) → {parsed2['result']}")
    else:
        print(f"  ❌ calculator 返回异常: {result2}")
        return False

    # 测试未知工具
    result3 = execute_tool("unknown_tool", {})
    parsed3 = json.loads(result3)
    if parsed3.get("status") == "failed":
        print(f"  ✅ 未知工具正确返回错误: {parsed3.get('error', '')}")
        return True
    else:
        print(f"  ❌ 未知工具应返回 failed 状态")
        return False


def test_should_use_tool():
    print("\n" + "=" * 55)
    print("测试 Part 3: should_use_tool()")
    print("=" * 55)

    # 测试天气查询
    result1 = should_use_tool("上海今天天气怎么样")
    if result1 is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if result1.get("tool") == "weather":
        print(f"  ✅ 天气问题 → 调用 weather 工具, city={result1['args'].get('city')}")
    else:
        print(f"  ❌ 天气问题应该触发 weather 工具，得到 {result1}")
        return False

    # 测试计算
    result2 = should_use_tool("帮我计算 123 * 456")
    if result2 is not None and result2.get("tool") == "calculator":
        print(f"  ✅ 计算问题 → 调用 calculator 工具")
    else:
        print(f"  ❌ 计算问题应触发 calculator，得到 {result2}")
        return False

    # 测试搜索
    result3 = should_use_tool("什么是 Transformer")
    if result3 is not None and result3.get("tool") == "search":
        print(f"  ✅ 知识问题 → 调用 search 工具")
    else:
        print(f"  ❌ '什么是'问题应触发 search，得到 {result3}")
        return False

    # 测试不需要工具
    result4 = should_use_tool("你好，今天过得怎么样")
    if result4 is None:
        print(f"  ✅ 日常聊天 → 不需要工具 (None)")
        return True
    else:
        print(f"  ⚠️  日常聊天不应该调用工具，得到 {result4}")
        return True


def test_format_context():
    print("\n" + "=" * 55)
    print("测试 Part 4: format_context()")
    print("=" * 55)

    result = format_context(
        user_query="北京天气如何",
        tool_name="weather",
        tool_args={"city": "北京"},
        tool_result='{"city":"北京","temp":"5°C","weather":"晴","status":"success"}',
    )

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if not isinstance(result, str):
        print(f"  ❌ 应返回字符串，得到 {type(result)}")
        return False

    checks = [
        ("北京天气如何" in result, "包含用户问题"),
        ("weather" in result, "包含工具名称"),
        ("5°C" in result or "晴" in result, "包含工具结果"),
    ]

    all_ok = True
    for check, desc in checks:
        if check:
            print(f"  ✅ 上下文{desc} ✓")
        else:
            print(f"  ❌ 上下文未{desc}")
            all_ok = False

    if all_ok:
        print(f"\n  📝 生成的上下文预览（前 200 字）：")
        preview = result[:200].replace('\n', '\n     ')
        print(f"     {preview}")
    return all_ok


def test_agent_loop():
    print("\n" + "=" * 55)
    print("测试 Part 5: agent_loop()")
    print("=" * 55)

    # 测试天气查询
    result1 = agent_loop("广州天气怎么样")
    if result1 is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    required_keys = ['answer', 'tool_calls', 'steps']
    for key in required_keys:
        if key not in result1:
            print(f"  ❌ 返回字典缺少 '{key}'")
            return False

    if len(result1['tool_calls']) > 0:
        tc = result1['tool_calls'][0]
        print(f"  ✅ 天气查询：调用了 {tc['tool']} 工具")
        print(f"     参数: {tc['args']}")
        result_preview = tc['result'][:80] if len(tc['result']) > 80 else tc['result']
        print(f"     结果: {result_preview}")
    else:
        print(f"  ❌ 天气查询应该调用工具，但 tool_calls 为空")
        return False

    if result1['answer'] and len(result1['answer']) > 0:
        print(f"  ✅ 生成了回答: {result1['answer'][:60]}...")
    else:
        print(f"  ❌ 未生成回答")
        return False

    # 测试不需要工具的场景
    result2 = agent_loop("你好呀")
    if len(result2['tool_calls']) == 0 and result2['steps'] == 0:
        print(f"  ✅ 日常聊天：无需工具，直接回答 ✓")
    else:
        print(f"  ⚠️  日常聊天不应该调用工具")

    # 测试计算
    result3 = agent_loop("帮我计算 15 * 28")
    if len(result3['tool_calls']) > 0 and result3['tool_calls'][0]['tool'] == 'calculator':
        parsed = json.loads(result3['tool_calls'][0]['result'])
        if parsed.get('result') == 420:
            print(f"  ✅ 计算查询：15 * 28 = {parsed['result']} ✓")
        else:
            print(f"  ⚠️  计算结果可能不正确: {parsed}")
    else:
        print(f"  ⚠️  计算问题应该调用 calculator 工具")

    print(f"\n  🤖 Agent 完整流程验证：")
    print(f"     用户提问 → 判断需要工具 → 调用工具 → 获取结果 → 生成回答")
    print(f"     整个循环成功运转！")
    return True


if __name__ == "__main__":
    print()
    print("🎓 第八课练习：构建一个迷你 Agent")
    print("=" * 55)
    print()

    all_passed = True
    all_passed = test_parse_tool_call() and all_passed
    all_passed = test_execute_tool() and all_passed
    all_passed = test_should_use_tool() and all_passed
    all_passed = test_format_context() and all_passed
    all_passed = test_agent_loop() and all_passed

    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 全部通过！你已经构建了一个能工作的迷你 Agent！")
        print("   你刚刚亲手实现了：")
        print("   工具解析 → 工具执行 → 决策判断 → 上下文构建 → Agent 循环")
        print()
        print("   这就是 ChatGPT Plugins、Cursor、Perplexity 等产品的核心模式。")
        print("   真实的 Agent 还需要：更智能的决策（用大模型代替规则）、")
        print("   多步循环、错误恢复、并行工具调用、安全审核等。")
        print("   但核心架构就是你刚实现的：决策→执行→观察→回答。")
        print()
        print("   🎓 恭喜完成全部八节课的学习！")
        print("   你现在对大模型从原理到应用的完整链路有了深入理解：")
        print("   文字→向量 → Attention → 训练 → 对齐 → 推理 → 微调 → Agent")
    else:
        print("💪 还有测试没通过，继续加油！")
        print("   提示：按照 TODO 的顺序逐个实现，每完成一个就运行一次检查")
    print("=" * 55)
    print()
