"""
============================================================
第一课练习：手写一个简易 BPE Tokenizer
============================================================

BPE (Byte Pair Encoding) 是 GPT、LLaMA 等大模型使用的核心分词算法。
在这个练习中，你将从零实现一个简化版的 BPE tokenizer。

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过 ✅

难度：⭐⭐ (适合有 Python 基础的初学者)
预计用时：20-30 分钟
"""

from collections import Counter


# ============================================================
# 🧱 Part 1: 统计相邻 pair 的频率
# ============================================================
#
# 给定一个 token 列表（如 ["l", "o", "w"]），
# 统计所有相邻 pair 出现的次数。
#
# 例如：["l", "o", "w", "l", "o", "w"]
#   → {("l","o"): 2, ("o","w"): 2, ("w","l"): 1}
#

def count_pairs(token_list: list[str]) -> dict[tuple[str, str], int]:
    """统计 token_list 中所有相邻 pair 的频率。

    Args:
        token_list: 一维的 token 列表，如 ["l", "o", "w", "e", "r"]

    Returns:
        字典，key 是 (token_a, token_b) 元组，value 是出现次数
    """
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：遍历列表，取每个 token_list[i] 和 token_list[i+1] 组成 pair
    # 用 Counter 或普通 dict 来计数

    # pass  # ← 删掉这行，写你的实现
    return dict(Counter(zip(token_list, token_list[1:])))

    # ======== END TODO 1 ========


# ============================================================
# 🔗 Part 2: 合并指定的 pair
# ============================================================
#
# 给定一个 token 列表和一个要合并的 pair，
# 将列表中所有相邻出现的该 pair 合并为一个新 token。
#
# 例如：merge_pair(["l", "o", "w"], ("l", "o"))
#   → ["lo", "w"]
#

def merge_pair(token_list: list[str], pair: tuple[str, str]) -> list[str]:
    """将 token_list 中所有相邻的 pair 合并为一个新 token。

    Args:
        token_list: 当前的 token 列表
        pair: 要合并的 (token_a, token_b)

    Returns:
        合并后的新 token 列表
    """
    # ======== TODO 2: 在这里写你的代码 ========
    # 提示：遍历列表，当发现 token_list[i] == pair[0] 且 token_list[i+1] == pair[1] 时，
    # 将它们合并为 pair[0] + pair[1]，跳过下一个位置
    #
    # 例如：["a", "b", "c", "a", "b"] + pair=("a","b") → ["ab", "c", "ab"]

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 2 ========


# ============================================================
# 🏋️ Part 3: BPE 训练循环
# ============================================================
#
# 现在把上面两个函数组合起来，实现完整的 BPE 训练。
# 思路：反复找到频率最高的 pair → 合并 → 直到达到目标词表大小。
#

def train_bpe(text: str, num_merges: int) -> tuple[list[str], list[tuple[str, str]]]:
    """训练 BPE tokenizer。

    Args:
        text: 训练语料（一段文本）
        num_merges: 要执行的合并次数

    Returns:
        (final_tokens, merge_rules)
        - final_tokens: 最终的 token 列表
        - merge_rules: 按顺序记录的合并规则列表，如 [("l","o"), ("lo","w"), ...]
    """
    # Step 1: 将文本拆分为单个字符（初始 token）
    tokens = list(text)
    merge_rules = []

    # ======== TODO 3: 在这里写你的代码 ========
    # 提示：写一个循环，重复 num_merges 次：
    #   1. 用 count_pairs() 统计当前 tokens 中的 pair 频率
    #   2. 找到频率最高的 pair（提示：用 max() 函数配合 key 参数）
    #   3. 用 merge_pair() 执行合并
    #   4. 把合并规则记录到 merge_rules 列表中
    #
    # 注意：如果没有可合并的 pair 了（count_pairs 返回空字典），提前退出循环

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 3 ========

    return tokens, merge_rules


# ============================================================
# 🔄 Part 4: 编码和解码
# ============================================================

def encode(text: str, merge_rules: list[tuple[str, str]]) -> list[str]:
    """用训练好的 merge_rules 对新文本进行编码（tokenize）。

    Args:
        text: 要编码的文本
        merge_rules: 训练时得到的合并规则

    Returns:
        编码后的 token 列表
    """
    # ======== TODO 4: 在这里写你的代码 ========
    # 提示：
    #   1. 先把 text 拆成单个字符列表
    #   2. 按照 merge_rules 的顺序，依次应用每条 merge 规则
    #      （对当前 token 列表调用 merge_pair）
    #   3. 返回最终的 token 列表

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 4 ========


def decode(tokens: list[str]) -> str:
    """将 token 列表解码回原始文本。

    这个很简单，送你了 :)
    """
    return "".join(tokens)


# ============================================================
# 🧪 测试 — 运行 python exercise.py 来检查你的实现
# ============================================================

def test_count_pairs():
    print("=" * 50)
    print("测试 Part 1: count_pairs()")
    print("=" * 50)

    result = count_pairs(["l", "o", "w", "l", "o", "w"])
    expected = {("l", "o"): 2, ("o", "w"): 2, ("w", "l"): 1}

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if result == expected:
        print(f"  ✅ 通过！{result}")
        return True
    else:
        print(f"  ❌ 期望: {expected}")
        print(f"       得到: {result}")
        return False


def test_merge_pair():
    print("\n" + "=" * 50)
    print("测试 Part 2: merge_pair()")
    print("=" * 50)

    result = merge_pair(["l", "o", "w", "l", "o", "w"], ("l", "o"))
    expected = ["lo", "w", "lo", "w"]

    if result is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    if result == expected:
        print(f"  ✅ 通过！{result}")
    else:
        print(f"  ❌ 期望: {expected}")
        print(f"       得到: {result}")
        return False

    result2 = merge_pair(["a", "b", "c", "a", "b", "a"], ("a", "b"))
    expected2 = ["ab", "c", "ab", "a"]
    if result2 == expected2:
        print(f"  ✅ 通过！{result2}")
        return True
    else:
        print(f"  ❌ 期望: {expected2}")
        print(f"       得到: {result2}")
        return False


def test_train_bpe():
    print("\n" + "=" * 50)
    print("测试 Part 3: train_bpe()")
    print("=" * 50)

    tokens, rules = train_bpe("aaabdaaabac", 3)

    if tokens is None:
        print("  ❌ 函数返回了 None — 你还没写实现呢！")
        return False

    print(f"  训练语料: 'aaabdaaabac'")
    print(f"  合并 3 次后:")
    print(f"  Token 列表: {tokens}")
    print(f"  合并规则:   {rules}")

    if rules[0] == ("a", "a"):
        print("  ✅ 第一条规则正确: ('a', 'a') — 'aa' 出现最多")
    else:
        print(f"  ❌ 第一条规则应该是 ('a', 'a')，但得到了 {rules[0]}")
        return False

    if rules[1] == ("aa", "a"):
        print("  ✅ 第二条规则正确: ('aa', 'a') — 'aaa' 是下一个高频")
    else:
        print(f"  ❌ 第二条规则应该是 ('aa', 'a')，但得到了 {rules[1]}")
        return False

    if rules[2] == ("aaa", "b"):
        print("  ✅ 第三条规则正确: ('aaa', 'b') — 'aaab' 出现 2 次")
    else:
        print(f"  ❌ 第三条规则应该是 ('aaa', 'b')，但得到了 {rules[2]}")
        return False

    return True


def test_encode_decode():
    print("\n" + "=" * 50)
    print("测试 Part 4: encode() & decode()")
    print("=" * 50)

    _, rules = train_bpe("aaabdaaabac", 3)
    encoded = encode("aaab", rules)

    if encoded is None:
        print("  ❌ encode() 返回了 None — 你还没写实现呢！")
        return False

    print(f"  编码 'aaab': {encoded}")
    expected = ["aaab"]
    if encoded == expected:
        print(f"  ✅ 编码正确！")
    else:
        print(f"  ❌ 期望: {expected}，得到: {encoded}")
        return False

    decoded = decode(encoded)
    if decoded == "aaab":
        print(f"  ✅ 解码正确！'{decoded}'")
    else:
        print(f"  ❌ 解码失败: '{decoded}'")
        return False

    encoded2 = encode("aaac", rules)
    print(f"  编码 'aaac': {encoded2}")
    expected2 = ["aaa", "c"]
    if encoded2 == expected2:
        print(f"  ✅ 编码正确！新文本也能正确编码")
        return True
    else:
        print(f"  ❌ 期望: {expected2}，得到: {encoded2}")
        return False


if __name__ == "__main__":
    print()
    print("🎓 第一课练习：手写 BPE Tokenizer")
    print("=" * 50)
    print()

    all_passed = True
    all_passed = test_count_pairs() and all_passed
    all_passed = test_merge_pair() and all_passed
    all_passed = test_train_bpe() and all_passed
    all_passed = test_encode_decode() and all_passed

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 全部通过！你已经理解了 BPE 的核心原理！")
        print("   下一步：打开第二课学习 Embedding 和 Next-Token Prediction")
    else:
        print("💪 还有测试没通过，继续加油！")
        print("   提示：按照 TODO 的顺序逐个实现，每完成一个就运行一次检查")
    print("=" * 50)
    print()
