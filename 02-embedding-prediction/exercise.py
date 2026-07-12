"""
============================================================
第二课练习：Embedding、Softmax 与 Next-Token Prediction
============================================================

在这个练习中，你将亲手实现大模型"猜下一个词"的完整计算链路：
  Token ID → Embedding 向量 → 线性变换 → Softmax → 概率分布 → 交叉熵损失

我们使用纯 Python + math 库，不依赖 PyTorch/NumPy，
让你能看清每一步计算的本质。

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过 ✅

难度：⭐⭐⭐ (比第一课稍难，涉及少量数学)
预计用时：30-40 分钟
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


# ============================================================
# 🧱 Part 1: Embedding 查找
# ============================================================
#
# Embedding 本质就是一个查找表：给一个整数 ID，返回矩阵中对应的那一行。
# 这是整个前向传播的起点。
#
# embedding_matrix 形状为 (vocab_size, embed_dim)
# 例如：vocab_size=100, embed_dim=8 → 矩阵有 100 行，每行 8 个浮点数
#

def embedding_lookup(embedding_matrix: list[list[float]], token_id: int) -> list[float]:
    """根据 token_id 从 embedding_matrix 中取出对应的向量。

    Args:
        embedding_matrix: 词表大小 × 向量维度 的矩阵
        token_id: 要查找的 token 的整数编号

    Returns:
        一个向量（float 列表），长度 = embed_dim
    """
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：只需要一行代码。token_id 就是矩阵的行索引。

    pass  # ← 删掉这行，写你的实现
    return embedding_matrix[token_id]

    # ======== END TODO 1 ========


# ============================================================
# 📐 Part 2: 余弦相似度
# ============================================================
#
# 余弦相似度衡量两个向量"方向"上的相似程度，值域 [-1, 1]。
# 1 = 方向完全一致，0 = 正交，-1 = 方向完全相反。
#
# 公式：cos(a, b) = (a · b) / (|a| × |b|)
#   其中 |a| = sqrt(a1² + a2² + ... + an²)
#

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """计算两个向量的余弦相似度。

    Args:
        vec_a: 向量 A
        vec_b: 向量 B

    Returns:
        余弦相似度值，范围 [-1, 1]
    """
    # ======== TODO 2: 在这里写你的代码 ========
    # 提示：
    #   1. 用上面已给的 dot_product() 算 a · b
    #   2. 分别计算 |a| 和 |b|（向量的模 / L2范数）
    #      |a| = sqrt(a1² + a2² + ... + an²)  即 sqrt(dot_product(a, a))
    #   3. 返回 dot_product(a,b) / (|a| * |b|)
    #   4. 注意处理分母为 0 的情况（可以返回 0.0）

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 2 ========


# ============================================================
# 🔢 Part 3: Softmax
# ============================================================
#
# Softmax 把一组任意实数转化为概率分布（0~1 之间，总和为 1）。
# 公式：softmax(x_i) = e^(x_i) / Σ e^(x_j)
#
# 实用技巧：为了数值稳定性，通常先减去最大值再计算：
#   softmax(x_i) = e^(x_i - max(x)) / Σ e^(x_j - max(x))
# 结果是一样的（分子分母同时除以 e^max，约掉了），但避免了 e^x 溢出。
#

def softmax(logits: list[float]) -> list[float]:
    """将一组 logits（原始分数）转化为概率分布。

    Args:
        logits: 模型输出的原始分数列表

    Returns:
        概率列表，每个值在 [0,1] 之间，总和为 1
    """
    # ======== TODO 3: 在这里写你的代码 ========
    # 提示（按步骤来）：
    #   1. 找到 logits 中的最大值 max_val = max(logits)
    #   2. 对每个 logit 计算 e^(logit - max_val)，得到一个列表 exp_vals
    #   3. 计算 exp_vals 的总和 sum_exp
    #   4. 每个 exp_val 除以 sum_exp，得到概率

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 3 ========


# ============================================================
# 📉 Part 4: 交叉熵损失
# ============================================================
#
# 交叉熵损失衡量模型预测的概率分布和真实标签之间的差距。
# 对于 next-token prediction，真实标签是"正确的下一个 token"。
#
# 公式：loss = -log(p_correct)
#   其中 p_correct 是模型给正确答案分配的概率。
#

def cross_entropy_loss(probs: list[float], correct_index: int) -> float:
    """计算交叉熵损失。

    Args:
        probs: softmax 输出的概率列表（对应词表中每个 token）
        correct_index: 正确答案的索引

    Returns:
        损失值（非负浮点数，越小越好）
    """
    # ======== TODO 4: 在这里写你的代码 ========
    # 提示：
    #   1. 取出正确答案的概率 p = probs[correct_index]
    #   2. 为了避免 log(0) 报错，给 p 加一个极小值：p = max(p, 1e-10)
    #   3. 返回 -math.log(p)

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 4 ========


# ============================================================
# 🎯 Part 5: 完整的前向传播
# ============================================================
#
# 把上面的步骤串起来，模拟模型预测下一个 token 的完整过程：
#   1. 用 embedding_lookup 取出输入 token 的向量
#   2. 用一个线性变换把向量映射到词表大小（模拟 Transformer + output head）
#   3. 用 softmax 得到概率分布
#   4. 用 cross_entropy_loss 算损失
#

def predict_next_token(
    token_id: int,
    embedding_matrix: list[list[float]],
    output_matrix: list[list[float]],
    correct_next_id: int,
) -> tuple[list[float], float]:
    """模拟一次 next-token prediction 的前向传播。

    Args:
        token_id: 输入 token 的 ID
        embedding_matrix: Embedding 查找表 (vocab_size × embed_dim)
        output_matrix: 输出线性层的权重矩阵 (vocab_size × embed_dim)
        correct_next_id: 正确的下一个 token 的 ID

    Returns:
        (probs, loss)
        - probs: 词表上的概率分布
        - loss: 交叉熵损失
    """
    # ======== TODO 5: 在这里写你的代码 ========
    # 提示（按步骤来）：
    #   1. 用 embedding_lookup() 取出 token_id 对应的向量 embed_vec
    #   2. 用 mat_vec_mul(output_matrix, embed_vec) 计算 logits
    #      （这一步模拟了 "Transformer处理 + 线性输出头" 的效果）
    #   3. 用 softmax(logits) 得到概率分布 probs
    #   4. 用 cross_entropy_loss(probs, correct_next_id) 计算损失 loss
    #   5. 返回 (probs, loss)

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 5 ========


# ============================================================
# 🧪 测试 — 运行 python exercise.py 来检查你的实现
# ============================================================

def test_embedding_lookup():
    print("=" * 55)
    print("测试 Part 1: embedding_lookup()")
    print("=" * 55)

    matrix = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
    result = embedding_lookup(matrix, 1)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected = [0.4, 0.5, 0.6]
    if result == expected:
        print(f"  ✅ 通过！embedding_lookup(matrix, 1) = {result}")
        return True
    else:
        print(f"  ❌ 期望: {expected}，得到: {result}")
        return False


def test_cosine_similarity():
    print("\n" + "=" * 55)
    print("测试 Part 2: cosine_similarity()")
    print("=" * 55)

    result1 = cosine_similarity([1, 0, 0], [1, 0, 0])
    if result1 is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if abs(result1 - 1.0) < 1e-6:
        print(f"  ✅ 相同向量相似度 = {result1:.4f}（期望 1.0）")
    else:
        print(f"  ❌ 相同向量相似度应为 1.0，得到 {result1:.4f}")
        return False

    result2 = cosine_similarity([1, 0, 0], [0, 1, 0])
    if abs(result2) < 1e-6:
        print(f"  ✅ 正交向量相似度 = {result2:.4f}（期望 0.0）")
    else:
        print(f"  ❌ 正交向量相似度应为 0.0，得到 {result2:.4f}")
        return False

    result3 = cosine_similarity([1, 2, 3], [2, 4, 6])
    if abs(result3 - 1.0) < 1e-6:
        print(f"  ✅ 同方向向量相似度 = {result3:.4f}（期望 1.0）")
        return True
    else:
        print(f"  ❌ 同方向向量 [1,2,3] 和 [2,4,6] 相似度应为 1.0，得到 {result3:.4f}")
        return False


def test_softmax():
    print("\n" + "=" * 55)
    print("测试 Part 3: softmax()")
    print("=" * 55)

    result = softmax([2.0, 1.0, 0.1])
    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    total = sum(result)
    if abs(total - 1.0) < 1e-6:
        print(f"  ✅ 概率总和 = {total:.6f}（期望 1.0）")
    else:
        print(f"  ❌ 概率总和应为 1.0，得到 {total:.6f}")
        return False

    if result[0] > result[1] > result[2]:
        print(f"  ✅ 概率排序正确：{[f'{p:.4f}' for p in result]}")
    else:
        print(f"  ❌ logit 越大概率应越高，得到: {result}")
        return False

    big_result = softmax([1000.0, 1000.1, 999.9])
    if big_result is not None and abs(sum(big_result) - 1.0) < 1e-6:
        print(f"  ✅ 大数值稳定性测试通过")
        return True
    else:
        print(f"  ❌ 大数值情况下 softmax 不稳定，请确保减去了最大值")
        return False


def test_cross_entropy_loss():
    print("\n" + "=" * 55)
    print("测试 Part 4: cross_entropy_loss()")
    print("=" * 55)

    loss_high = cross_entropy_loss([0.9, 0.05, 0.05], 0)
    if loss_high is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    loss_low = cross_entropy_loss([0.01, 0.01, 0.98], 0)

    expected_high = -math.log(0.9)
    expected_low = -math.log(0.01)

    if abs(loss_high - expected_high) < 1e-6:
        print(f"  ✅ 高概率（0.9）的损失 = {loss_high:.4f}（很小，几乎没惩罚）")
    else:
        print(f"  ❌ 期望 {expected_high:.4f}，得到 {loss_high:.4f}")
        return False

    if abs(loss_low - expected_low) < 1e-4:
        print(f"  ✅ 低概率（0.01）的损失 = {loss_low:.4f}（很大，严重惩罚）")
    else:
        print(f"  ❌ 期望 {expected_low:.4f}，得到 {loss_low:.4f}")
        return False

    if loss_low > loss_high:
        print(f"  ✅ 验证：低概率的损失({loss_low:.2f}) > 高概率的损失({loss_high:.2f}) ✓")
        return True
    else:
        print(f"  ❌ 低概率应该有更大的损失")
        return False


def test_predict_next_token():
    print("\n" + "=" * 55)
    print("测试 Part 5: predict_next_token()")
    print("=" * 55)

    vocab_size = 10
    embed_dim = 4
    embed_matrix = make_random_matrix(vocab_size, embed_dim)
    out_matrix = make_random_matrix(vocab_size, embed_dim)

    result = predict_next_token(3, embed_matrix, out_matrix, 5)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    probs, loss = result

    if len(probs) == vocab_size:
        print(f"  ✅ 概率分布长度 = {len(probs)}（等于词表大小 {vocab_size}）")
    else:
        print(f"  ❌ 概率分布长度应为 {vocab_size}，得到 {len(probs)}")
        return False

    if abs(sum(probs) - 1.0) < 1e-6:
        print(f"  ✅ 概率总和 = {sum(probs):.6f}")
    else:
        print(f"  ❌ 概率总和应为 1.0，得到 {sum(probs):.6f}")
        return False

    if loss > 0:
        print(f"  ✅ 损失值 = {loss:.4f}（正数 ✓）")
    else:
        print(f"  ❌ 损失应为正数，得到 {loss}")
        return False

    top_token = probs.index(max(probs))
    print(f"  ✅ 模型预测最可能的下一个 token ID = {top_token}（概率 {probs[top_token]:.4f}）")
    print(f"     正确答案 token ID = 5（概率 {probs[5]:.4f}）")
    print(f"     （参数是随机的，所以预测大概率不对——这就是为什么需要训练！）")
    return True


def bonus_embedding_similarity():
    print("\n" + "=" * 55)
    print("🎁 Bonus: 体验 Embedding 语义聚类")
    print("=" * 55)

    print("  用手工设计的 Embedding 来验证余弦相似度：")
    print()

    embeddings = {
        '猫':   [0.9, 0.8, 0.1, 0.0, 0.0, 0.1],
        '狗':   [0.85, 0.75, 0.15, 0.0, 0.05, 0.1],
        '金鱼': [0.7, 0.3, 0.1, 0.0, 0.0, 0.5],
        '苹果': [0.0, 0.1, 0.9, 0.8, 0.0, 0.0],
        '香蕉': [0.0, 0.15, 0.85, 0.75, 0.05, 0.0],
        '钢筋': [0.0, 0.0, 0.0, 0.1, 0.9, 0.8],
    }

    pairs = [('猫', '狗'), ('猫', '金鱼'), ('苹果', '香蕉'), ('猫', '苹果'), ('猫', '钢筋')]

    for w1, w2 in pairs:
        sim = cosine_similarity(embeddings[w1], embeddings[w2])
        if sim is not None:
            bar = '█' * int(max(0, sim) * 20)
            print(f"  {w1:4s} vs {w2:4s}  相似度 = {sim:+.4f}  {bar}")
        else:
            print(f"  {w1} vs {w2}  ← cosine_similarity 返回了 None")

    print()
    print("  观察：猫🐱 和 狗🐕 相似度最高（都是宠物），")
    print("        苹果🍎 和 香蕉🍌 相似度也很高（都是水果），")
    print("        猫🐱 和 钢筋🔩 相似度最低（毫无关系）。")
    print("  这就是 Embedding 空间的魔力！")


if __name__ == "__main__":
    print()
    print("🎓 第二课练习：Embedding、Softmax 与 Next-Token Prediction")
    print("=" * 55)
    print()

    all_passed = True
    all_passed = test_embedding_lookup() and all_passed
    all_passed = test_cosine_similarity() and all_passed
    all_passed = test_softmax() and all_passed
    all_passed = test_cross_entropy_loss() and all_passed
    all_passed = test_predict_next_token() and all_passed

    if all_passed:
        bonus_embedding_similarity()

    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 全部通过！你已经理解了预训练的核心计算链路！")
        print("   你刚刚亲手实现了：")
        print("   Embedding查找 → 余弦相似度 → Softmax → 交叉熵 → 前向传播")
        print("   下一步：打开第三课学习 Transformer 架构")
    else:
        print("💪 还有测试没通过，继续加油！")
        print("   提示：按照 TODO 的顺序逐个实现，每完成一个就运行一次检查")
    print("=" * 55)
    print()
