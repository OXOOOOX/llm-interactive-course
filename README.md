# Interactive Course · 交互式课程

用 AI 生成的交互式 HTML 课程，覆盖多个领域。每课一份可交互的 `lesson.html`，部分课程附带动手练习。

本项目包含两部分：

1. **`courses/`** — 已生成的完整课程，可直接浏览器打开学习
2. **`skill/`** — 课程生成器的 Cursor Skill，可用来生成任意主题的新课程

---

## 🚀 服务器自动部署

生产网站 [sdspeed.com.cn](https://sdspeed.com.cn) 使用自有腾讯云服务器。更新
`OXOOOOX/llm-interactive-course` 的 `main` 分支后，GitHub Actions 自动同步源码，
在服务器检查课程与资源、打包镜像，再切换新版本。电脑不需要一直开机。

1. 修改课程或静态资源，检查后提交到生产仓库的 `main`。
2. 在仓库 **Actions** 中确认检查和部署任务均成功。
3. 打开原域名验证修改；手动运行工作流时，勾选 `activate` 才会正式上线。

域名根路径继续跳转到 **AI 产品经理实战课**。`_redirects` 和 `_headers` 会在打包时
转换为独立的 Caddy 配置。网站保留 `connect-src 'none'`，仅提供静态课程，
不调用生成式人工智能实时服务。学习进度与笔记继续保存在原浏览器。

Zeabur 的旧 GitHub 发布连接已解除，原课程分支的线上内容已接续到 `main`。
目录、配置、检查和回退方法见 [服务器部署说明](deploy/README.md)。

---

## 📚 已生成的课程

### AI 产品经理实战课

> 从真实问题出发，学习 AI 产品经理如何判断机会、设计人机协作、建立评估体系，并把原型安全地推向上线。

**受众**：零基础产品经理 / 想转向 AI 产品方向的学习者

**课数**：6 课

**配套练习**：✅ 交互判断、测验、思考笔记与毕业方案

| 目录 | 主题 |
|------|------|
| [`01-role-and-boundary`](courses/AI产品经理实战课/01-role-and-boundary/) | 角色与边界 |
| [`02-find-the-problem`](courses/AI产品经理实战课/02-find-the-problem/) | 找到真问题 |
| [`03-design-ai-experience`](courses/AI产品经理实战课/03-design-ai-experience/) | 设计 AI 体验 |
| [`04-evals-and-metrics`](courses/AI产品经理实战课/04-evals-and-metrics/) | 评估与指标 |
| [`05-prototype-to-launch`](courses/AI产品经理实战课/05-prototype-to-launch/) | 从原型到上线 |
| [`06-capstone`](courses/AI产品经理实战课/06-capstone/) | 毕业实战 |

### 大模型训练课

> 从零理解大语言模型：用纯 Python 动手实现 Tokenization、Attention、训练、RLHF、推理优化、LoRA 与 Agent。

**受众**：有一点技术背景的产品经理 / 对 AI 感兴趣的入门者  
**课数**：8 课  
**配套练习**：✅ 代码练习（`exercise.py`，纯 Python，无需第三方依赖）

| 目录 | 主题 | 练习内容 |
|------|------|----------|
| [`01-tokenization`](courses/大模型训练课/01-tokenization/) | Tokenization — 文字如何变成数字 | 手写简易 BPE Tokenizer |
| [`02-embedding-prediction`](courses/大模型训练课/02-embedding-prediction/) | Embedding 与 Next-Token Prediction | Embedding → Softmax → 交叉熵 |
| [`03-transformer`](courses/大模型训练课/03-transformer/) | Transformer — 模型如何「思考」 | 手写 Self-Attention |
| [`04-training`](courses/大模型训练课/04-training/) | 训练 — 模型如何从数据中学习 | 损失、梯度与训练循环 |
| [`05-rlhf`](courses/大模型训练课/05-rlhf/) | RLHF 与对齐 | 奖励、偏好损失、DPO |
| [`06-inference`](courses/大模型训练课/06-inference/) | 推理优化 | KV Cache、量化、采样 |
| [`07-finetuning`](courses/大模型训练课/07-finetuning/) | 微调与 LoRA | LoRA 前向、梯度与微调循环 |
| [`08-agents`](courses/大模型训练课/08-agents/) | Agent 与工具调用 | 迷你 Agent 工具循环 |

### 浪漫主义古典音乐

> 走进 19 世纪的音乐世界：从贝多芬的革命到马勒的黄昏，理解浪漫主义如何改变了古典音乐的面貌。

**受众**：有一定音乐基础（了解基本乐理、能识谱）  
**课数**：8 课（持续生成中）  
**配套练习**：无  
**特色**：浅色人文风格 · 内嵌 YouTube 聆听示例 · 风格对比交互

| 目录 | 主题 | 状态 |
|------|------|------|
| [`01-classical-to-romantic`](courses/浪漫主义古典音乐/01-classical-to-romantic/) | 从古典到浪漫 — 一场美学革命 | ✅ |
| `02-beethoven` | 贝多芬 — 跨越两个时代的巨人 | 🔜 |
| `03-piano-poets` | 钢琴诗人 — 肖邦与李斯特 | 🔜 |
| `04-art-song` | 歌曲的艺术 — 舒伯特与艺术歌曲 | 🔜 |
| `05-symphonic-ambition` | 交响的野心 — 从柏辽兹到布鲁克纳 | 🔜 |
| `06-opera-wars` | 歌剧战争 — 瓦格纳 vs 威尔第 | 🔜 |
| `07-nationalism` | 民族之声 — 音乐中的身份认同 | 🔜 |
| `08-late-romanticism` | 黄昏与黎明 — 晚期浪漫主义的终章 | 🔜 |

---

## 🛠️ 课程生成器 Skill

[`skill/SKILL.md`](skill/SKILL.md) 是一个 [Cursor Skill](https://docs.cursor.com/)，可以为**任意主题**生成交互式课程。

### 功能

- 🎯 自动规划课程大纲（课次、核心概念、呈现方式）
- 🎨 根据学科类型自动选择视觉风格（深色科技风 / 浅色人文风）
- 🧩 丰富的交互组件库（时间轴、A/B 对比、步进动画、Canvas 可视化等）
- 📝 自适应练习类型（代码练习 / 思考练习 / 实操练习）
- 📖 自动搜索并整理延伸阅读资料
- ♫ 支持聆听示例组件（音乐/语言类课程）

### 使用方式

1. 将 `skill/SKILL.md` 复制到你项目的 `.cursor/skills/interactive-course/SKILL.md`
2. 在 Cursor 中对 AI 说："帮我生成一套关于 X 的课程"
3. AI 会按 Skill 定义的流程自动执行：需求确认 → 课程规划 → 逐课生成

### 已验证的课程主题

| 主题 | 学科类型 | 视觉方案 | 练习形式 |
|------|---------|---------|---------|
| 大模型训练（LLM） | 理工科 / 编程 | 深色科技风 | 代码练习 (`exercise.py`) |
| 浪漫主义古典音乐 | 人文 / 艺术 | 浅色人文风 | 无练习 |

---

## 使用方式

### 浏览课程（浏览器）

直接打开任意一课的 HTML 文件：

```bash
open courses/大模型训练课/01-tokenization/lesson.html
open courses/浪漫主义古典音乐/01-classical-to-romantic/lesson.html
```

### 做代码练习（Python 3.10+）

```bash
cd courses/大模型训练课/01-tokenization
python exercise.py
```

按文件中的 `TODO` 补全实现，全部通过后会看到测试成功提示。

---

## 项目结构

```
.
├── index.html                        # Zeabur 静态站点入口
├── _redirects                       # 首页服务端跳转规则
├── _headers                         # 基础安全响应头
├── assets/
│   └── site-compliance.js           # 全站固定备案栏与静态服务声明
├── README.md
├── courses/                          # 已生成的课程
│   ├── AI产品经理实战课/                # 6 课 · 交互式产品实战
│   │   ├── index.html
│   │   └── 01-role-and-boundary/
│   │       └── lesson.html
│   ├── 大模型训练课/                   # 8 课 · 深色科技风 · 含代码练习
│   │   ├── 01-tokenization/
│   │   │   ├── lesson.html
│   │   │   └── exercise.py
│   │   ├── 02-embedding-prediction/
│   │   └── ...
│   └── 浪漫主义古典音乐/               # 8 课 · 浅色人文风 · 持续生成中
│       └── 01-classical-to-romantic/
│           └── lesson.html
└── skill/                            # 课程生成器
    └── SKILL.md                      # Cursor Skill 定义文件
```

## License

个人学习与分享用途。欢迎 Star / Fork；若用于教学转载，请注明出处。
