"""
============================================================
第五课练习：实现对齐算法（RLHF / DPO）
============================================================

对齐是让模型从"能说话"变成"说好话"的关键步骤。
核心思想：用人类的偏好来引导模型——让它学会"什么是好回答"。

在这个练习中，你将亲手实现对齐的核心组件：
  奖励函数 → 偏好损失 → 对数比率 → DPO 损失 → 对齐训练循环

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过 ✅

难度：⭐⭐⭐ (涉及 sigmoid/log 运算，但公式都有详细提示)
预计用时：30-45 分钟
"""

import math
import random

random.seed(42)


# ============================================================
# 辅助函数（已实现，不需要修改）
# ============================================================

def sigmoid(x: float) -> float:
    """Sigmoid 函数：将任意实数映射到 (0, 1) 之间。"""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    else:
        exp_x = math.exp(x)
        return exp_x / (1.0 + exp_x)


def log_sigmoid(x: float) -> float:
    """log(sigmoid(x)) 的数值稳定版本。"""
    if x >= 0:
        return -math.log(1 + math.exp(-x))
    else:
        return x - math.log(1 + math.exp(x))


# ============================================================
# 🧱 Part 1: 奖励函数 (Reward Function)
# ============================================================
#
# 奖励模型为每个"回答"打一个分数。
# 这里我们用一个简化的规则来模拟奖励函数的行为：
#   - 根据回答的几个质量维度（相关性、详细度、安全性）
#   - 用加权求和计算综合得分
#
# 在真实的 RLHF 中，奖励模型是一个神经网络，
# 从人类偏好数据中学到"什么是好回答"。
# 但核心思想一样：输入一个回答 → 输出一个分数。
#

def compute_reward(
    relevance: float, detail: float, safety: float,
    weights: list[float] = [0.4, 0.3, 0.3]
) -> float:
    """计算回答的综合奖励分数。

    Args:
        relevance: 相关性得分 (0-1)，回答是否切题
        detail: 详细度得分 (0-1)，信息是否充分
        safety: 安全性得分 (0-1)，是否无害
        weights: 三个维度的权重 [w_relevance, w_detail, w_safety]

    Returns:
        加权综合得分 = relevance × w[0] + detail × w[1] + safety × w[2]
    """
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：
    #   1. 将三个维度的得分分别乘以对应的权重
    #   2. 求和得到综合得分
    #   3. 返回结果
    #
    # 就是一个加权平均！

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 1 ========


# ============================================================
# ⚖️ Part 2: 偏好损失 (Preference Loss)
# ============================================================
#
# 奖励模型的训练目标：让"好回答"的奖励高于"差回答"。
# 使用 Bradley-Terry 模型的损失函数：
#
#   loss = -log(sigmoid(reward_good - reward_bad))
#
# 直觉：
#   - 当 reward_good >> reward_bad 时：sigmoid → 1，loss → 0（好！模型分辨力强）
#   - 当 reward_good ≈ reward_bad 时：sigmoid → 0.5，loss → 0.69（模型无法区分）
#   - 当 reward_good << reward_bad 时：sigmoid → 0，loss → ∞（糟糕！排序反了）
#

def preference_loss(reward_good: float, reward_bad: float) -> float:
    """计算偏好对的训练损失。

    Args:
        reward_good: 奖励模型给"好回答"的分数
        reward_bad: 奖励模型给"差回答"的分数

    Returns:
        损失 = -log(sigmoid(reward_good - reward_bad))
    """
    # ======== TODO 2: 在这里写你的代码 ========
    # 提示：
    #   1. 计算两个奖励的差值：diff = reward_good - reward_bad
    #   2. 用上面提供的 log_sigmoid(diff) 函数计算 log(sigmoid(diff))
    #   3. 取负号得到损失
    #   4. 返回损失
    #
    # 注意：使用 log_sigmoid() 而不是 -math.log(sigmoid(x))
    #       前者数值更稳定，避免 log(0) 的问题

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 2 ========


# ============================================================
# 📐 Part 3: 对数概率比 (Log Probability Ratio)
# ============================================================
#
# DPO 的核心计算是"对数概率比"：
#   log_ratio = log(π(y|x)) - log(π_ref(y|x))
#
# 它衡量的是：相比参考模型，当前模型有多"偏好"这个回答。
# - log_ratio > 0：当前模型比参考模型更喜欢这个回答
# - log_ratio < 0：当前模型比参考模型更不喜欢这个回答
# - log_ratio = 0：和参考模型一样
#
# 这里我们用简化的对数概率来模拟。
#

def compute_log_ratio(
    log_prob_current: float, log_prob_reference: float
) -> float:
    """计算当前模型和参考模型的对数概率比。

    Args:
        log_prob_current: 当前模型给这个回答的对数概率 log(π(y|x))
        log_prob_reference: 参考模型给这个回答的对数概率 log(π_ref(y|x))

    Returns:
        对数概率比 = log_prob_current - log_prob_reference
    """
    # ======== TODO 3: 在这里写你的代码 ========
    # 提示：
    #   就是一个减法！
    #   log(π/π_ref) = log(π) - log(π_ref)

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 3 ========


# ============================================================
# 🎯 Part 4: DPO 损失函数 (DPO Loss)
# ============================================================
#
# DPO 损失的完整公式：
#
#   loss = -log(sigmoid(β × (log_ratio_good - log_ratio_bad)))
#
# 其中：
#   log_ratio_good = log(π(好回答|x)) - log(π_ref(好回答|x))
#   log_ratio_bad  = log(π(差回答|x)) - log(π_ref(差回答|x))
#   β = 温度参数（控制偏离参考模型的程度）
#
# 直觉：
#   让当前模型相对于参考模型，更倾向于选择"好回答"而非"差回答"
#

def dpo_loss(
    log_prob_good_current: float,
    log_prob_good_reference: float,
    log_prob_bad_current: float,
    log_prob_bad_reference: float,
    beta: float = 0.1,
) -> float:
    """计算 DPO 损失。

    Args:
        log_prob_good_current: 当前模型对"好回答"的对数概率
        log_prob_good_reference: 参考模型对"好回答"的对数概率
        log_prob_bad_current: 当前模型对"差回答"的对数概率
        log_prob_bad_reference: 参考模型对"差回答"的对数概率
        beta: 温度参数

    Returns:
        DPO 损失值
    """
    # ======== TODO 4: 在这里写你的代码 ========
    # 提示（按步骤来）：
    #   1. 计算好回答的 log_ratio：
    #      log_ratio_good = compute_log_ratio(log_prob_good_current, log_prob_good_reference)
    #   2. 计算差回答的 log_ratio：
    #      log_ratio_bad = compute_log_ratio(log_prob_bad_current, log_prob_bad_reference)
    #   3. 计算差值并乘以 beta：
    #      scaled_diff = beta * (log_ratio_good - log_ratio_bad)
    #   4. 计算损失：loss = -log_sigmoid(scaled_diff)
    #   5. 返回损失

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 4 ========


# ============================================================
# 🚀 Part 5: 对齐训练循环 (Alignment Training)
# ============================================================
#
# 模拟一个简化的 DPO 训练过程：
# - 模型用一个"偏好分数"向量来表示（模拟 logits）
# - 每一步选一个偏好对，计算 DPO 损失的梯度，更新模型
# - 观察模型的偏好如何向人类标注的偏好靠拢
#
# 这里我们使用一个极简的模型：
# - model_scores[i] 代表模型对第 i 个选项的"偏好分数"
# - 训练目标：让 model_scores 排序与人类偏好一致
#

def alignment_training(
    initial_scores: list[float],
    preference_pairs: list[tuple[int, int]],
    learning_rate: float = 0.5,
    n_epochs: int = 10,
    beta: float = 0.1,
) -> dict:
    """执行简化的对齐训练。

    Args:
        initial_scores: 模型的初始偏好分数（每个选项一个分数）
        preference_pairs: 偏好对列表，每对 (good_idx, bad_idx) 表示
                         选项 good_idx 优于选项 bad_idx
        learning_rate: 学习率
        n_epochs: 训练轮数（遍历所有偏好对的次数）
        beta: DPO 温度参数

    Returns:
        包含训练结果的字典：
        {
            'final_scores': 训练后的偏好分数,
            'loss_history': 每步的损失列表,
            'score_history': 每步后的分数快照列表,
        }
    """
    # ======== TODO 5: 在这里写你的代码 ========
    # 提示（按步骤来）：
    #   1. 复制 initial_scores 到 scores（不修改原始输入）
    #      同时保存一份 reference_scores = initial_scores 的副本（固定不变）
    #   2. 创建 loss_history 和 score_history 列表
    #   3. 对于每个 epoch（共 n_epochs 个）：
    #      对于每个偏好对 (good_idx, bad_idx)：
    #        a. 计算 DPO 损失：
    #           - log_prob_good_current = scores[good_idx]
    #           - log_prob_good_reference = reference_scores[good_idx]
    #           - log_prob_bad_current = scores[bad_idx]
    #           - log_prob_bad_reference = reference_scores[bad_idx]
    #           - loss = dpo_loss(上述四个值, beta)
    #        b. 记录损失到 loss_history
    #        c. 计算梯度并更新 scores：
    #           - log_ratio_good = scores[good_idx] - reference_scores[good_idx]
    #           - log_ratio_bad = scores[bad_idx] - reference_scores[bad_idx]
    #           - scaled_diff = beta * (log_ratio_good - log_ratio_bad)
    #           - common = sigmoid(-scaled_diff) * beta
    #             （这是 DPO 损失对 scaled_diff 的梯度的简化形式）
    #           - scores[good_idx] += learning_rate * common
    #             （增加好回答的分数）
    #           - scores[bad_idx] -= learning_rate * common
    #             （降低差回答的分数）
    #        d. 记录当前 scores 的副本到 score_history
    #   4. 返回字典

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 5 ========


# ============================================================
# 🧪 测试 — 运行 python exercise.py 来检查你的实现
# ============================================================

def test_compute_reward():
    print("=" * 55)
    print("测试 Part 1: compute_reward()")
    print("=" * 55)

    result = compute_reward(0.9, 0.8, 1.0)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected = 0.9 * 0.4 + 0.8 * 0.3 + 1.0 * 0.3  # 0.36 + 0.24 + 0.30 = 0.90
    if abs(result - expected) < 1e-6:
        print(f"  ✅ 通过！高质量回答得分 = {result:.4f}")
    else:
        print(f"  ❌ 期望: {expected:.4f}，得到: {result:.4f}")
        return False

    # 测试低质量回答
    result2 = compute_reward(0.3, 0.2, 0.1)
    expected2 = 0.3 * 0.4 + 0.2 * 0.3 + 0.1 * 0.3  # 0.12 + 0.06 + 0.03 = 0.21
    if abs(result2 - expected2) < 1e-6:
        print(f"  ✅ 低质量回答得分 = {result2:.4f}（远低于高质量的 {result:.4f}）")
    else:
        print(f"  ❌ 期望: {expected2:.4f}，得到: {result2:.4f}")
        return False

    # 测试自定义权重
    result3 = compute_reward(1.0, 0.0, 0.0, weights=[1.0, 0.0, 0.0])
    if abs(result3 - 1.0) < 1e-6:
        print(f"  ✅ 自定义权重测试通过（只看相关性→得分=相关性）")
        return True
    else:
        print(f"  ❌ 自定义权重测试失败，期望 1.0，得到 {result3}")
        return False


def test_preference_loss():
    print("\n" + "=" * 55)
    print("测试 Part 2: preference_loss()")
    print("=" * 55)

    # 好回答分数远高于差回答 → loss 应该很低
    result1 = preference_loss(reward_good=5.0, reward_bad=1.0)
    if result1 is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected1 = -log_sigmoid(5.0 - 1.0)
    if abs(result1 - expected1) < 1e-6:
        print(f"  ✅ 好>>差 时 loss = {result1:.6f}（很低 → 模型分辨力强 ✓）")
    else:
        print(f"  ❌ 期望: {expected1:.6f}，得到: {result1:.6f}")
        return False

    # 分数接近 → loss 较高
    result2 = preference_loss(reward_good=2.0, reward_bad=1.8)
    expected2 = -log_sigmoid(2.0 - 1.8)
    if abs(result2 - expected2) < 1e-6:
        print(f"  ✅ 好≈差 时 loss = {result2:.6f}（较高 → 模型难以区分）")
    else:
        print(f"  ❌ 期望: {expected2:.6f}，得到: {result2:.6f}")
        return False

    # 排序反了 → loss 很高
    result3 = preference_loss(reward_good=1.0, reward_bad=5.0)
    expected3 = -log_sigmoid(1.0 - 5.0)
    if abs(result3 - expected3) < 1e-6:
        print(f"  ✅ 好<<差 时 loss = {result3:.6f}（很高 → 排序反了 ✗）")
        print(f"     直觉：loss 越大 → 越需要调整参数让好回答得更高分")
        return True
    else:
        print(f"  ❌ 期望: {expected3:.6f}，得到: {result3:.6f}")
        return False


def test_log_ratio():
    print("\n" + "=" * 55)
    print("测试 Part 3: compute_log_ratio()")
    print("=" * 55)

    result = compute_log_ratio(-2.0, -3.0)
    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected = -2.0 - (-3.0)  # = 1.0
    if abs(result - expected) < 1e-6:
        print(f"  ✅ log_ratio = {result:.4f}（> 0：当前模型更偏好这个回答）")
    else:
        print(f"  ❌ 期望: {expected:.4f}，得到: {result:.4f}")
        return False

    result2 = compute_log_ratio(-5.0, -3.0)
    expected2 = -5.0 - (-3.0)  # = -2.0
    if abs(result2 - expected2) < 1e-6:
        print(f"  ✅ log_ratio = {result2:.4f}（< 0：当前模型更不偏好这个回答）")
    else:
        print(f"  ❌ 期望: {expected2:.4f}，得到: {result2:.4f}")
        return False

    result3 = compute_log_ratio(-3.0, -3.0)
    if abs(result3 - 0.0) < 1e-6:
        print(f"  ✅ log_ratio = {result3:.4f}（= 0：和参考模型一样）")
        print(f"     直觉：log_ratio 衡量当前模型相对于参考模型的偏好变化方向")
        return True
    else:
        print(f"  ❌ 期望: 0.0，得到: {result3}")
        return False


def test_dpo_loss():
    print("\n" + "=" * 55)
    print("测试 Part 4: dpo_loss()")
    print("=" * 55)

    # 场景1：模型已经更偏好好回答（训练成功的状态）
    result1 = dpo_loss(
        log_prob_good_current=-1.0,    # 当前模型：好回答概率高
        log_prob_good_reference=-2.0,  # 参考模型：好回答概率一般
        log_prob_bad_current=-4.0,     # 当前模型：差回答概率低
        log_prob_bad_reference=-2.0,   # 参考模型：差回答概率一般
        beta=0.1,
    )

    if result1 is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    # 手动计算期望值
    log_ratio_good = -1.0 - (-2.0)  # = 1.0
    log_ratio_bad = -4.0 - (-2.0)   # = -2.0
    scaled_diff = 0.1 * (1.0 - (-2.0))  # = 0.1 * 3.0 = 0.3
    expected1 = -log_sigmoid(scaled_diff)

    if abs(result1 - expected1) < 1e-6:
        print(f"  ✅ 模型偏好正确时 loss = {result1:.6f}（较低）")
    else:
        print(f"  ❌ 期望: {expected1:.6f}，得到: {result1:.6f}")
        return False

    # 场景2：模型偏好反了（需要更多训练）
    result2 = dpo_loss(
        log_prob_good_current=-4.0,    # 当前模型：好回答概率低
        log_prob_good_reference=-2.0,
        log_prob_bad_current=-1.0,     # 当前模型：差回答概率高
        log_prob_bad_reference=-2.0,
        beta=0.1,
    )

    log_ratio_good2 = -4.0 - (-2.0)  # = -2.0
    log_ratio_bad2 = -1.0 - (-2.0)   # = 1.0
    scaled_diff2 = 0.1 * (-2.0 - 1.0)  # = -0.3
    expected2 = -log_sigmoid(scaled_diff2)

    if abs(result2 - expected2) < 1e-6:
        print(f"  ✅ 模型偏好反转时 loss = {result2:.6f}（较高）")
        print(f"     正确偏好 loss={result1:.4f} < 反转偏好 loss={result2:.4f} ✓")
        return True
    else:
        print(f"  ❌ 期望: {expected2:.6f}，得到: {result2:.6f}")
        return False


def test_alignment_training():
    print("\n" + "=" * 55)
    print("测试 Part 5: alignment_training()")
    print("=" * 55)

    # 4 个选项，人类偏好排序：选项2 > 选项0 > 选项3 > 选项1
    initial_scores = [0.0, 0.0, 0.0, 0.0]
    preference_pairs = [
        (2, 0),  # 选项2 优于 选项0
        (2, 1),  # 选项2 优于 选项1
        (2, 3),  # 选项2 优于 选项3
        (0, 1),  # 选项0 优于 选项1
        (0, 3),  # 选项0 优于 选项3
        (3, 1),  # 选项3 优于 选项1
    ]

    result = alignment_training(
        initial_scores, preference_pairs,
        learning_rate=0.5, n_epochs=10, beta=0.1,
    )

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    required_keys = ['final_scores', 'loss_history', 'score_history']
    for key in required_keys:
        if key not in result:
            print(f"  ❌ 返回的字典缺少 '{key}' 键")
            return False

    final = result['final_scores']
    history = result['loss_history']

    print(f"  📊 训练结果：")
    print(f"     初始分数：{initial_scores}")
    print(f"     训练后分数：[{', '.join(f'{s:.3f}' for s in final)}]")

    # 检查排序是否正确
    # 期望：final[2] > final[0] > final[3] > final[1]
    correct_order = final[2] > final[0] > final[3] > final[1]

    if correct_order:
        print(f"  ✅ 排序正确！")
        print(f"     选项2({final[2]:.3f}) > 选项0({final[0]:.3f}) > 选项3({final[3]:.3f}) > 选项1({final[1]:.3f})")
    else:
        print(f"  ⚠️  排序未完全正确，但如果 loss 在下降，说明方向是对的")
        sorted_indices = sorted(range(4), key=lambda i: final[i], reverse=True)
        print(f"     实际排序：{sorted_indices}（期望 [2, 0, 3, 1]）")

    # 检查 loss 是否下降
    if len(history) > 0:
        first_avg = sum(history[:6]) / 6
        last_avg = sum(history[-6:]) / 6
        if last_avg < first_avg:
            print(f"  ✅ Loss 下降了！（前6步平均: {first_avg:.4f} → 后6步平均: {last_avg:.4f}）")
        else:
            print(f"  ⚠️  Loss 没有明显下降（前: {first_avg:.4f}, 后: {last_avg:.4f}）")
    else:
        print(f"  ❌ loss_history 为空")
        return False

    # 可视化训练过程
    total_steps = len(history)
    print(f"\n  📉 Loss 变化（共 {total_steps} 步训练）：")
    show_steps = min(total_steps, 60)
    step_interval = max(1, total_steps // 8)
    for i in range(0, show_steps, step_interval):
        bar_len = int(min(history[i], 1.0) * 30)
        bar = '█' * bar_len + '░' * (30 - bar_len)
        print(f"     Step {i:3d} | {bar} | {history[i]:.4f}")

    if correct_order:
        print(f"\n  🎓 模型成功学会了人类的偏好排序！")
        print(f"     这就是 DPO 的核心：通过偏好对，让模型的'品味'和人类对齐")
        return True
    else:
        return len(history) > 0 and last_avg < first_avg


if __name__ == "__main__":
    print()
    print("🎓 第五课练习：实现对齐算法（RLHF / DPO）")
    print("=" * 55)
    print()

    all_passed = True
    all_passed = test_compute_reward() and all_passed
    all_passed = test_preference_loss() and all_passed
    all_passed = test_log_ratio() and all_passed
    all_passed = test_dpo_loss() and all_passed
    all_passed = test_alignment_training() and all_passed

    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 全部通过！你已经完整实现了对齐的核心算法！")
        print("   你刚刚亲手实现了：")
        print("   奖励函数 → 偏好损失 → 对数比率 → DPO 损失 → 对齐训练")
        print()
        print("   这就是 ChatGPT、Claude 等模型从'能说话'到'说好话'的秘密。")
        print("   真实的对齐还需要：海量高质量的偏好数据、更复杂的优化策略、")
        print("   以及大量的 Red Teaming（安全测试）。但核心数学原理就是你刚写的这些。")
        print()
        print("   🎓 恭喜完成全部五节课的学习！")
        print("   你现在对大模型从头到尾的工作原理有了完整的理解：")
        print("   文字→数字 → 向量→预测 → Attention → 训练 → 对齐")
    else:
        print("💪 还有测试没通过，继续加油！")
        print("   提示：按照 TODO 的顺序逐个实现，每完成一个就运行一次检查")
    print("=" * 55)
    print()
