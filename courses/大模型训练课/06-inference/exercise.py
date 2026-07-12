"""
============================================================
第六课练习：实现推理优化
============================================================

训练好的模型怎么高效地跑起来？推理优化决定了用户体验和服务成本。
核心技术：KV Cache 避免重复计算，量化压缩模型，采样控制输出风格。

在这个练习中，你将亲手实现推理的核心优化技术：
  KV Cache → 量化/反量化 → 温度采样 → Top-P 采样 → 投机采样

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过 ✅

难度：⭐⭐⭐ (逻辑清晰，每步都有详细提示)
预计用时：30-45 分钟
"""

import math
import random

random.seed(42)


# ============================================================
# 辅助函数（已实现，不需要修改）
# ============================================================

def softmax(logits: list[float]) -> list[float]:
    """将 logits 转化为概率分布。"""
    max_val = max(logits)
    exp_vals = [math.exp(x - max_val) for x in logits]
    sum_exp = sum(exp_vals)
    return [v / sum_exp for v in exp_vals]


def dot_product(a: list[float], b: list[float]) -> float:
    """向量点积。"""
    return sum(x * y for x, y in zip(a, b))


def sample_from_probs(probs: list[float]) -> int:
    """根据概率分布采样一个索引。"""
    r = random.random()
    cumsum = 0.0
    for i, p in enumerate(probs):
        cumsum += p
        if r <= cumsum:
            return i
    return len(probs) - 1


# ============================================================
# 🧱 Part 1: KV Cache 模拟
# ============================================================
#
# 在自回归生成中，每步都要和所有历史 token 计算注意力。
# 没有 KV Cache：每步重新计算所有 token 的 K/V → 浪费巨大
# 有 KV Cache：缓存历史的 K/V，每步只算新 token 的 → 大幅加速
#
# 这里我们模拟这个过程，统计计算量来直观感受差异。
#

def kv_cache_generate(
    prompt_length: int, generate_length: int
) -> dict:
    """模拟有/无 KV Cache 的生成过程，统计计算量。

    Args:
        prompt_length: 输入 prompt 的 token 数量
        generate_length: 要生成的 token 数量

    Returns:
        {
            'without_cache_ops': 无 KV Cache 时的总注意力计算次数,
            'with_cache_ops': 有 KV Cache 时的总注意力计算次数,
            'speedup': 加速比 (without / with),
        }

    注意力计算次数的定义：
    - 每生成一个 token，需要和前面所有 token 计算注意力
    - 无 Cache：每步需要重新计算所有 token 的 K/V，计算量 = 当前序列长度
    - 有 Cache：只需计算新 token 的 K/V（1次），但注意力仍需和所有历史交互
      计算 K/V 的次数 = 1，注意力交互次数 = 当前序列长度
      我们统计的是"K/V 计算次数"（这是 Cache 节省的部分）
    """
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：
    #   无 KV Cache 的计算量：
    #     - 第 1 步生成时序列长度 = prompt_length，需要计算 prompt_length 个 K/V
    #     - 第 2 步生成时序列长度 = prompt_length + 1，需要计算 prompt_length + 1 个 K/V
    #     - ...
    #     - 第 N 步生成时序列长度 = prompt_length + N - 1
    #     - 总计 = sum(prompt_length + i for i in range(generate_length))
    #
    #   有 KV Cache 的计算量：
    #     - 第 1 步：需要计算 prompt_length 个 K/V（Prefill 阶段，初始化缓存）
    #     - 第 2 步及以后：每步只需计算 1 个新 token 的 K/V
    #     - 总计 = prompt_length + (generate_length - 1) × 1
    #              = prompt_length + generate_length - 1
    #
    #   加速比 = without_cache_ops / with_cache_ops
    #
    #   返回包含三个值的字典

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 1 ========


# ============================================================
# 📐 Part 2: 量化与反量化
# ============================================================
#
# 量化：把浮点数映射到有限范围的整数
# 反量化：从整数还原为浮点数（有微小误差）
#
# INT8 量化：映射到 [0, 255] 的整数范围
# 公式：
#   quantized = round((value - min_val) / (max_val - min_val) * 255)
#   dequantized = quantized / 255 * (max_val - min_val) + min_val
#

def quantize_and_dequantize(
    values: list[float], bits: int = 8
) -> dict:
    """对一组浮点数进行量化再反量化，统计精度损失。

    Args:
        values: 浮点数列表（模拟模型参数）
        bits: 量化位数（8 表示 INT8，4 表示 INT4）

    Returns:
        {
            'quantized': 量化后的整数列表,
            'dequantized': 反量化后的浮点数列表,
            'max_error': 最大绝对误差,
            'mean_error': 平均绝对误差,
        }
    """
    # ======== TODO 2: 在这里写你的代码 ========
    # 提示：
    #   1. 计算 values 的最小值 min_val 和最大值 max_val
    #   2. 计算量化范围 max_int = 2^bits - 1（如 8 位 → 255）
    #   3. 处理特殊情况：如果 min_val == max_val，所有值量化为 0
    #   4. 对每个值 v 做量化：
    #      quantized_val = round((v - min_val) / (max_val - min_val) * max_int)
    #      注意 clamp 到 [0, max_int] 范围
    #   5. 对每个量化值做反量化：
    #      dequantized_val = quantized_val / max_int * (max_val - min_val) + min_val
    #   6. 计算误差：
    #      error[i] = abs(values[i] - dequantized[i])
    #      max_error = max(errors)
    #      mean_error = sum(errors) / len(errors)
    #   7. 返回字典

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 2 ========


# ============================================================
# 🌡️ Part 3: 温度采样 (Temperature Sampling)
# ============================================================
#
# Temperature 通过缩放 logits 来控制概率分布的"尖锐度"：
#   adjusted_logits[i] = logits[i] / temperature
#
# T < 1：分布变尖锐，高概率 token 更突出（更确定）
# T = 1：不变
# T > 1：分布变平坦，所有 token 概率更接近（更随机）
# T → 0：退化为贪心解码（总选最高的）
#

def temperature_sampling(
    logits: list[float], temperature: float
) -> list[float]:
    """用温度参数调整 logits 后做 Softmax，返回调整后的概率分布。

    Args:
        logits: 模型原始输出
        temperature: 温度参数（> 0）

    Returns:
        调整后的概率分布
    """
    # ======== TODO 3: 在这里写你的代码 ========
    # 提示：
    #   1. 将每个 logit 除以 temperature：
    #      adjusted[i] = logits[i] / temperature
    #   2. 对 adjusted 做 softmax
    #   3. 返回结果概率分布
    #
    # 特殊处理：如果 temperature 非常小（如 < 0.01），
    # 直接返回 one-hot 分布（最大值位置为 1，其余为 0）
    # 避免除以接近零的数导致数值溢出

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 3 ========


# ============================================================
# 🎯 Part 4: Top-P 采样 (Nucleus Sampling)
# ============================================================
#
# Top-P 从概率最高的 token 开始累加，直到累积概率 >= p，
# 然后只从这个子集中按比例采样。
#
# 优点：自适应候选集大小
#   - 模型很确定时（一个 token 概率 0.9）→ 候选集很小
#   - 模型不确定时（多个 token 概率接近）→ 候选集较大
#

def top_p_sampling(probs: list[float], p: float) -> list[float]:
    """实现 Top-P (Nucleus) 采样，返回过滤后的概率分布。

    Args:
        probs: 原始概率分布（已经经过 softmax）
        p: 累积概率阈值（如 0.9）

    Returns:
        过滤后的概率分布（不在 Top-P 集合中的位置概率为 0，
        集合内的概率按比例重新归一化使总和为 1）
    """
    # ======== TODO 4: 在这里写你的代码 ========
    # 提示：
    #   1. 将 (概率, 原始索引) 按概率从大到小排序
    #   2. 从大到小累加概率，直到累加值 >= p
    #      记录哪些索引被包含在 Top-P 集合中
    #   3. 创建新的概率列表（长度同 probs）：
    #      - 在 Top-P 集合中的位置：保留原始概率
    #      - 不在集合中的位置：设为 0
    #   4. 对新列表做归一化（除以总和使之和为 1）
    #   5. 返回新的概率分布

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 4 ========


# ============================================================
# 🚀 Part 5: 投机采样 (Speculative Decoding)
# ============================================================
#
# 用一个快速的"草稿模型"生成候选 token，
# 然后让目标大模型验证。验证是并行的，所以比逐个生成快。
#
# 简化版流程：
# 1. 草稿模型生成 K 个候选 token（用各自的概率分布）
# 2. 目标模型对每个位置给出自己的概率分布
# 3. 对于每个位置，如果草稿模型选的 token 的概率在目标模型中
#    也"足够高"（具体：目标概率 >= 草稿概率），则接受
#    否则按一定概率拒绝
# 4. 在第一个被拒绝的位置停下，用目标模型重新采样
#

def speculative_decode(
    draft_tokens: list[int],
    draft_probs: list[list[float]],
    target_probs: list[list[float]],
) -> dict:
    """模拟投机采样的验证过程。

    Args:
        draft_tokens: 草稿模型生成的 token ID 列表（长度 K）
        draft_probs: 草稿模型在每个位置的概率分布（K 个分布）
        target_probs: 目标模型在每个位置的概率分布（K 个分布）

    Returns:
        {
            'accepted_count': 被接受的 token 数量,
            'accepted_tokens': 被接受的 token 列表,
            'acceptance_rate': 接受率 (accepted / total),
        }

    验证规则（简化版）：
    对于第 i 个位置，草稿选择的 token 为 t = draft_tokens[i]
    - 如果 target_probs[i][t] >= draft_probs[i][t]：一定接受
    - 如果 target_probs[i][t] < draft_probs[i][t]：
      以概率 target_probs[i][t] / draft_probs[i][t] 接受
    - 一旦某个位置被拒绝，后续全部拒绝（从该位置重新生成）
    """
    # ======== TODO 5: 在这里写你的代码 ========
    # 提示：
    #   1. 创建 accepted_tokens 列表
    #   2. 遍历每个位置 i (0 到 len(draft_tokens)-1)：
    #      a. 获取草稿选择的 token：t = draft_tokens[i]
    #      b. 获取目标模型对该 token 的概率：p_target = target_probs[i][t]
    #      c. 获取草稿模型对该 token 的概率：p_draft = draft_probs[i][t]
    #      d. 计算接受概率：accept_prob = min(1.0, p_target / p_draft)
    #      e. 生成随机数：r = random.random()
    #      f. 如果 r < accept_prob：接受，把 t 加入 accepted_tokens
    #         否则：拒绝，停止循环
    #   3. 计算 accepted_count 和 acceptance_rate
    #   4. 返回字典

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 5 ========


# ============================================================
# 🧪 测试 — 运行 python exercise.py 来检查你的实现
# ============================================================

def test_kv_cache():
    print("=" * 55)
    print("测试 Part 1: kv_cache_generate()")
    print("=" * 55)

    result = kv_cache_generate(prompt_length=100, generate_length=200)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    # 无 Cache: sum(100 + i for i in range(200)) = 200*100 + sum(0..199) = 20000 + 19900 = 39900
    expected_without = sum(100 + i for i in range(200))
    # 有 Cache: 100 + 199 = 299
    expected_with = 100 + 199

    if result['without_cache_ops'] != expected_without:
        print(f"  ❌ 无 Cache 计算量：期望 {expected_without}，得到 {result['without_cache_ops']}")
        return False

    if result['with_cache_ops'] != expected_with:
        print(f"  ❌ 有 Cache 计算量：期望 {expected_with}，得到 {result['with_cache_ops']}")
        return False

    speedup = expected_without / expected_with
    if abs(result['speedup'] - speedup) < 0.01:
        print(f"  ✅ 无 KV Cache: {expected_without:,} 次 K/V 计算")
        print(f"  ✅ 有 KV Cache: {expected_with:,} 次 K/V 计算")
        print(f"  ✅ 加速比: {speedup:.1f}×")
        print(f"     → KV Cache 在生成 200 token 时节省了 {(1-1/speedup)*100:.1f}% 的 K/V 计算！")
        return True
    else:
        print(f"  ❌ 加速比：期望 {speedup:.2f}，得到 {result['speedup']:.2f}")
        return False


def test_quantization():
    print("\n" + "=" * 55)
    print("测试 Part 2: quantize_and_dequantize()")
    print("=" * 55)

    random.seed(123)
    values = [random.gauss(0, 0.5) for _ in range(100)]

    result = quantize_and_dequantize(values, bits=8)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if len(result['quantized']) != 100:
        print(f"  ❌ quantized 长度应为 100，得到 {len(result['quantized'])}")
        return False

    if len(result['dequantized']) != 100:
        print(f"  ❌ dequantized 长度应为 100，得到 {len(result['dequantized'])}")
        return False

    # 检查量化值在合理范围内
    for q in result['quantized']:
        if q < 0 or q > 255:
            print(f"  ❌ INT8 量化值应在 [0, 255]，得到 {q}")
            return False

    print(f"  ✅ INT8 量化值范围正确 [0, 255]")
    print(f"  ✅ 最大误差: {result['max_error']:.6f}")
    print(f"  ✅ 平均误差: {result['mean_error']:.6f}")

    # 对于正态分布 ±2σ 内的数据，INT8 误差应该很小
    if result['mean_error'] < 0.01:
        print(f"     → 平均误差 < 0.01，量化几乎无损！")
    else:
        print(f"     ⚠️ 平均误差偏大，检查量化公式")

    # 测试 4-bit
    result4 = quantize_and_dequantize(values, bits=4)
    if result4 is not None and result4['mean_error'] > result['mean_error']:
        print(f"  ✅ INT4 平均误差 ({result4['mean_error']:.6f}) > INT8 ({result['mean_error']:.6f})")
        print(f"     → 位数越少精度越低，符合预期")
        return True
    elif result4 is not None:
        print(f"  ⚠️  INT4 误差应大于 INT8（位数少→精度低）")
        return True
    return True


def test_temperature_sampling():
    print("\n" + "=" * 55)
    print("测试 Part 3: temperature_sampling()")
    print("=" * 55)

    logits = [2.0, 1.0, 0.5, -1.0, 0.0]

    # T = 1.0: 应该等于普通 softmax
    result_t1 = temperature_sampling(logits, temperature=1.0)
    if result_t1 is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected_t1 = softmax(logits)
    if all(abs(result_t1[i] - expected_t1[i]) < 1e-6 for i in range(5)):
        print(f"  ✅ T=1.0: 等于原始 softmax ✓")
    else:
        print(f"  ❌ T=1.0 应等于原始 softmax")
        print(f"     期望: {[f'{p:.4f}' for p in expected_t1]}")
        print(f"     得到: {[f'{p:.4f}' for p in result_t1]}")
        return False

    # T = 0.5: 分布应该更尖锐（最大值概率更高）
    result_t05 = temperature_sampling(logits, temperature=0.5)
    if result_t05[0] > result_t1[0]:
        print(f"  ✅ T=0.5: 最高概率 {result_t05[0]:.4f} > T=1.0 的 {result_t1[0]:.4f}（更尖锐 ✓）")
    else:
        print(f"  ❌ T<1 应该让分布更尖锐（最高概率增大）")
        return False

    # T = 2.0: 分布应该更平坦（最大值概率更低）
    result_t2 = temperature_sampling(logits, temperature=2.0)
    if result_t2[0] < result_t1[0]:
        print(f"  ✅ T=2.0: 最高概率 {result_t2[0]:.4f} < T=1.0 的 {result_t1[0]:.4f}（更平坦 ✓）")
    else:
        print(f"  ❌ T>1 应该让分布更平坦（最高概率降低）")
        return False

    # T ≈ 0: 应该接近 one-hot
    result_t001 = temperature_sampling(logits, temperature=0.01)
    if result_t001[0] > 0.99:
        print(f"  ✅ T≈0: 最高概率 {result_t001[0]:.6f} ≈ 1.0（贪心 ✓）")
        return True
    else:
        print(f"  ⚠️  T≈0 时最高概率应接近 1.0，得到 {result_t001[0]:.4f}")
        return True  # 不算硬失败


def test_top_p_sampling():
    print("\n" + "=" * 55)
    print("测试 Part 4: top_p_sampling()")
    print("=" * 55)

    probs = [0.4, 0.3, 0.15, 0.10, 0.05]

    # p = 0.8: 应该保留前 3 个 (0.4 + 0.3 + 0.15 = 0.85 >= 0.8)
    result = top_p_sampling(probs, p=0.8)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if len(result) != 5:
        print(f"  ❌ 返回长度应为 5，得到 {len(result)}")
        return False

    # 检查总和 ≈ 1
    total = sum(result)
    if abs(total - 1.0) > 1e-6:
        print(f"  ❌ 概率总和应为 1.0，得到 {total:.6f}")
        return False

    print(f"  ✅ 概率总和 = {total:.6f} ✓")

    # 检查最后两个被截断（变为 0 或非常小）
    # p=0.8, 前两个就 0.7, 加第三个 0.85 > 0.8
    if result[3] < 1e-6 and result[4] < 1e-6:
        print(f"  ✅ Top-P=0.8 过滤结果: [{', '.join(f'{p:.4f}' for p in result)}]")
        print(f"     → 保留了前 3 个 token（累积概率 0.85 ≥ 0.8）")
        print(f"     → 后 2 个被过滤（概率设为 0）")
    else:
        print(f"  ⚠️  Top-P=0.8 应该过滤掉后面的 token")
        print(f"     得到: {[f'{p:.4f}' for p in result]}")

    # 检查保留的概率被重新归一化
    kept_sum = probs[0] + probs[1] + probs[2]
    expected_0 = probs[0] / kept_sum
    if abs(result[0] - expected_0) < 1e-4:
        print(f"  ✅ 保留的概率被正确归一化 ✓")
        return True
    else:
        print(f"  ⚠️  归一化可能有问题：期望 result[0]={expected_0:.4f}，得到 {result[0]:.4f}")
        return True


def test_speculative_decode():
    print("\n" + "=" * 55)
    print("测试 Part 5: speculative_decode()")
    print("=" * 55)

    random.seed(42)

    # 场景：草稿生成了 5 个 token
    # 目标模型大部分同意，但在某些位置概率不同
    draft_tokens = [3, 1, 4, 2, 0]

    # 草稿模型的概率分布（5 个位置，每个有 5 个候选）
    draft_probs = [
        [0.1, 0.1, 0.1, 0.6, 0.1],  # 位置0：选了 token 3 (概率 0.6)
        [0.1, 0.5, 0.1, 0.2, 0.1],  # 位置1：选了 token 1 (概率 0.5)
        [0.1, 0.1, 0.1, 0.1, 0.6],  # 位置2：选了 token 4 (概率 0.6)
        [0.1, 0.1, 0.5, 0.2, 0.1],  # 位置3：选了 token 2 (概率 0.5)
        [0.4, 0.2, 0.1, 0.2, 0.1],  # 位置4：选了 token 0 (概率 0.4)
    ]

    # 目标模型的概率分布
    target_probs = [
        [0.1, 0.1, 0.1, 0.5, 0.2],  # 位置0：对 token 3 概率 0.5 (< 0.6 但接近)
        [0.1, 0.6, 0.1, 0.1, 0.1],  # 位置1：对 token 1 概率 0.6 (> 0.5，一定接受)
        [0.1, 0.1, 0.1, 0.1, 0.6],  # 位置2：对 token 4 概率 0.6 (= 0.6，一定接受)
        [0.1, 0.1, 0.4, 0.2, 0.2],  # 位置3：对 token 2 概率 0.4 (< 0.5)
        [0.3, 0.2, 0.2, 0.2, 0.1],  # 位置4：对 token 0 概率 0.3 (< 0.4)
    ]

    result = speculative_decode(draft_tokens, draft_probs, target_probs)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    required_keys = ['accepted_count', 'accepted_tokens', 'acceptance_rate']
    for key in required_keys:
        if key not in result:
            print(f"  ❌ 返回的字典缺少 '{key}' 键")
            return False

    accepted = result['accepted_count']
    rate = result['acceptance_rate']

    print(f"  📊 投机采样结果：")
    print(f"     草稿 tokens: {draft_tokens}")
    print(f"     接受的 tokens: {result['accepted_tokens']}")
    print(f"     接受数量: {accepted} / 5")
    print(f"     接受率: {rate:.1%}")

    if accepted >= 0 and accepted <= 5:
        print(f"  ✅ 接受数量在合理范围 [0, 5] ✓")
    else:
        print(f"  ❌ 接受数量应在 [0, 5]，得到 {accepted}")
        return False

    if abs(rate - accepted / 5) < 1e-6:
        print(f"  ✅ 接受率计算正确 ✓")
    else:
        print(f"  ❌ 接受率应为 {accepted}/5 = {accepted/5:.4f}，得到 {rate:.4f}")
        return False

    # 验证 accepted_tokens 和 draft_tokens 的前 accepted 个一致
    for i in range(accepted):
        if result['accepted_tokens'][i] != draft_tokens[i]:
            print(f"  ❌ accepted_tokens[{i}] 应为 {draft_tokens[i]}")
            return False

    print(f"  ✅ 接受的 token 序列正确 ✓")

    # 运行多次看概率性
    random.seed(100)
    total_accepted = 0
    n_runs = 100
    for _ in range(n_runs):
        r = speculative_decode(draft_tokens, draft_probs, target_probs)
        total_accepted += r['accepted_count']

    avg_accepted = total_accepted / n_runs
    print(f"\n  📈 100 次模拟平均接受: {avg_accepted:.2f} / 5 tokens")
    print(f"     → 目标模型和草稿模型越一致，接受率越高")
    print(f"     → 实际中同系列模型的接受率通常在 70-85%")

    return True


if __name__ == "__main__":
    print()
    print("🎓 第六课练习：实现推理优化")
    print("=" * 55)
    print()

    all_passed = True
    all_passed = test_kv_cache() and all_passed
    all_passed = test_quantization() and all_passed
    all_passed = test_temperature_sampling() and all_passed
    all_passed = test_top_p_sampling() and all_passed
    all_passed = test_speculative_decode() and all_passed

    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 全部通过！你已经掌握了推理优化的核心技术！")
        print("   你刚刚亲手实现了：")
        print("   KV Cache → 量化 → 温度采样 → Top-P 采样 → 投机采样")
        print()
        print("   这些就是 ChatGPT/Claude 能快速响应数亿用户的秘密。")
        print("   真实的推理系统还涉及：分布式推理、请求调度、显存管理、")
        print("   模型并行等工程挑战。但核心优化思想就是你刚实现的这些。")
        print()
        print("   🎓 恭喜完成全部六节课的学习！")
        print("   你现在对大模型从训练到部署的完整链路有了深入的理解。")
    else:
        print("💪 还有测试没通过，继续加油！")
        print("   提示：按照 TODO 的顺序逐个实现，每完成一个就运行一次检查")
    print("=" * 55)
    print()
