"""
============================================================
第七课练习：实现 LoRA 微调
============================================================

LoRA 是当前最流行的参数高效微调方法：
不修改原始权重 W，而是在旁边加一对低秩矩阵 B×A 来学习新能力。
output = Wx + BAx，其中 W 冻结，只训练 A 和 B。

在这个练习中，你将亲手实现 LoRA 的核心机制：
  前向传播 → 参数统计 → 梯度计算 → 训练步 → 完整微调循环

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过 ✅

难度：⭐⭐⭐ (涉及矩阵运算，但公式都有详细提示)
预计用时：30-45 分钟
"""

import math
import random

random.seed(42)


# ============================================================
# 辅助函数（已实现，不需要修改）
# ============================================================

def make_random_matrix(rows: int, cols: int, scale: float = 0.5) -> list[list[float]]:
    """生成随机矩阵。"""
    return [[random.uniform(-scale, scale) for _ in range(cols)] for _ in range(rows)]


def make_zero_matrix(rows: int, cols: int) -> list[list[float]]:
    """生成全零矩阵。"""
    return [[0.0] * cols for _ in range(rows)]


def mat_mul(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    """矩阵乘法：A (m×n) × B (n×p) → (m×p)。"""
    m, n, p = len(A), len(B), len(B[0])
    result = [[0.0] * p for _ in range(m)]
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    return result


def mat_vec_mul(matrix: list[list[float]], vec: list[float]) -> list[float]:
    """矩阵乘向量。"""
    return [sum(row[j] * vec[j] for j in range(len(vec))) for row in matrix]


def vec_outer_product(a: list[float], b: list[float]) -> list[list[float]]:
    """向量外积：a (m,) × b (n,) → (m×n) 矩阵。"""
    return [[a[i] * b[j] for j in range(len(b))] for i in range(len(a))]


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    """矩阵转置。"""
    rows, cols = len(matrix), len(matrix[0])
    return [[matrix[i][j] for i in range(rows)] for j in range(cols)]


def mse_loss(predicted: list[float], target: list[float]) -> float:
    """均方误差损失。"""
    n = len(predicted)
    return sum((predicted[i] - target[i]) ** 2 for i in range(n)) / n


def mse_loss_gradient(predicted: list[float], target: list[float]) -> list[float]:
    """MSE 损失对 predicted 的梯度：2/n * (predicted - target)。"""
    n = len(predicted)
    return [2.0 / n * (predicted[i] - target[i]) for i in range(n)]


# ============================================================
# 🧱 Part 1: LoRA 前向传播
# ============================================================
#
# LoRA 的前向传播公式：
#   output = W × x + (B × A) × x
#
# 其中：
#   W: 原始权重矩阵 (d_out × d_in)，冻结不动
#   A: 降维矩阵 (rank × d_in)，可训练
#   B: 升维矩阵 (d_out × rank)，可训练
#   x: 输入向量 (d_in,)
#
# 计算顺序（省计算）：
#   先算 A×x 得到低维向量 (rank,)
#   再算 B×(Ax) 得到输出修正 (d_out,)
#   最后加到 W×x 上
#

def lora_forward(
    W: list[list[float]],
    A: list[list[float]],
    B: list[list[float]],
    x: list[float],
    scaling: float = 1.0,
) -> list[float]:
    """LoRA 前向传播。

    Args:
        W: 原始权重矩阵 (d_out × d_in)
        A: LoRA 降维矩阵 (rank × d_in)
        B: LoRA 升维矩阵 (d_out × rank)
        x: 输入向量 (d_in,)
        scaling: LoRA 缩放因子（alpha / rank）

    Returns:
        输出向量 (d_out,) = Wx + scaling * B(Ax)
    """
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：
    #   1. 计算原始输出：base_output = mat_vec_mul(W, x)
    #   2. 计算 LoRA 中间结果：Ax = mat_vec_mul(A, x)  → 形状 (rank,)
    #   3. 计算 LoRA 输出：BAx = mat_vec_mul(B, Ax)  → 形状 (d_out,)
    #   4. 合并：output[i] = base_output[i] + scaling * BAx[i]
    #   5. 返回 output

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 1 ========


# ============================================================
# 📊 Part 2: 参数量对比
# ============================================================
#
# LoRA 的核心优势是参数效率。这里我们具体计算对比。
#

def count_parameters(d_in: int, d_out: int, rank: int) -> dict:
    """统计原始矩阵和 LoRA 适配器的参数量。

    Args:
        d_in: 输入维度
        d_out: 输出维度
        rank: LoRA 的秩

    Returns:
        {
            'original_params': 原始矩阵 W 的参数数量,
            'lora_params': LoRA (A+B) 的参数数量,
            'ratio': LoRA 参数占原始参数的比例,
            'savings': 参数节省百分比,
        }
    """
    # ======== TODO 2: 在这里写你的代码 ========
    # 提示：
    #   - 原始矩阵 W 的参数量 = d_out × d_in
    #   - A 矩阵的参数量 = rank × d_in
    #   - B 矩阵的参数量 = d_out × rank
    #   - LoRA 总参数量 = A + B
    #   - ratio = lora_params / original_params
    #   - savings = (1 - ratio) × 100（百分比）

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 2 ========


# ============================================================
# 📐 Part 3: LoRA 梯度计算
# ============================================================
#
# 在 LoRA 训练中，只有 A 和 B 的梯度需要计算，W 完全冻结。
#
# 给定损失对输出的梯度 grad_output (d_out,)：
#
#   ∂L/∂B = grad_output × (Ax)^T   → 形状 (d_out × rank)
#   ∂L/∂A = B^T × grad_output × x^T  → 简化为按行计算
#
# 这里我们用简化版本：直接对整个 BA 的输出做梯度
#

def lora_gradient(
    grad_output: list[float],
    A: list[list[float]],
    B: list[list[float]],
    x: list[float],
    scaling: float = 1.0,
) -> dict:
    """计算 LoRA 参数 A 和 B 的梯度。

    Args:
        grad_output: 损失对最终输出的梯度 (d_out,)
        A: 当前的 A 矩阵 (rank × d_in)
        B: 当前的 B 矩阵 (d_out × rank)
        x: 输入向量 (d_in,)
        scaling: LoRA 缩放因子

    Returns:
        {
            'grad_B': B 的梯度 (d_out × rank),
            'grad_A': A 的梯度 (rank × d_in),
        }
    """
    # ======== TODO 3: 在这里写你的代码 ========
    # 提示：
    #   1. 计算 Ax = mat_vec_mul(A, x)  → (rank,)
    #   2. 缩放梯度：scaled_grad = [g * scaling for g in grad_output]
    #   3. 计算 grad_B = scaled_grad 和 Ax 的外积：
    #      grad_B = vec_outer_product(scaled_grad, Ax)  → (d_out × rank)
    #   4. 计算 B^T × scaled_grad → (rank,)
    #      BT_grad = mat_vec_mul(transpose(B), scaled_grad)
    #   5. 计算 grad_A = BT_grad 和 x 的外积：
    #      grad_A = vec_outer_product(BT_grad, x)  → (rank × d_in)
    #      再乘以 scaling
    #   6. 返回字典

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 3 ========


# ============================================================
# 🔧 Part 4: 一步 LoRA 训练
# ============================================================
#
# 把前向、损失、梯度、更新串起来完成一步训练。
# 注意：只更新 A 和 B，W 保持不变！
#

def lora_training_step(
    W: list[list[float]],
    A: list[list[float]],
    B: list[list[float]],
    x: list[float],
    target: list[float],
    learning_rate: float = 0.01,
    scaling: float = 1.0,
) -> dict:
    """执行一步 LoRA 训练。

    Args:
        W: 原始权重（冻结）
        A, B: LoRA 参数（将被更新）
        x: 输入向量
        target: 目标输出向量
        learning_rate: 学习率
        scaling: LoRA 缩放因子

    Returns:
        {
            'new_A': 更新后的 A 矩阵,
            'new_B': 更新后的 B 矩阵,
            'loss': 本步的损失值,
            'output': 本步的模型输出,
        }
    """
    # ======== TODO 4: 在这里写你的代码 ========
    # 提示：
    #   1. 前向传播：output = lora_forward(W, A, B, x, scaling)
    #   2. 计算损失：loss = mse_loss(output, target)
    #   3. 计算损失对输出的梯度：grad_output = mse_loss_gradient(output, target)
    #   4. 计算 LoRA 梯度：grads = lora_gradient(grad_output, A, B, x, scaling)
    #   5. 更新 A：new_A[i][j] = A[i][j] - learning_rate * grads['grad_A'][i][j]
    #   6. 更新 B：new_B[i][j] = B[i][j] - learning_rate * grads['grad_B'][i][j]
    #   7. 返回字典

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 4 ========


# ============================================================
# 🚀 Part 5: 完整的 LoRA 微调循环
# ============================================================
#
# 在一组训练数据上反复训练 LoRA，观察模型如何学会新的映射。
#

def lora_finetune(
    W: list[list[float]],
    train_data: list[tuple[list[float], list[float]]],
    rank: int = 4,
    learning_rate: float = 0.05,
    n_epochs: int = 20,
    scaling: float = 1.0,
) -> dict:
    """完整的 LoRA 微调循环。

    Args:
        W: 原始权重矩阵 (d_out × d_in)，冻结不变
        train_data: 训练数据列表，每项是 (input, target) 对
        rank: LoRA 的秩
        learning_rate: 学习率
        n_epochs: 训练轮数
        scaling: LoRA 缩放因子

    Returns:
        {
            'final_A': 训练后的 A 矩阵,
            'final_B': 训练后的 B 矩阵,
            'loss_history': 每步的损失列表,
            'initial_loss': 训练前第一步的损失,
            'final_loss': 训练后最后一步的损失,
        }
    """
    # ======== TODO 5: 在这里写你的代码 ========
    # 提示：
    #   1. 获取维度：d_out = len(W), d_in = len(W[0])
    #   2. 初始化 LoRA 参数：
    #      - A = make_random_matrix(rank, d_in, scale=0.01)  （小随机初始化）
    #      - B = make_zero_matrix(d_out, rank)  （零初始化，确保初始时 LoRA 输出为 0）
    #   3. 创建 loss_history 列表
    #   4. 对于每个 epoch：
    #      对于每个 (x, target) in train_data：
    #        result = lora_training_step(W, A, B, x, target, learning_rate, scaling)
    #        A = result['new_A']
    #        B = result['new_B']
    #        loss_history.append(result['loss'])
    #   5. 返回字典

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 5 ========


# ============================================================
# 🧪 测试 — 运行 python exercise.py 来检查你的实现
# ============================================================

def test_lora_forward():
    print("=" * 55)
    print("测试 Part 1: lora_forward()")
    print("=" * 55)

    d_in, d_out, rank = 4, 3, 2
    W = [[1.0, 0.0, 0.0, 0.0],
         [0.0, 1.0, 0.0, 0.0],
         [0.0, 0.0, 1.0, 0.0]]

    A = [[1.0, 0.0, 0.0, 0.0],
         [0.0, 1.0, 0.0, 0.0]]

    B = [[0.1, 0.0],
         [0.0, 0.1],
         [0.1, 0.1]]

    x = [1.0, 2.0, 3.0, 4.0]

    result = lora_forward(W, A, B, x, scaling=1.0)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    # Wx = [1, 2, 3]
    # Ax = [1, 2]
    # BAx = [0.1*1, 0.1*2, 0.1*1+0.1*2] = [0.1, 0.2, 0.3]
    # output = [1.1, 2.2, 3.3]
    expected = [1.1, 2.2, 3.3]

    if all(abs(result[i] - expected[i]) < 1e-6 for i in range(3)):
        print(f"  ✅ LoRA 前向传播正确！")
        print(f"     Wx   = [1.0, 2.0, 3.0]（原始输出）")
        print(f"     BAx  = [0.1, 0.2, 0.3]（LoRA 适配）")
        print(f"     总输出 = {result}（原始 + LoRA）")
    else:
        print(f"  ❌ 输出不正确")
        print(f"     期望: {expected}")
        print(f"     得到: {result}")
        return False

    # 测试 scaling
    result_scaled = lora_forward(W, A, B, x, scaling=2.0)
    expected_scaled = [1.2, 2.4, 3.6]
    if all(abs(result_scaled[i] - expected_scaled[i]) < 1e-6 for i in range(3)):
        print(f"  ✅ scaling=2.0 时输出正确: {result_scaled}")
        return True
    else:
        print(f"  ❌ scaling=2.0 时输出不正确，期望 {expected_scaled}，得到 {result_scaled}")
        return False


def test_count_parameters():
    print("\n" + "=" * 55)
    print("测试 Part 2: count_parameters()")
    print("=" * 55)

    result = count_parameters(d_in=4096, d_out=4096, rank=16)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    expected_orig = 4096 * 4096  # 16,777,216
    expected_lora = 16 * 4096 + 4096 * 16  # 131,072
    expected_ratio = expected_lora / expected_orig

    if result['original_params'] != expected_orig:
        print(f"  ❌ 原始参数量：期望 {expected_orig:,}，得到 {result['original_params']:,}")
        return False

    if result['lora_params'] != expected_lora:
        print(f"  ❌ LoRA 参数量：期望 {expected_lora:,}，得到 {result['lora_params']:,}")
        return False

    print(f"  ✅ 原始矩阵 W: {result['original_params']:,} 参数")
    print(f"  ✅ LoRA (A+B):  {result['lora_params']:,} 参数")
    print(f"  ✅ 比例: {result['ratio']:.4f} ({result['ratio']*100:.2f}%)")
    print(f"  ✅ 节省: {result['savings']:.2f}%")
    print(f"     → LoRA 只用了原始参数量的 {result['ratio']*100:.2f}%！")
    return True


def test_lora_gradient():
    print("\n" + "=" * 55)
    print("测试 Part 3: lora_gradient()")
    print("=" * 55)

    d_in, d_out, rank = 3, 2, 2
    A = [[1.0, 0.0, 0.0],
         [0.0, 1.0, 0.0]]
    B = [[0.5, 0.0],
         [0.0, 0.5]]
    x = [1.0, 2.0, 3.0]
    grad_output = [1.0, -1.0]

    result = lora_gradient(grad_output, A, B, x, scaling=1.0)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if 'grad_B' not in result or 'grad_A' not in result:
        print("  ❌ 返回字典缺少 'grad_B' 或 'grad_A'")
        return False

    # Ax = [1, 2]
    # grad_B = outer(grad_output, Ax) = [[1*1, 1*2], [-1*1, -1*2]] = [[1,2],[-1,-2]]
    expected_grad_B = [[1.0, 2.0], [-1.0, -2.0]]
    # B^T @ grad_output = [[0.5, 0], [0, 0.5]] @ [1, -1] = [0.5, -0.5]
    # grad_A = outer([0.5, -0.5], x) * scaling = [[0.5, 1.0, 1.5], [-0.5, -1.0, -1.5]]
    expected_grad_A = [[0.5, 1.0, 1.5], [-0.5, -1.0, -1.5]]

    ok_B = all(abs(result['grad_B'][i][j] - expected_grad_B[i][j]) < 1e-6
               for i in range(d_out) for j in range(rank))
    ok_A = all(abs(result['grad_A'][i][j] - expected_grad_A[i][j]) < 1e-6
               for i in range(rank) for j in range(d_in))

    if ok_B:
        print(f"  ✅ grad_B 正确: {result['grad_B']}")
    else:
        print(f"  ❌ grad_B 不正确")
        print(f"     期望: {expected_grad_B}")
        print(f"     得到: {result['grad_B']}")
        return False

    if ok_A:
        print(f"  ✅ grad_A 正确: {result['grad_A']}")
        print(f"     注意：W 的梯度不需要计算（冻结！）")
        return True
    else:
        print(f"  ❌ grad_A 不正确")
        print(f"     期望: {expected_grad_A}")
        print(f"     得到: {result['grad_A']}")
        return False


def test_lora_training_step():
    print("\n" + "=" * 55)
    print("测试 Part 4: lora_training_step()")
    print("=" * 55)

    d_in, d_out, rank = 3, 2, 2
    W = [[1.0, 0.0, 0.0],
         [0.0, 1.0, 0.0]]
    A = [[0.1, 0.0, 0.0],
         [0.0, 0.1, 0.0]]
    B = [[0.0, 0.0],
         [0.0, 0.0]]

    x = [1.0, 2.0, 3.0]
    target = [2.0, 0.0]  # 我们想让输出从 [1, 2] 变成 [2, 0]

    result = lora_training_step(W, A, B, x, target, learning_rate=0.1, scaling=1.0)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if 'loss' not in result or 'new_A' not in result or 'new_B' not in result:
        print("  ❌ 返回字典缺少必要的键")
        return False

    # B 初始为零，所以初始输出 = Wx = [1, 2]
    # target = [2, 0]，所以 loss = ((1-2)^2 + (2-0)^2) / 2 = (1+4)/2 = 2.5
    expected_loss = 2.5
    if abs(result['loss'] - expected_loss) < 1e-4:
        print(f"  ✅ 初始 loss = {result['loss']:.4f}（Wx=[1,2] vs target=[2,0]）")
    else:
        print(f"  ❌ 初始 loss 期望 {expected_loss}，得到 {result['loss']:.4f}")
        return False

    # 检查 W 没有被修改
    if W[0][0] == 1.0 and W[1][1] == 1.0:
        print(f"  ✅ 原始权重 W 未被修改（冻结 ✓）")
    else:
        print(f"  ❌ W 被修改了！LoRA 训练中 W 应该保持不变")
        return False

    # 做第二步，loss 应该更低
    result2 = lora_training_step(W, result['new_A'], result['new_B'], x, target, 0.1, 1.0)
    if result2['loss'] < result['loss']:
        print(f"  ✅ 第二步 loss = {result2['loss']:.4f} < {result['loss']:.4f}（在学习 ✓）")
        return True
    else:
        print(f"  ⚠️  第二步 loss 没有下降，检查梯度更新逻辑")
        return False


def test_lora_finetune():
    print("\n" + "=" * 55)
    print("测试 Part 5: lora_finetune()")
    print("=" * 55)

    random.seed(42)

    # 场景：原始权重 W 是单位矩阵（输出=输入）
    # 我们用 LoRA 教它学会一个新的映射
    d = 4
    W = [[1.0 if i == j else 0.0 for j in range(d)] for i in range(d)]

    # 训练数据：我们想让模型学会"输出 = 输入的反转"
    train_data = [
        ([1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]),
        ([0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]),
        ([0.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0, 1.0], [1.0, 0.0, 0.0, 0.0]),
    ]

    result = lora_finetune(W, train_data, rank=4, learning_rate=0.1, n_epochs=50, scaling=1.0)

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    required_keys = ['final_A', 'final_B', 'loss_history', 'initial_loss', 'final_loss']
    for key in required_keys:
        if key not in result:
            print(f"  ❌ 返回字典缺少 '{key}'")
            return False

    history = result['loss_history']
    initial = result['initial_loss']
    final = result['final_loss']

    print(f"  📈 训练过程：")
    print(f"     初始 Loss = {initial:.6f}")
    print(f"     最终 Loss = {final:.6f}")

    if final >= initial:
        print(f"  ❌ Loss 没有下降！检查训练循环逻辑")
        return False

    print(f"  ✅ Loss 下降了 {(1 - final/initial)*100:.1f}%")

    # 检查微调后的效果
    A, B = result['final_A'], result['final_B']
    test_input = [1.0, 0.0, 0.0, 0.0]
    test_output = lora_forward(W, A, B, test_input, scaling=1.0)
    expected = [0.0, 0.0, 0.0, 1.0]

    error = sum(abs(test_output[i] - expected[i]) for i in range(d)) / d
    print(f"\n  🧪 微调效果验证：")
    print(f"     输入: {test_input}")
    print(f"     期望: {expected}")
    print(f"     实际: [{', '.join(f'{v:.3f}' for v in test_output)}]")
    print(f"     平均误差: {error:.4f}")

    if error < 0.2:
        print(f"  ✅ 模型学会了新映射！（误差 < 0.2）")
    else:
        print(f"  ⚠️  误差偏大，可能需要更多训练步或更大的 rank")

    # 可视化 loss 下降
    total_steps = len(history)
    print(f"\n  📉 Loss 曲线（{total_steps} 步训练）：")
    step_interval = max(1, total_steps // 6)
    for i in range(0, min(total_steps, 6 * step_interval), step_interval):
        bar_len = int(min(history[i] / max(initial, 0.001), 1.0) * 30)
        bar = '█' * bar_len + '░' * (30 - bar_len)
        print(f"     Step {i:3d} | {bar} | {history[i]:.4f}")

    print(f"\n  🎓 LoRA 成功地在不修改 W 的情况下让模型学会了新行为！")
    print(f"     原始 W 是单位矩阵（输出=输入），LoRA 教它学会了「反转」")
    return final < initial * 0.5


if __name__ == "__main__":
    print()
    print("🎓 第七课练习：实现 LoRA 微调")
    print("=" * 55)
    print()

    all_passed = True
    all_passed = test_lora_forward() and all_passed
    all_passed = test_count_parameters() and all_passed
    all_passed = test_lora_gradient() and all_passed
    all_passed = test_lora_training_step() and all_passed
    all_passed = test_lora_finetune() and all_passed

    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 全部通过！你已经完整实现了 LoRA 微调！")
        print("   你刚刚亲手实现了：")
        print("   LoRA 前向 → 参数统计 → 梯度计算 → 训练步 → 完整微调")
        print()
        print("   这就是让开源模型变成你的专属助手的核心技术。")
        print("   真实的 LoRA 微调还需要：更好的初始化策略、")
        print("   学习率调度、梯度累积、多层同时适配等。")
        print("   但核心数学原理就是你刚写的：W 不动，只训练旁边的 BA。")
    else:
        print("💪 还有测试没通过，继续加油！")
        print("   提示：按照 TODO 的顺序逐个实现，每完成一个就运行一次检查")
    print("=" * 55)
    print()
