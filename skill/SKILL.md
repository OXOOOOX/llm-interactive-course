---
name: interactive-course
description: >-
  为任意领域或知识点生成一套交互式课程。输出为多课时的 HTML 课程页（含可视化、动画、交互演示、测验）及可选的配套练习（代码练习 / 思考练习 / 实操练习）。
  课程结构、呈现方式、视觉风格由 Agent 根据学科类型自动适配。
  Use when the user asks to "帮我生成一套课程"、"给我做一个教程"、"我想学 X"、"生成交互式课程"、"create a course on X"、"teach me about X" or similar requests for structured learning content.
---

# Interactive Course Generator

为用户生成一套结构化的交互式课程。每课为一个独立 HTML 页面，包含可视化、动画、交互演示、测验等元素，以及可选的配套练习。

## 何时触发

- 用户要求"帮我生成一套课程 / 教程 / 学习材料"
- 用户说"我想学 X，帮我规划"
- 用户要求"给我做一个关于 Y 的交互式教程"
- 用户在已有课程基础上要求"继续生成下一课"

不触发：用户只是提问某个知识点（走普通问答），或者要求生成 PPT / 视频脚本等非 HTML 交付物。

---

## Phase 1 — 需求确认

用 AskQuestion 或对话确认以下信息：

1. **主题**：要学什么？（如"微观经济学"、"React 开发"、"唐宋诗词赏析"）
2. **目标受众**：学习者的知识水平（如"零基础产品经理"、"有 Python 基础的开发者"、"高中生"）
3. **预计课数**：用户期望的课程长度（默认 5-8 课，Agent 可根据主题建议调整）
4. **配套练习**：是否需要？形式由 Agent 根据学科类型自动适配——
   - 编程 / 理工科 → **代码练习**（独立 `exercise.py`，TODO 脚手架 + 自测）
   - 人文 / 社科 / 商业 → **思考练习**（嵌入 HTML，案例分析、论述、情境判断、概念辨析等）
   - 语言学习 → **实操练习**（嵌入 HTML，填空、翻译、语法改错、配对连线等）
   - 用户也可以指定不需要任何练习
5. **语言偏好**：课程内容用中文还是英文（默认中文）
6. **存放路径**：课程文件放在仓库的哪个目录下（默认 `互动课程/<课程主题>/`）

如果用户的请求已经隐含了以上大部分信息，不需要逐条追问——直接推断，只对不确定的点做确认。

---

## Phase 2 — 课程规划

### 2.1 生成大纲

根据确认的需求，规划完整的课程大纲。以 Markdown 表格呈现给用户确认：

```markdown
| 课次 | 标题 | 核心概念 | 主要呈现方式 | 练习类型 |
|------|------|----------|-------------|---------|
| 01 | … | 概念A, 概念B, 概念C | 故事卡 + 步进动画 + 模拟器 | 代码练习 |
| 02 | … | 概念D, 概念E | Canvas 可视化 + 概率条 | 思考练习 |
| … | … | … | … | … |
```

### 2.2 规划原则

- 每课聚焦 3-5 个核心概念，不贪多
- 课与课之间有清晰的逻辑递进（前一课是后一课的基础）
- 第一课应从最直觉、最容易理解的概念入手
- 呈现方式应与内容特点匹配（见「呈现组件库」）
- 每课的交互元素不少于 1 个，测验不少于 3 题

### 2.3 用户确认

将大纲呈现给用户，等待确认或调整后再进入 Phase 3。

---

## Phase 3 — 逐课生成

### 3.1 生成顺序

按课次顺序逐课生成。每课产出：
- `lesson.html` — 交互式课程页（必须）
- `exercise.py` — 代码练习文件（仅编程/理工科类且用户选择需要时）

### 3.2 每课 HTML 结构

```
hero（课次标签 + 标题 + 副标题）
  ↓
settings-bar（配套练习开关，有练习时才显示）
  ↓
container
  ├── §0 快速回顾（第 2 课起）
  ├── §1-N 主内容章节（3-8 节）
  │     每节内可包含：正文段落、故事卡、要点框、
  │     交互演示、代码块、流程图、对比表等
  │     部分章节内可嵌入「延伸阅读」内联卡片
  ├── §延伸阅读（课末汇总）
  ├── §测验（3-4 题选择题）
  ├── §配套练习（id="code-exercise"，可被 toggle 隐藏）
  └── lesson-nav（上一课/下一课链接，始终可见）
```

### 3.3 文字量要求

每节课必须有充分的文字讲解。标准：**仅阅读文字（不看任何交互元素）也能完整理解全部概念和逻辑关系**。交互元素是锦上添花的辅助，不是替代文字的捷径。

### 3.4 延伸阅读

每课生成完主体内容后，针对核心概念做 2-3 次 WebSearch，寻找权威参考资料。

**课末汇总**（`§延伸阅读`）：列 3-6 条资料，每条含标题、来源、一句话说明。

**章节内联**：在正文的关键章节中，可插入 1-2 个小型内联阅读卡片：
```html
<div class="further-reading-inline">
  <span class="fr-icon">📖</span>
  <span>想深入了解 X？→ <a href="..." target="_blank">《资料标题》</a>（来源，一句话推荐理由）</span>
</div>
```

**材料标准**：
- 必须匹配目标受众的知识水平
- 只推公认优质资料（官方文档、经典教材、权威博客、知名课程等）
- 搜索不要占用太多时间——课程内容本身是重点

### 3.5 配套练习开关

所有包含配套练习的课都应有 `settings-bar` + toggle：

```html
<div class="settings-bar">
  <label class="toggle-wrap active" id="code-toggle">
    <span>配套练习</span>
    <div class="toggle-track"></div>
  </label>
</div>
```

JS 逻辑：读写 `localStorage` key `course-show-exercises`，切换 `#code-exercise.hidden`。所有课共享同一个 key，用户在任一课关闭后，其他课也自动隐藏。

---

## 呈现组件库

根据内容特点选择合适的组件。以下为可用组件及适用场景：

### 通用组件（所有学科适用）

| 组件 | CSS 类 | 适用场景 |
|------|--------|---------|
| 故事卡 | `.story-card` | 类比引入、真实案例、任务说明 |
| 要点框 | `.insight-box` | 核心认知、关键要点、容易被忽略的重点 |
| 三栏对比 | `.compare-grid` + `.compare-box` | 2-3 种方案/概念的优劣对比 |
| 流程管线 | `.pipeline` + `.pipeline-step` | 线性流程、因果链、数据流 |
| 代码块 | `.code-block` | 伪代码、公式、配置示例 |
| 引用块 | `.blockquote` | 示例推导、名言、假设情境 |
| 选择题测验 | `.quiz` + `.quiz-option` | 理解检验（每课 3-4 题） |
| 数据表格 | `.compare-table` | 参数对比、特性比较 |
| 卡片网格 | `.method-cards` | 工具/方法/人物/作品列表 |

### 交互组件（按需选用）

| 组件 | 适用场景 | 复杂度 |
|------|---------|--------|
| 步进动画 | 算法/过程逐步演示（如 BPE 合并） | 中 |
| 输入框 + Tab 切换 | 实时模拟器（如分词器、计算器） | 中 |
| Canvas 2D 可视化 | 散点图、曲线图、空间分布 | 高 |
| 热力图/矩阵 | 权重、关系强度、时间表 | 中 |
| 概率条/进度条 | 概率分布、性能对比、占比 | 低 |
| A/B 偏好选择 | 标注体验、判断练习、审美比较 | 中 |
| 对话模拟 | 对话流程、API 交互、角色扮演 | 低 |
| 循环/流程图 | 迭代过程、反馈环路 | 低 |
| 时间轴 | 历史演进、项目阶段、生平纪事 | 中 |
| 拖拽排序 | 排序练习、优先级排列 | 高 |
| 填空/配对 | 语言练习、概念匹配 | 中 |
| 聆听示例 | 音乐/语言/演讲类课程的音视频示范 | 低 |

选择原则：每课至少 1 个交互组件。优先选低/中复杂度组件；Canvas 等高复杂度组件仅在确实需要可视化空间关系时使用。

### 聆听示例组件（音乐/音频类课程）

当课程涉及音乐、语言、演讲等需要听觉示范的领域时，使用「聆听示例」组件嵌入 YouTube 视频（懒加载，点击后才加载 iframe）：

```html
<div class="listen-card">
  <div class="listen-header">
    <div class="listen-icon">♫</div>
    <div class="listen-meta">
      <div class="listen-title">作品名称</div>
      <div class="listen-subtitle">完整标题 · 演奏者/乐团</div>
    </div>
  </div>
  <div class="listen-body">
    <p>为什么选这段、听什么、和课程内容的关系。</p>
    <div class="listen-guide">
      <strong>聆听提示：</strong>具体的时间点和聆听要点。
    </div>
  </div>
  <a class="listen-player" href="https://www.youtube.com/watch?v=VIDEO_ID&t=STARTs" target="_blank" rel="noopener">
    <img src="https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg" alt="描述">
    <div class="play-overlay">
      <div class="play-btn">▶</div>
      <div class="play-label">在 YouTube 中播放</div>
    </div>
  </a>
</div>
```

技术说明：
- 使用 `<a>` 标签 + YouTube 缩略图（`img.youtube.com/vi/ID/hqdefault.jpg`），点击在新标签页打开 YouTube
- 不使用 iframe 嵌入——本地 `file://` 协议下 YouTube iframe 会报 Error 153
- 通过 URL 参数 `&t=NNs` 跳转到指定时间点
- 缩略图加 `opacity` 遮罩 + hover 动效，视觉上接近播放器体验

使用原则：
- 每课 2-4 个聆听示例，放在讲解相关概念的段落之后
- 优先选择知名乐团/演奏家的官方频道录制（DG、Decca、Berliner Phil 等）
- 使用 `data-start` 参数精确跳转到最关键的段落
- 每个示例都需要「聆听提示」，告诉学习者具体要听什么、注意哪个时间点

---

## 视觉风格

### 方案选择

Agent 根据课程主题自动判断使用哪套方案。不确定时默认浅色。

#### 深色方案（理工科 / 编程类）

```css
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface2: #242836;
  --border: #2e3347;
  --text: #e4e6f0;
  --text-dim: #8b8fa8;
  --accent: #6c8cff;    /* 每课可换 */
  --accent2: #a78bfa;
}
body { background: var(--bg); color: var(--text); }
```

适合：编程教程、AI/ML、数据科学、数学、工程类。

#### 浅色方案（人文 / 社科 / 通用类）

```css
:root {
  --bg: #faf9f5;
  --surface: #ffffff;
  --surface2: #f3f1ec;
  --border: #e5e2db;
  --text: #1a1a1a;
  --text-dim: #6b6560;
  --accent: #c2785c;    /* 每课可换 */
  --accent2: #8b6d5c;
}
body {
  background: var(--bg); color: var(--text);
  font-family: 'Source Serif 4', Georgia, 'Noto Serif SC', serif;
}
```

适合：文学、历史、哲学、经济学、心理学、语言学习、商业管理等。
标题可用衬线字体增加质感；正文保持无衬线以确保可读性。

### 跨课一致性

同一套课程内所有课共用同一套视觉方案。每课可通过调整 `--accent` 主题色来区分，但 `--bg`、`--surface`、`--text` 等基础色保持一致。

---

## 设计规范

### 章节编号

- `h2` 使用 `.num` 编号徽章：`<h2><span class="num">1</span> 章节标题</h2>`
- 第一课从 1 开始；第二课起以 0（快速回顾）开头
- 补充/延伸章节可用 `✦` 代替数字

### 每课必含元素

- Hero 区域（课次标签 + 标题 + 一句话副标题）
- 至少 1 个交互组件
- 至少 1 个故事卡或要点框
- 3-4 道选择题测验
- 延伸阅读板块
- 课程导航链接

### lesson-nav

```html
<!-- 始终在 container 末尾，code-exercise section 之外 -->
<div class="lesson-nav">
  <a href="../01-xxx/lesson.html">← 上一课：XXX</a>
  <a href="../03-xxx/lesson.html">下一课：XXX →</a>
</div>
```

第一课左侧写"← 这是第一课"（无链接），最后一课右侧写"课程完结"。

### 测验 JS（所有课复用）

```javascript
function checkQuiz(btn, quizId) {
  const quiz = document.getElementById(quizId);
  const options = quiz.querySelectorAll('.quiz-option');
  const isCorrect = btn.dataset.correct === 'true';
  options.forEach(o => {
    o.disabled = true;
    o.style.pointerEvents = 'none';
    o.style.opacity = '0.5';
  });
  btn.style.opacity = '1';
  btn.classList.add(isCorrect ? 'correct' : 'wrong');
  document.getElementById(
    quizId + (isCorrect ? '-correct' : '-wrong')
  ).classList.add('show');
}
```

### 配套练习开关 JS（所有课复用）

```javascript
(function() {
  const KEY = 'course-show-exercises';
  const toggle = document.getElementById('code-toggle');
  const section = document.getElementById('code-exercise');
  if (!toggle || !section) return;
  const saved = localStorage.getItem(KEY);
  let show = saved === null ? true : saved === '1';
  function apply() {
    toggle.classList.toggle('active', show);
    section.classList.toggle('hidden', !show);
  }
  apply();
  toggle.addEventListener('click', () => {
    show = !show;
    localStorage.setItem(KEY, show ? '1' : '0');
    apply();
  });
})();
```

---

## 代码练习模板（仅编程/理工科）

独立 `exercise.py` 文件，结构：

```python
"""
============================================================
第 N 课练习：<标题>
============================================================

<一句话描述学生将实现什么>

运行方式：  python exercise.py
完成所有 TODO 后，你应该看到所有测试通过

难度：⭐⭐ 或 ⭐⭐⭐
预计用时：20-45 分钟
"""

# ============================================================
# 🧱 Part 1: <子任务标题>
# ============================================================
#
# <概念说明 2-3 行>
#

def function_name(args) -> return_type:
    """Docstring with Args and Returns."""
    # ======== TODO 1: 在这里写你的代码 ========
    # 提示：<分步提示>

    pass  # ← 删掉这行，写你的实现

    # ======== END TODO 1 ========

# ... 重复 Part 2-5 ...

# ============================================================
# 🧪 测试
# ============================================================

def test_function_name():
    # 检查 None（未实现）→ 精确断言 → 打印 ✅/❌
    ...

if __name__ == "__main__":
    # 链式执行所有测试，最后打印总结
    all_passed = True
    all_passed = test_1() and all_passed
    # ...
    if all_passed:
        print("🎉 全部通过！")
    else:
        print("💪 还有测试没通过，继续加油！")
```

规范：
- 每课 4-5 个 TODO，难度递进
- 最后一个 TODO 串联前面所有函数
- 零外部依赖（纯 Python + math/random/json）
- 中文提示和 emoji 分隔
- 测试函数先检查 `result is None`（未实现提示）

---

## 思考练习 / 实操练习模板（嵌入 HTML）

非编程类课程的练习直接嵌入 `lesson.html` 的 `#code-exercise` section 内。

### 思考练习示例（人文/社科/商业）

```html
<section id="code-exercise">
  <h2><span class="num">N</span> 思考练习</h2>

  <div class="exercise-card">
    <h3>练习 1：案例分析</h3>
    <div class="exercise-scenario">
      <p>阅读以下情境，回答问题：</p>
      <div class="blockquote">（案例描述……）</div>
    </div>
    <div class="exercise-question">
      <p><strong>问题：</strong>如果你是决策者，你会选择方案 A 还是方案 B？请从以下三个维度分析……</p>
    </div>
    <div class="exercise-hints">
      <button class="hint-toggle" onclick="this.nextElementSibling.classList.toggle('show')">
        💡 查看思路提示
      </button>
      <div class="hint-content">（提示内容……）</div>
    </div>
  </div>
  <!-- 重复 2-3 个练习 -->
</section>
```

### 实操练习示例（语言学习）

```html
<section id="code-exercise">
  <h2><span class="num">N</span> 动手练习</h2>

  <div class="exercise-card">
    <h3>练习 1：填空</h3>
    <p>根据语境填入合适的词：</p>
    <div class="fill-blank">
      <span>她每天早上都会去公园</span>
      <input type="text" class="blank-input" data-answer="跑步" placeholder="___">
      <span>。</span>
      <button onclick="checkBlank(this)">检查</button>
      <span class="blank-feedback"></span>
    </div>
  </div>
  <!-- 重复 3-5 个练习 -->
</section>
```

---

## 非编程领域适配指引

不同学科在组件选择上有不同偏好：

| 学科类型 | 推荐组件 | 不太适用 |
|----------|---------|---------|
| 历史 | 时间轴、人物卡片网格、故事卡、地图示意 | Canvas 可视化 |
| 文学 | 引用块（原文赏析）、A/B 对比（译文比较）、故事卡 | 代码块 |
| 经济学 | Canvas 曲线图（供需曲线）、数据表格、概率条 | 对话模拟 |
| 心理学 | A/B 偏好选择（实验体验）、故事卡（案例）、流程图 | 热力图 |
| 编程 | 代码块、输入模拟器、步进动画、Canvas | 时间轴 |
| 数学/物理 | Canvas 可视化、步进动画（证明过程）、公式代码块 | 对话模拟 |
| 语言学习 | 填空/配对、对话模拟、A/B 选择（语法判断） | Canvas |
| 商业/产品 | 决策流程图、案例卡片、对比表、框架管线 | 步进动画 |

这些只是建议，Agent 可根据具体内容灵活调整。

---

## 延伸阅读 HTML 组件

### 课末汇总板块

```html
<section class="further-reading">
  <h2><span class="num">✦</span> 延伸阅读</h2>
  <p>如果你想更深入地理解本课涉及的概念，以下是一些优质资料：</p>
  <div class="reading-list">
    <div class="reading-item">
      <div class="reading-title">
        <a href="..." target="_blank" rel="noopener">资料标题</a>
      </div>
      <div class="reading-meta">来源 · 类型（文章/视频/书籍章节）</div>
      <div class="reading-desc">一句话推荐理由</div>
    </div>
    <!-- 重复 3-6 条 -->
  </div>
</section>
```

### 章节内联卡片

```html
<div class="further-reading-inline">
  <span class="fr-icon">📖</span>
  <span>想深入了解 X？→
    <a href="..." target="_blank" rel="noopener">《资料标题》</a>
    （来源，一句话推荐理由）
  </span>
</div>
```

### CSS（两套方案通用，颜色跟随 `--accent`）

```css
.further-reading { padding: 40px 0; }
.reading-list { display: flex; flex-direction: column; gap: 12px; margin-top: 16px; }
.reading-item {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 16px 20px;
}
.reading-title a {
  color: var(--accent); font-weight: 600; text-decoration: none;
  font-size: 15px;
}
.reading-title a:hover { text-decoration: underline; }
.reading-meta { font-size: 12px; color: var(--text-dim); margin-top: 4px; }
.reading-desc { font-size: 14px; color: var(--text-dim); margin-top: 6px; }

.further-reading-inline {
  display: flex; align-items: flex-start; gap: 8px;
  background: var(--surface2); border-radius: 8px;
  padding: 10px 14px; margin: 12px 0; font-size: 14px;
}
.further-reading-inline .fr-icon { flex-shrink: 0; }
.further-reading-inline a { color: var(--accent); font-weight: 600; }
```

### 搜索策略

- 课程主体内容完成后再搜索，不要边写边搜
- 每课做 2-3 次有针对性的 WebSearch
- 关键词模式：`"<核心概念> best tutorial/guide <当前年份>"` 或 `"<核心概念> 入门教程 推荐"`
- 只收录：链接可访问、匹配受众水平、质量公认优秀的资料
- 不贪多，每课 3-6 条

---

## 输出文件结构

```
<课程根目录>/
├── 01-<slug>/
│   ├── lesson.html
│   └── exercise.py        (仅编程/理工科)
├── 02-<slug>/
│   ├── lesson.html
│   └── exercise.py        (仅编程/理工科)
├── ...
└── NN-<slug>/
    └── lesson.html
```

- 目录名：两位数字 + 英文短横线 slug（如 `01-tokenization`、`03-supply-demand`）
- 默认存放路径：`互动课程/<课程主题>/`，用户指定其他路径则遵从

---

## 工作流 Checklist

生成每节课时，复制此清单逐项完成：

```
课程进度:
- [ ] 1. Phase 1 完成：确认主题、受众、课数、练习类型、存放路径
- [ ] 2. Phase 2 完成：大纲表格已获用户确认
- [ ] 3. 创建课程根目录

逐课生成（每课重复）:
- [ ] a. 确定本课的视觉方案（深色/浅色）和主题色
- [ ] b. 编写 lesson.html 主体内容（hero + 章节 + 交互 + 测验）
- [ ] c. 确保文字量充分——仅阅读文字也能理解全部概念
- [ ] d. 至少 1 个交互组件正常工作
- [ ] e. 3-4 道测验题，含正确/错误反馈
- [ ] f. WebSearch 2-3 次，收集延伸阅读资料
- [ ] g. 添加延伸阅读板块（课末 + 可选的章节内联）
- [ ] h. 如需配套练习：
        - 代码练习 → 生成 exercise.py（4-5 个 TODO + 测试）
        - 思考/实操练习 → 嵌入 HTML #code-exercise section
- [ ] i. 添加配套练习开关（如有练习）
- [ ] j. 添加 lesson-nav（确保在 #code-exercise 之外）
- [ ] k. 在浏览器中验证页面渲染正常

收尾:
- [ ] 4. 所有课生成完毕
- [ ] 5. 向用户汇报：目录结构 + 每课标题 + 如何打开浏览
```

---

## 反模式

- **不要**只有交互没有文字 → 文字讲解是骨架，交互是锦上添花
- **不要**把所有组件塞进一课 → 每课选 2-4 种最合适的组件
- **不要**给初学者推论文 / 给专家推入门帖 → 延伸阅读必须匹配受众
- **不要**编造延伸阅读链接 → 没搜到就不放，宁缺毋滥
- **不要**课与课之间视觉风格不一致 → 同一套课程共用相同的 `:root` 变量
- **不要**把 lesson-nav 放在 `#code-exercise` 内 → 否则关闭练习时导航也消失
- **不要**在搜索延伸阅读上花太多时间 → 主要精力放在课程内容本身
- **不要**一次性生成所有课 → 逐课生成，每课完成后让用户检查再继续
- **不要**把练习类型硬编码为代码练习 → 根据学科类型自动选择合适的练习形式
- **不要**忽略非编程学科的交互设计 → 人文类同样可以有丰富的交互（时间轴、A/B 选择、对话模拟等）
