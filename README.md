# LLM Interactive Course · 大模型交互式课程

从零理解大语言模型：每课一份可交互的 `lesson.html` + 一份带自测的 `exercise.py`。  
用纯 Python（几乎不依赖第三方库）动手实现 Tokenization、Attention、训练、RLHF、推理优化、LoRA 与 Agent。

远程仓库：[github.com/ericffu/llm-interactive-course](https://github.com/ericffu/llm-interactive-course)

## 课程目录

| 目录 | 主题 | 练习内容 |
|------|------|----------|
| [`01-tokenization`](01-tokenization/) | Tokenization — 文字如何变成数字 | 手写简易 BPE Tokenizer |
| [`02-embedding-prediction`](02-embedding-prediction/) | Embedding 与 Next-Token Prediction | Embedding → Softmax → 交叉熵 |
| [`03-transformer`](03-transformer/) | Transformer — 模型如何「思考」 | 手写 Self-Attention |
| [`04-training`](04-training/) | 训练 — 模型如何从数据中学习 | 损失、梯度与训练循环 |
| [`05-rlhf`](05-rlhf/) | RLHF 与对齐 | 奖励、偏好损失、DPO |
| [`06-inference`](06-inference/) | 推理优化 | KV Cache、量化、采样 |
| [`07-finetuning`](07-finetuning/) | 微调与 LoRA | LoRA 前向、梯度与微调循环 |
| [`08-agents`](08-agents/) | Agent 与工具调用 | 迷你 Agent 工具循环 |

## 使用方式

### 1. 看课（浏览器）

直接打开任意一课的 HTML：

```bash
open 01-tokenization/lesson.html
# 或用任意静态服务器 / 浏览器打开对应路径
```

### 2. 做练习（Python）

需要 **Python 3.10+**（类型注解使用了 `list[str]` 等写法）。练习默认只依赖标准库。

```bash
cd 01-tokenization
python exercise.py
```

按文件中的 `TODO` 补全实现；全部通过后会看到测试成功提示。

其余各课同理：进入对应目录后运行 `python exercise.py`。

## 建议学习路径

1. 先打开当课 `lesson.html` 建立直觉  
2. 再完成同目录 `exercise.py` 中的 TODO  
3. 按编号顺序推进；前四课偏「模型怎么工作」，后四课偏「怎么训、怎么跑、怎么定制与行动」

## 项目结构

```
llm-interactive-course/
├── README.md
├── 01-tokenization/
│   ├── lesson.html
│   └── exercise.py
├── 02-embedding-prediction/
│   └── ...
└── ...
```

## License

个人学习与分享用途。欢迎 Star / Fork；若用于教学转载，请注明出处。
