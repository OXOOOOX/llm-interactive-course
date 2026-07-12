"""
============================================================
第三课练习：手写 Self-Attention
============================================================

Self-Attention 是 Transformer 的核心——它让每个 token 能"看到"
序列中的其他 token，并根据相关性动态地融合上下文信息。

在这个练习中，你将从零实现 Self-Attention 的完整计算流程：
  生成 Q/K/V → 计算注意力分数 → 因果遮罩 → Softmax → 加权求和

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过 ✅

难度：⭐⭐⭐ (涉及矩阵运算，但每步都有详细提示)
预计用时：30-45 分钟
"""

import math
import random

random.seed(42)


# ============================================================
# 辅助函数（已实现，不需要修改）
# ============================================================

def make_random_matrix(rows: int, cols: int) -> list[list[float]]:
    """生成一个 rows × cols 的随机矩阵，值在 [-0.5, 0.5] 之间。"""
    return [[random.uniform(-0.5, 0.5) for _ in range(cols)] for _ in range(rows)]


def dot_product(vec_a: list[float], vec_b: list[float]) -> float:
    """计算两个向量的点积。"""
    return sum(a * b for a, b in zip(vec_a, vec_b))


def mat_vec_mul(matrix: list[list[float]], vec: list[float]) -> list[float]:
    """矩阵乘向量：matrix (m×n) × vec (n,) → result (m,)。"""
    return [dot_product(row, vec) for row in matrix]


def mat_mul(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    """矩阵乘矩阵：A (m×n) × B (n×p) → result (m×p)。"""
    m = len(A)
    n = len(B)
    p = len(B[0])
    result = [[0.0] * p for _ in range(m)]
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    return result


def softmax(logits: list[float]) -> list[float]:
    """将一组 logits 转化为概率分布（带数值稳定处理）。"""
    max_val = max(logits)
    exp_vals = [math.exp(x - max_val) for x in logits]
    sum_exp = sum(exp_vals)
    return [v / sum_exp for v in exp_vals]


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    """矩阵转置。"""
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[i][j] for i in range(rows)] for j in range(cols)]


# ============================================================
# 🧱 Part 1: 计算注意力分数 (Attention Scores)
# ============================================================
#
# 注意力分数衡量 Query 和 Key 之间的"相关性"。
# 对于每对 (i, j)，分数 = Q[i] · K[j] / √d_k
#
# 输入：
#   Q: (seq_len, d_k) — 每行是一个 token 的 Query 向量
#   K: (seq_len, d_k) — 每行是一个 token 的 Key 向量
#
# 输出：
#   scores: (seq_len, seq_len) — scores[i][j] = Q[i]·K[j] / √d_k
#

def compute_attention_scores(Q: list[list[float]], K: list[list[float]]) -> list[list[float]]:
    """计算缩放点积注意力分数。

    Args:
        Q: Query 矩阵，形状 (seq_len, d_k)
        K: Key 矩阵，形状 (seq_len, d_k)

    Returns:
        scores 矩阵，形状 (seq_len, seq_len)
        其中 scores[i][j] = dot(Q[i], K[j]) / sqrt(d_k)
    """
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：
    #   1. 获取 d_k（Q 的列数 = 每个向量的维度）
    #   2. 计算缩放因子 scale = sqrt(d_k)
    #   3. 对于每对 (i, j)，计算 dot_product(Q[i], K[j]) / scale
    #   4. 返回 seq_len × seq_len 的二维列表

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 1 ========


# ============================================================
# 🎭 Part 2: 因果遮罩 (Causal Mask)
# ============================================================
#
# 在生成式模型中，token 不能"偷看"后面的内容。
# 因果遮罩把 j > i 的位置设为 -∞ (用 float('-inf') 表示)。
# 这样 Softmax 之后这些位置的权重会变成 0。
#
# 例如 4×4 的 scores 遮罩后：
#   [[s00,  -∞,  -∞,  -∞ ],
#    [s10, s11,  -∞,  -∞ ],
#    [s20, s21, s22,  -∞ ],
#    [s30, s31, s32, s33]]
#

def apply_causal_mask(scores: list[list[float]]) -> list[list[float]]:
    """对注意力分数矩阵应用因果遮罩。

    Args:
        scores: 注意力分数矩阵 (seq_len, seq_len)

    Returns:
        遮罩后的分数矩阵，j > i 的位置被设为 float('-inf')
    """
    # ======== TODO 2: 在这里写你的代码 ========
    # 提示：
    #   1. 获取 seq_len（矩阵的行数）
    #   2. 创建一个新矩阵（不要直接修改输入）
    #   3. 对于位置 (i, j)：
    #      - 如果 j <= i：保留原始分数
    #      - 如果 j > i：设为 float('-inf')
    #   4. 返回新矩阵

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 2 ========


# ============================================================
# 📊 Part 3: 计算注意力权重 (Attention Weights)
# ============================================================
#
# 对遮罩后的分数的每一行做 Softmax，得到注意力权重。
# 每行的权重之和 = 1，代表该 token 对其他 token 的"关注度分配"。
#

def compute_attention_weights(masked_scores: list[list[float]]) -> list[list[float]]:
    """对注意力分数的每一行做 Softmax，得到权重矩阵。

    Args:
        masked_scores: 遮罩后的分数矩阵 (seq_len, seq_len)

    Returns:
        权重矩阵 (seq_len, seq_len)，每行之和 = 1
    """
    # ======== TODO 3: 在这里写你的代码 ========
    # 提示：
    #   1. 对矩阵的每一行调用上面提供的 softmax() 函数
    #   2. 返回所有行的结果组成的新矩阵
    #   （非常简单，一个列表推导就够了）

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 3 ========


# ============================================================
# 🎯 Part 4: 计算注意力输出 (Attention Output)
# ============================================================
#
# 用权重对 Value 矩阵做加权求和。
# output[i] = Σ_j weights[i][j] * V[j]
#
# 直觉：每个 token 的输出 = 它关注的所有 token 的 Value 的加权混合
#

def compute_attention_output(
    weights: list[list[float]], V: list[list[float]]
) -> list[list[float]]:
    """用注意力权重对 Value 矩阵做加权求和。

    Args:
        weights: 注意力权重矩阵 (seq_len, seq_len)
        V: Value 矩阵 (seq_len, d_v)

    Returns:
        输出矩阵 (seq_len, d_v)
        output[i] = sum(weights[i][j] * V[j] for all j)
    """
    # ======== TODO 4: 在这里写你的代码 ========
    # 提示：
    #   1. 获取 seq_len 和 d_v（V 的列数）
    #   2. 对于输出的每一行 i：
    #      对于输出的每一列（维度）d：
    #        output[i][d] = sum(weights[i][j] * V[j][d] for j in range(seq_len))
    #   3. 返回结果矩阵
    #
    # 或者你可以直接用：return mat_mul(weights, V)（矩阵乘法就是加权求和！）

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 4 ========


# ============================================================
# 🧠 Part 5: 完整的 Self-Attention
# ============================================================
#
# 把上面的步骤串起来，实现完整的 Self-Attention：
#   1. 用权重矩阵把输入变换为 Q, K, V
#   2. 计算注意力分数
#   3. 应用因果遮罩
#   4. Softmax 得到权重
#   5. 加权求和得到输出
#

def self_attention(
    X: list[list[float]],
    W_Q: list[list[float]],
    W_K: list[list[float]],
    W_V: list[list[float]],
    use_causal_mask: bool = True,
) -> list[list[float]]:
    """完整的 Self-Attention 前向传播。

    Args:
        X: 输入矩阵 (seq_len, d_model)，每行是一个 token 的向量
        W_Q: Query 权重矩阵 (d_model, d_k)
        W_K: Key 权重矩阵 (d_model, d_k)
        W_V: Value 权重矩阵 (d_model, d_v)
        use_causal_mask: 是否使用因果遮罩

    Returns:
        输出矩阵 (seq_len, d_v)
    """
    # ======== TODO 5: 在这里写你的代码 ========
    # 提示（按步骤来）：
    #   1. 计算 Q = X × W_Q  →  用 mat_mul(X, W_Q)
    #   2. 计算 K = X × W_K  →  用 mat_mul(X, W_K)
    #   3. 计算 V = X × W_V  →  用 mat_mul(X, W_V)
    #   4. 计算注意力分数   →  用 compute_attention_scores(Q, K)
    #   5. 如果 use_causal_mask，应用因果遮罩  →  用 apply_causal_mask(scores)
    #   6. 计算注意力权重   →  用 compute_attention_weights(scores)
    #   7. 计算注意力输出   →  用 compute_attention_output(weights, V)
    #   8. 返回输出

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 5 ========


# ============================================================
# 🧪 测试 — 运行 python exercise.py 来检查你的实现
# ============================================================

def test_attention_scores():
    print("=" * 55)
    print("测试 Part 1: compute_attention_scores()")
    print("=" * 55)

    Q = [[1.0, 0.0], [0.0, 1.0]]
    K = [[1.0, 0.0], [0.0, 1.0]]

    result = compute_attention_scores(Q, K)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    d_k = 2
    scale = math.sqrt(d_k)
    expected = [[1.0 / scale, 0.0], [0.0, 1.0 / scale]]

    ok = True
    for i in range(2):
        for j in range(2):
            if abs(result[i][j] - expected[i][j]) > 1e-6:
                ok = False

    if ok:
        print(f"  ✅ 通过！正交向量点积=0，自身点积=1/√d_k={1/scale:.4f}")
        print(f"     scores = {[[f'{v:.4f}' for v in row] for row in result]}")
    else:
        print(f"  ❌ 期望: {expected}")
        print(f"     得到: {result}")
        return False

    Q2 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    K2 = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    result2 = compute_attention_scores(Q2, K2)
    scale2 = math.sqrt(3)
    exp_00 = 1.0 / scale2
    exp_01 = 2.0 / scale2

    if abs(result2[0][0] - exp_00) < 1e-6 and abs(result2[0][1] - exp_01) < 1e-6:
        print(f"  ✅ 非方阵测试也通过！")
        return True
    else:
        print(f"  ❌ 非方阵测试失败")
        print(f"     期望 scores[0][0]={exp_00:.4f}, scores[0][1]={exp_01:.4f}")
        print(f"     得到 scores[0][0]={result2[0][0]:.4f}, scores[0][1]={result2[0][1]:.4f}")
        return False


def test_causal_mask():
    print("\n" + "=" * 55)
    print("测试 Part 2: apply_causal_mask()")
    print("=" * 55)

    scores = [[1.0, 2.0, 3.0],
              [4.0, 5.0, 6.0],
              [7.0, 8.0, 9.0]]

    result = apply_causal_mask(scores)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected = [[1.0, float('-inf'), float('-inf')],
                [4.0, 5.0, float('-inf')],
                [7.0, 8.0, 9.0]]

    ok = True
    for i in range(3):
        for j in range(3):
            if expected[i][j] == float('-inf'):
                if result[i][j] != float('-inf'):
                    ok = False
            elif abs(result[i][j] - expected[i][j]) > 1e-6:
                ok = False

    if ok:
        print("  ✅ 通过！上三角被正确遮罩为 -∞")
        print(f"     第 1 行（token 0 只能看自己）: {result[0]}")
        print(f"     第 2 行（能看前 2 个）:        {result[1]}")
        print(f"     第 3 行（能看所有）:           {result[2]}")
    else:
        print(f"  ❌ 遮罩结果不正确")
        print(f"     期望: {expected}")
        print(f"     得到: {result}")
        return False

    if scores[0][1] == 2.0:
        print("  ✅ 原始矩阵未被修改 ✓")
        return True
    else:
        print("  ❌ 警告：原始矩阵被修改了！请创建新矩阵而不是就地修改")
        return False


def test_attention_weights():
    print("\n" + "=" * 55)
    print("测试 Part 3: compute_attention_weights()")
    print("=" * 55)

    masked = [[1.0, float('-inf'), float('-inf')],
              [1.0, 2.0, float('-inf')],
              [1.0, 2.0, 3.0]]

    result = compute_attention_weights(masked)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if abs(result[0][0] - 1.0) < 1e-6 and abs(result[0][1]) < 1e-6:
        print(f"  ✅ 第 1 行：只能看自己 → 权重 = [{result[0][0]:.4f}, {result[0][1]:.6f}, {result[0][2]:.6f}]")
    else:
        print(f"  ❌ 第 1 行权重不正确：{result[0]}")
        print(f"     当只有一个有效位置时，那个位置的权重应该是 1.0")
        return False

    row1_sum = sum(result[1])
    if abs(row1_sum - 1.0) < 1e-6:
        print(f"  ✅ 第 2 行：权重之和 = {row1_sum:.6f} ≈ 1.0")
    else:
        print(f"  ❌ 第 2 行权重之和 = {row1_sum}，应为 1.0")
        return False

    if result[1][0] < result[1][1]:
        print(f"  ✅ 第 2 行：分数更高的位置权重更大 ({result[1][0]:.4f} < {result[1][1]:.4f})")
    else:
        print(f"  ❌ 第 2 行权重顺序错误：高分数应有更高权重")
        return False

    row2_sum = sum(result[2])
    if abs(row2_sum - 1.0) < 1e-6 and result[2][0] < result[2][1] < result[2][2]:
        print(f"  ✅ 第 3 行：三个权重递增，总和=1 ✓")
        return True
    else:
        print(f"  ❌ 第 3 行验证失败：{result[2]}")
        return False


def test_attention_output():
    print("\n" + "=" * 55)
    print("测试 Part 4: compute_attention_output()")
    print("=" * 55)

    weights = [[1.0, 0.0, 0.0],
               [0.5, 0.5, 0.0],
               [0.2, 0.3, 0.5]]

    V = [[1.0, 0.0],
         [0.0, 1.0],
         [1.0, 1.0]]

    result = compute_attention_output(weights, V)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected_0 = [1.0, 0.0]
    expected_1 = [0.5, 0.5]
    expected_2 = [0.2 * 1 + 0.3 * 0 + 0.5 * 1, 0.2 * 0 + 0.3 * 1 + 0.5 * 1]

    ok = True
    for d in range(2):
        if abs(result[0][d] - expected_0[d]) > 1e-6:
            ok = False
        if abs(result[1][d] - expected_1[d]) > 1e-6:
            ok = False
        if abs(result[2][d] - expected_2[d]) > 1e-6:
            ok = False

    if ok:
        print(f"  ✅ 第 1 个 token（权重=[1,0,0]）: output = {result[0]} — 完全复制 V[0]")
        print(f"  ✅ 第 2 个 token（权重=[0.5,0.5,0]）: output = {result[1]} — V[0]和V[1]的平均")
        print(f"  ✅ 第 3 个 token（权重=[0.2,0.3,0.5]）: output = [{result[2][0]:.2f}, {result[2][1]:.2f}] — 加权混合")
        return True
    else:
        print(f"  ❌ 输出不正确")
        print(f"     期望第 1 行: {expected_0}，得到: {result[0]}")
        print(f"     期望第 2 行: {expected_1}，得到: {result[1]}")
        print(f"     期望第 3 行: {expected_2}，得到: {result[2]}")
        return False


def test_self_attention():
    print("\n" + "=" * 55)
    print("测试 Part 5: self_attention()")
    print("=" * 55)

    seq_len = 3
    d_model = 4
    d_k = 3

    X = make_random_matrix(seq_len, d_model)
    W_Q = make_random_matrix(d_model, d_k)
    W_K = make_random_matrix(d_model, d_k)
    W_V = make_random_matrix(d_model, d_k)

    result = self_attention(X, W_Q, W_K, W_V, use_causal_mask=True)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if len(result) != seq_len:
        print(f"  ❌ 输出行数应为 {seq_len}，得到 {len(result)}")
        return False

    if len(result[0]) != d_k:
        print(f"  ❌ 输出列数应为 {d_k}（d_v），得到 {len(result[0])}")
        return False

    print(f"  ✅ 输出形状正确: ({len(result)}, {len(result[0])}) = (seq_len, d_v)")

    Q = mat_mul(X, W_Q)
    first_token_output = result[0]
    V = mat_mul(X, W_V)
    diff = sum(abs(first_token_output[d] - V[0][d]) for d in range(d_k))
    if diff < 1e-6:
        print(f"  ✅ 因果遮罩验证：第一个 token 只能看自己，输出 = V[0] ✓")
    else:
        print(f"  ❌ 第一个 token 的输出应该等于 V[0]（因为因果遮罩只允许看自己）")
        print(f"     V[0]   = {V[0]}")
        print(f"     output = {first_token_output}")
        return False

    result_no_mask = self_attention(X, W_Q, W_K, W_V, use_causal_mask=False)
    if result_no_mask is not None and len(result_no_mask) == seq_len:
        diff_total = 0
        for i in range(seq_len):
            for d in range(d_k):
                diff_total += abs(result[i][d] - result_no_mask[i][d])
        if diff_total > 1e-6:
            print(f"  ✅ 有/无遮罩结果不同（差异={diff_total:.4f}），说明遮罩生效了 ✓")
        else:
            print(f"  ⚠️  有/无遮罩结果相同，遮罩可能没有正确应用")
            return False
    else:
        print(f"  ⚠️  无遮罩模式返回异常")
        return False

    print(f"\n  📋 Self-Attention 输出（带因果遮罩）：")
    for i, row in enumerate(result):
        print(f"     token {i}: [{', '.join(f'{v:.4f}' for v in row)}]")

    return True


def bonus_attention_pattern():
    """展示注意力权重矩阵的可视化。"""
    print("\n" + "=" * 55)
    print("🎁 Bonus: 注意力权重可视化")
    print("=" * 55)

    seq_len = 5
    d_model = 8
    d_k = 4

    random.seed(123)
    X = make_random_matrix(seq_len, d_model)
    W_Q = make_random_matrix(d_model, d_k)
    W_K = make_random_matrix(d_model, d_k)
    W_V = make_random_matrix(d_model, d_k)

    Q = mat_mul(X, W_Q)
    K = mat_mul(X, W_K)

    scores = compute_attention_scores(Q, K)
    masked = apply_causal_mask(scores)
    weights = compute_attention_weights(masked)

    tokens = ['我', '喜欢', '学', 'AI', '。']

    print(f"\n  输入句子: {''.join(tokens)}")
    print(f"\n  注意力权重矩阵（行=Query，列=Key）：")
    print(f"{'':>8}", end='')
    for t in tokens:
        print(f'{t:>7}', end='')
    print()

    for i, row in enumerate(weights):
        print(f"  {tokens[i]:>4}  ", end='')
        for j, w in enumerate(row):
            if w < 0.01:
                block = '  · '
            elif w < 0.15:
                block = '  ░ '
            elif w < 0.30:
                block = '  ▒ '
            elif w < 0.50:
                block = '  ▓ '
            else:
                block = '  █ '
            print(f'{block:>7}', end='')
        print(f'  ← {[f"{w:.2f}" for w in row]}')

    print(f"\n  图例: · (<1%)  ░ (1-15%)  ▒ (15-30%)  ▓ (30-50%)  █ (>50%)")
    print(f"  注意下三角模式：每个 token 只能关注自己和前面的 token（因果遮罩）")


if __name__ == "__main__":
    print()
    print("🎓 第三课练习：手写 Self-Attention")
    print("=" * 55)
    print()

    all_passed = True
    all_passed = test_attention_scores() and all_passed
    all_passed = test_causal_mask() and all_passed
    all_passed = test_attention_weights() and all_passed
    all_passed = test_attention_output() and all_passed
    all_passed = test_self_attention() and all_passed

    if all_passed:
        bonus_attention_pattern()

    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 全部通过！你已经完整实现了 Self-Attention！")
        print("   你刚刚亲手实现了：")
        print("   注意力分数 → 因果遮罩 → Softmax权重 → 加权求和 → 完整Attention")
        print()
        print("   这就是 GPT、Claude、LLaMA 等大模型核心中的核心机制。")
        print("   在真实模型中，这个计算会在 96 个头、80+ 层中并行重复执行。")
    else:
        print("💪 还有测试没通过，继续加油！")
        print("   提示：按照 TODO 的顺序逐个实现，每完成一个就运行一次检查")
    print("=" * 55)
    print()
