"""
============================================================
第四课练习：手写训练循环
============================================================

训练是让模型从"一无所知"变成"聪明绝顶"的过程。
它的核心极其简单：前向传播 → 算损失 → 算梯度 → 更新参数 → 重复。

在这个练习中，你将亲手实现训练的核心组件：
  交叉熵损失 → 数值梯度 → 解析梯度 → 参数更新 → 完整训练循环

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过 ✅

难度：⭐⭐⭐ (涉及一些微积分直觉，但每步都有详细提示)
预计用时：30-45 分钟
"""

import math
import random

random.seed(42)


# ============================================================
# 辅助函数（已实现，不需要修改）
# ============================================================

def softmax(logits: list[float]) -> list[float]:
    """将 logits 转化为概率分布（带数值稳定处理）。"""
    max_val = max(logits)
    exp_vals = [math.exp(x - max_val) for x in logits]
    sum_exp = sum(exp_vals)
    return [v / sum_exp for v in exp_vals]


def make_random_vector(size: int) -> list[float]:
    """生成一个随机向量，值在 [-0.5, 0.5] 之间。"""
    return [random.uniform(-0.5, 0.5) for _ in range(size)]


def make_random_matrix(rows: int, cols: int) -> list[float]:
    """生成一个 rows × cols 的随机矩阵，值在 [-0.5, 0.5] 之间。"""
    return [[random.uniform(-0.5, 0.5) for _ in range(cols)] for _ in range(rows)]


def mat_vec_mul(matrix: list[list[float]], vec: list[float]) -> list[float]:
    """矩阵乘向量：matrix (m×n) × vec (n,) → result (m,)。"""
    return [sum(row[j] * vec[j] for j in range(len(vec))) for row in matrix]


# ============================================================
# 🧱 Part 1: 交叉熵损失 (Cross-Entropy Loss)
# ============================================================
#
# 交叉熵损失衡量模型预测的概率分布和真实答案之间的"差距"。
# 公式：loss = -log(probs[target])
#
# - probs: 模型预测的概率分布（Softmax 的输出），长度 = 词表大小
# - target: 正确答案的 ID（一个整数）
#
# 性质：
#   - probs[target] 越接近 1 → loss 越接近 0（预测好）
#   - probs[target] 越接近 0 → loss 越大（预测差）
#

def cross_entropy_loss(probs: list[float], target: int) -> float:
    """计算交叉熵损失。

    Args:
        probs: 概率分布，长度为词表大小，每个值在 (0, 1) 之间，总和为 1
        target: 正确答案的 ID（索引）

    Returns:
        损失值 = -log(probs[target])
    """
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：
    #   1. 取出 probs 中 target 位置的值
    #   2. 对它取 log（用 math.log）
    #   3. 取负号
    #   4. 返回结果
    #
    # 就一行代码！

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 1 ========


# ============================================================
# 📐 Part 2: 数值梯度 (Numerical Gradient)
# ============================================================
#
# 梯度的定义：参数微小变化时，损失的变化率。
# 数值梯度用最朴素的方法来近似：
#   gradient ≈ (loss(w + ε) - loss(w - ε)) / (2ε)
#
# 这是理解梯度概念最直观的方式：
# "把参数拨动一点点，看 Loss 变了多少"
#

def compute_gradient_numerical(
    logits: list[float], target: int, param_index: int, epsilon: float = 1e-5
) -> float:
    """用数值差分法计算 logits[param_index] 的梯度。

    Args:
        logits: 模型的原始输出（Softmax 之前的值）
        target: 正确答案的 ID
        param_index: 要计算梯度的参数位置
        epsilon: 微小扰动量

    Returns:
        该参数的近似梯度
    """
    # ======== TODO 2: 在这里写你的代码 ========
    # 提示：
    #   1. 复制 logits 列表为 logits_plus，将 logits_plus[param_index] 加上 epsilon
    #   2. 复制 logits 列表为 logits_minus，将 logits_minus[param_index] 减去 epsilon
    #   3. 分别对 logits_plus 和 logits_minus 做 softmax，得到两个概率分布
    #   4. 分别算两个概率分布对 target 的交叉熵损失
    #   5. 梯度 ≈ (loss_plus - loss_minus) / (2 * epsilon)
    #   6. 返回梯度
    #
    # 注意：复制列表用 logits.copy() 或 logits[:]

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 2 ========


# ============================================================
# 🎯 Part 3: 解析梯度 (Analytical Gradient)
# ============================================================
#
# 数值梯度虽然直观，但太慢了（每个参数都要算两次前向）。
# 好消息是 Softmax + Cross-Entropy 的梯度有一个极其简洁的公式：
#
#   ∂loss/∂logits[i] = probs[i]          (如果 i ≠ target)
#   ∂loss/∂logits[i] = probs[i] - 1      (如果 i == target)
#
# 也就是说：梯度 = 预测概率 - 真实标签（one-hot）
# 这个公式简洁到不可思议，但它包含了 Softmax 和 log 的全部微积分。
#

def compute_softmax_gradient(logits: list[float], target: int) -> list[float]:
    """计算 Softmax + Cross-Entropy 对 logits 的解析梯度。

    Args:
        logits: 模型的原始输出
        target: 正确答案的 ID

    Returns:
        梯度向量，长度与 logits 相同
    """
    # ======== TODO 3: 在这里写你的代码 ========
    # 提示：
    #   1. 对 logits 做 softmax 得到 probs
    #   2. 创建一个和 probs 一样长的梯度列表
    #   3. 对于每个位置 i：
    #      - 如果 i == target：gradient[i] = probs[i] - 1
    #      - 如果 i != target：gradient[i] = probs[i]
    #   4. 返回梯度列表
    #
    # 你也可以用更简洁的写法：
    #   先让 gradient = probs 的副本，然后 gradient[target] -= 1

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 3 ========


# ============================================================
# 🔧 Part 4: 参数更新 (Parameter Update)
# ============================================================
#
# 梯度下降的核心公式：
#   参数_new = 参数_old - learning_rate × 梯度
#
# 每个参数都朝着让 Loss 减小的方向移动一小步。
#

def update_parameters(
    params: list[float], gradients: list[float], learning_rate: float
) -> list[float]:
    """执行一步梯度下降，返回更新后的参数。

    Args:
        params: 当前参数值列表
        gradients: 对应的梯度列表（和 params 等长）
        learning_rate: 学习率（步长）

    Returns:
        更新后的参数列表（新列表，不修改原始 params）
    """
    # ======== TODO 4: 在这里写你的代码 ========
    # 提示：
    #   对于每个位置 i：
    #     new_params[i] = params[i] - learning_rate * gradients[i]
    #   返回 new_params
    #
    # 一行列表推导就够了！

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 4 ========


# ============================================================
# 🚀 Part 5: 完整的训练循环 (Training Loop)
# ============================================================
#
# 把所有组件串起来！
# 我们训练一个最简单的模型：一组 logits 参数，通过反复训练
# 让它学会对 target 位置输出高概率。
#
# 训练循环：
#   1. 前向传播：logits → softmax → probs
#   2. 计算损失：cross_entropy_loss(probs, target)
#   3. 计算梯度：compute_softmax_gradient(logits, target)
#   4. 更新参数：logits = update_parameters(logits, gradient, lr)
#   5. 重复 n_steps 次
#

def training_loop(
    initial_logits: list[float],
    target: int,
    learning_rate: float = 1.0,
    n_steps: int = 50,
) -> dict:
    """执行完整的训练循环。

    Args:
        initial_logits: 初始参数（logits 向量）
        target: 要学习预测的目标 ID
        learning_rate: 学习率
        n_steps: 训练步数

    Returns:
        包含训练结果的字典：
        {
            'final_logits': 训练后的 logits,
            'final_probs': 训练后的概率分布,
            'final_loss': 最终损失,
            'loss_history': 每步的损失列表,
        }
    """
    # ======== TODO 5: 在这里写你的代码 ========
    # 提示（按步骤来）：
    #   1. 复制 initial_logits 到一个变量 logits（不要修改原始输入）
    #   2. 创建一个空列表 loss_history 来记录每步的损失
    #   3. 循环 n_steps 次：
    #      a. 对 logits 做 softmax 得到 probs
    #      b. 用 cross_entropy_loss(probs, target) 算损失
    #      c. 把损失追加到 loss_history
    #      d. 用 compute_softmax_gradient(logits, target) 算梯度
    #      e. 用 update_parameters(logits, gradient, learning_rate) 更新 logits
    #   4. 训练结束后，再做一次 softmax 得到最终的 probs
    #   5. 算最终的 loss
    #   6. 返回字典（格式见上面的 Returns 说明）

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 5 ========


# ============================================================
# 🧪 测试 — 运行 python exercise.py 来检查你的实现
# ============================================================

def test_cross_entropy_loss():
    print("=" * 55)
    print("测试 Part 1: cross_entropy_loss()")
    print("=" * 55)

    probs = [0.1, 0.7, 0.2]
    target = 1

    result = cross_entropy_loss(probs, target)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected = -math.log(0.7)

    if abs(result - expected) < 1e-6:
        print(f"  ✅ 通过！loss = -log(0.7) = {result:.6f}")
    else:
        print(f"  ❌ 期望: {expected:.6f}，得到: {result:.6f}")
        return False

    # 测试极端情况
    probs2 = [0.01, 0.01, 0.96, 0.01, 0.01]
    result2 = cross_entropy_loss(probs2, 2)
    expected2 = -math.log(0.96)

    if abs(result2 - expected2) < 1e-6:
        print(f"  ✅ 高置信度预测：loss = -log(0.96) = {result2:.6f}（很低 ✓）")
    else:
        print(f"  ❌ 期望: {expected2:.6f}，得到: {result2:.6f}")
        return False

    result3 = cross_entropy_loss(probs2, 0)
    expected3 = -math.log(0.01)
    if abs(result3 - expected3) < 1e-6:
        print(f"  ✅ 低置信度预测：loss = -log(0.01) = {result3:.6f}（很高 ✗）")
        return True
    else:
        print(f"  ❌ 期望: {expected3:.6f}，得到: {result3:.6f}")
        return False


def test_numerical_gradient():
    print("\n" + "=" * 55)
    print("测试 Part 2: compute_gradient_numerical()")
    print("=" * 55)

    logits = [1.0, 2.0, 0.5]
    target = 1

    result = compute_gradient_numerical(logits, target, param_index=0)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    # 用解析梯度验证
    probs = softmax(logits)
    expected_grad_0 = probs[0]  # 非 target 位置
    expected_grad_1 = probs[1] - 1  # target 位置

    if abs(result - expected_grad_0) < 1e-4:
        print(f"  ✅ logits[0] 的梯度 = {result:.6f}（接近解析值 {expected_grad_0:.6f}）")
    else:
        print(f"  ❌ logits[0] 梯度：期望 ≈{expected_grad_0:.6f}，得到 {result:.6f}")
        return False

    result1 = compute_gradient_numerical(logits, target, param_index=1)
    if abs(result1 - expected_grad_1) < 1e-4:
        print(f"  ✅ logits[1]（target）的梯度 = {result1:.6f}（接近解析值 {expected_grad_1:.6f}）")
    else:
        print(f"  ❌ logits[1] 梯度：期望 ≈{expected_grad_1:.6f}，得到 {result1:.6f}")
        return False

    result2 = compute_gradient_numerical(logits, target, param_index=2)
    expected_grad_2 = probs[2]
    if abs(result2 - expected_grad_2) < 1e-4:
        print(f"  ✅ logits[2] 的梯度 = {result2:.6f}（接近解析值 {expected_grad_2:.6f}）")
        print(f"     直觉：非 target 位置梯度为正（降低它的概率）")
        print(f"           target 位置梯度为负（提高它的概率）")
        return True
    else:
        print(f"  ❌ logits[2] 梯度：期望 ≈{expected_grad_2:.6f}，得到 {result2:.6f}")
        return False


def test_softmax_gradient():
    print("\n" + "=" * 55)
    print("测试 Part 3: compute_softmax_gradient()")
    print("=" * 55)

    logits = [1.0, 2.0, 0.5, -1.0]
    target = 2

    result = compute_softmax_gradient(logits, target)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if len(result) != len(logits):
        print(f"  ❌ 梯度长度应为 {len(logits)}，得到 {len(result)}")
        return False

    probs = softmax(logits)
    expected = [p for p in probs]
    expected[target] -= 1

    ok = True
    for i in range(len(logits)):
        if abs(result[i] - expected[i]) > 1e-6:
            ok = False
            break

    if ok:
        print(f"  ✅ 梯度计算正确！")
        print(f"     probs   = [{', '.join(f'{p:.4f}' for p in probs)}]")
        print(f"     gradient = [{', '.join(f'{g:.4f}' for g in result)}]")
        print(f"     target 位置(idx={target}) 梯度 = probs[{target}] - 1 = {result[target]:.4f}")
        print(f"     其他位置梯度 = probs[i]（正值→推低这些位置的概率）")
    else:
        print(f"  ❌ 梯度不正确")
        print(f"     期望: {expected}")
        print(f"     得到: {result}")
        return False

    # 验证和数值梯度一致
    for i in range(len(logits)):
        num_grad = compute_gradient_numerical(logits, target, i)
        if abs(num_grad - result[i]) > 1e-4:
            print(f"  ❌ 解析梯度和数值梯度不一致（位置 {i}）")
            return False
    print(f"  ✅ 解析梯度和数值梯度完全吻合 ✓（验证了公式的正确性）")
    return True


def test_update_parameters():
    print("\n" + "=" * 55)
    print("测试 Part 4: update_parameters()")
    print("=" * 55)

    params = [1.0, 2.0, 3.0]
    gradients = [0.5, -0.3, 0.1]
    lr = 0.1

    result = update_parameters(params, gradients, lr)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected = [
        1.0 - 0.1 * 0.5,   # 0.95
        2.0 - 0.1 * (-0.3),  # 2.03
        3.0 - 0.1 * 0.1,   # 2.99
    ]

    ok = all(abs(result[i] - expected[i]) < 1e-6 for i in range(3))

    if ok:
        print(f"  ✅ 参数更新正确！")
        print(f"     params  = {params}")
        print(f"     grads   = {gradients}")
        print(f"     lr      = {lr}")
        print(f"     更新后  = {result}")
        print(f"     梯度为正 → 参数减小（1.0 → {result[0]}）")
        print(f"     梯度为负 → 参数增大（2.0 → {result[1]}）")
    else:
        print(f"  ❌ 更新结果不正确")
        print(f"     期望: {expected}")
        print(f"     得到: {result}")
        return False

    # 验证不修改原始参数
    if params == [1.0, 2.0, 3.0]:
        print(f"  ✅ 原始参数未被修改 ✓")
        return True
    else:
        print(f"  ❌ 原始参数被修改了！请返回新列表而不是修改原列表")
        return False


def test_training_loop():
    print("\n" + "=" * 55)
    print("测试 Part 5: training_loop()")
    print("=" * 55)

    vocab_size = 5
    target = 3
    initial_logits = [0.0] * vocab_size  # 从均匀分布开始

    result = training_loop(initial_logits, target, learning_rate=1.0, n_steps=50)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    required_keys = ['final_logits', 'final_probs', 'final_loss', 'loss_history']
    for key in required_keys:
        if key not in result:
            print(f"  ❌ 返回的字典缺少 '{key}' 键")
            return False

    # 检查 loss 是否下降
    history = result['loss_history']
    if len(history) != 50:
        print(f"  ❌ loss_history 长度应为 50，得到 {len(history)}")
        return False

    first_loss = history[0]
    last_loss = history[-1]

    print(f"  📈 训练过程：")
    print(f"     初始 Loss = {first_loss:.4f}（≈ -log(1/{vocab_size}) = {-math.log(1/vocab_size):.4f}，接近随机猜测）")
    print(f"     最终 Loss = {last_loss:.4f}")

    if last_loss >= first_loss:
        print(f"  ❌ 训练后 Loss 没有下降！检查你的训练循环逻辑")
        return False

    print(f"  ✅ Loss 下降了 {first_loss - last_loss:.4f}（{(1 - last_loss/first_loss)*100:.1f}% ↓）")

    # 检查最终概率
    final_probs = result['final_probs']
    if final_probs[target] < 0.8:
        print(f"  ⚠️  训练后 target 概率 = {final_probs[target]:.4f}，可能训练步数不够或学习率太小")
        print(f"     但如果 Loss 确实在下降，说明方向是对的！")
    else:
        print(f"  ✅ 训练后 target(idx={target}) 概率 = {final_probs[target]:.4f}（>0.8 ✓）")

    # 检查 loss 单调递减（大趋势）
    decreasing = sum(1 for i in range(1, len(history)) if history[i] <= history[i-1] + 1e-10)
    if decreasing >= len(history) * 0.8:
        print(f"  ✅ Loss 曲线基本单调递减（{decreasing}/{len(history)-1} 步在下降）")
    else:
        print(f"  ⚠️  Loss 曲线不够平滑（只有 {decreasing}/{len(history)-1} 步在下降）")

    # 可视化 loss 曲线
    print(f"\n  📉 Loss 下降曲线（50 步训练）：")
    chart_width = 40
    max_loss = max(history)
    min_loss = min(history)
    loss_range = max_loss - min_loss if max_loss > min_loss else 1

    for i in range(0, 50, 5):
        bar_len = int((history[i] - min_loss) / loss_range * chart_width)
        bar = '█' * bar_len + '░' * (chart_width - bar_len)
        print(f"     Step {i:2d} | {bar} | {history[i]:.4f}")

    print(f"\n  🎓 从随机猜测 (Loss≈{first_loss:.2f}) 训练到几乎确定 (Loss≈{last_loss:.2f})")
    print(f"     模型学会了：给 target={target} 高概率，给其他位置低概率")

    return True


if __name__ == "__main__":
    print()
    print("🎓 第四课练习：手写训练循环")
    print("=" * 55)
    print()

    all_passed = True
    all_passed = test_cross_entropy_loss() and all_passed
    all_passed = test_numerical_gradient() and all_passed
    all_passed = test_softmax_gradient() and all_passed
    all_passed = test_update_parameters() and all_passed
    all_passed = test_training_loop() and all_passed

    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 全部通过！你已经完整实现了一个训练循环！")
        print("   你刚刚亲手实现了：")
        print("   交叉熵损失 → 数值梯度 → 解析梯度 → 参数更新 → 训练循环")
        print()
        print("   这就是 GPT、Claude、LLaMA 等大模型训练的核心逻辑。")
        print("   真实的训练只是在此基础上加了：更大的模型、更多的数据、")
        print("   更好的优化器、以及上千块 GPU 的并行。但核心循环一模一样。")
    else:
        print("💪 还有测试没通过，继续加油！")
        print("   提示：按照 TODO 的顺序逐个实现，每完成一个就运行一次检查")
    print("=" * 55)
    print()
