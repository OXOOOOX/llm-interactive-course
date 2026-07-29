(() => {
  const ROOT = 'ai-pm-course';
  const lessonId = document.body.dataset.lesson || '01';

  const ensureComplianceBar = () => {
    let footer = document.querySelector('.site-compliance-bar, .icp-footer');
    if (!footer) {
      footer = document.createElement('footer');
      document.body.appendChild(footer);
    }
    footer.className = 'site-compliance-bar';
    footer.setAttribute('aria-label', '网站备案与服务说明');
    footer.innerHTML = `
      <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">沪ICP备2026035574号</a>
      <span aria-hidden="true">·</span>
      <span>本网站仅提供静态课程内容，不提供生成式人工智能实时服务</span>
    `;
    Object.assign(footer.style, {
      position: 'fixed',
      zIndex: '2147483647',
      right: '0',
      bottom: '0',
      left: '0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexWrap: 'wrap',
      gap: '4px 8px',
      width: '100%',
      minHeight: '48px',
      padding: '8px 14px',
      boxSizing: 'border-box',
      color: '#5f6673',
      borderTop: '1px solid rgba(17, 24, 39, .12)',
      background: 'rgba(251, 250, 247, .96)',
      boxShadow: '0 -6px 24px rgba(17, 24, 39, .06)',
      fontSize: '12px',
      lineHeight: '1.4',
      textAlign: 'center',
      visibility: 'visible',
      opacity: '1',
    });
    const link = footer.querySelector('a');
    if (link) {
      link.style.color = 'inherit';
      link.style.textDecoration = 'none';
    }
    document.body.style.setProperty('padding-bottom', '68px', 'important');
  };
  ensureComplianceBar();

  const parse = (key, fallback) => {
    try {
      return JSON.parse(localStorage.getItem(`${ROOT}:${key}`)) ?? fallback;
    } catch {
      return fallback;
    }
  };

  const completed = new Set(parse('completed', []));
  document.querySelectorAll('.lesson-link').forEach((link) => {
    const id = link.dataset.lesson;
    link.classList.toggle('completed', completed.has(id) && id !== lessonId);
  });

  const note = document.querySelector('[data-note]');
  const count = document.querySelector('[data-note-count]');
  if (note) {
    if (!note.closest('.note-editor')) {
      const editor = document.createElement('div');
      editor.className = 'note-editor';
      const toolbar = document.createElement('div');
      toolbar.className = 'note-toolbar';
      toolbar.setAttribute('aria-label', '笔记格式工具');
      toolbar.innerHTML = `
        <button type="button" data-note-wrap="**" aria-label="加粗"><strong>B</strong></button>
        <button type="button" data-note-wrap="_" aria-label="斜体"><em>I</em></button>
        <span class="toolbar-divider" aria-hidden="true"></span>
        <button type="button" data-note-prefix="• " aria-label="项目符号">☷</button>
        <button type="button" data-note-prefix="1. " aria-label="编号列表">1.</button>
      `;
      note.parentNode.insertBefore(editor, note);
      editor.append(toolbar, note);
      toolbar.addEventListener('click', (event) => {
        const button = event.target.closest('button');
        if (!button) return;
        const start = note.selectionStart;
        const end = note.selectionEnd;
        const selected = note.value.slice(start, end);
        const wrap = button.dataset.noteWrap;
        const prefix = button.dataset.notePrefix;
        const insert = wrap ? `${wrap}${selected || '重点'}${wrap}` : `${prefix}${selected}`;
        note.setRangeText(insert, start, end, 'end');
        note.dispatchEvent(new Event('input', { bubbles: true }));
        note.focus();
      });
    }
    const key = `${ROOT}:note:${lessonId}`;
    note.value = localStorage.getItem(key) || '';
    const updateCount = () => {
      if (count) count.textContent = `${note.value.length} / 800`;
      localStorage.setItem(key, note.value.slice(0, 800));
    };
    note.addEventListener('input', updateCount);
    updateCount();
  }

  document.querySelectorAll('[data-save-note]').forEach((button) => {
    button.addEventListener('click', () => {
      if (note) localStorage.setItem(`${ROOT}:note:${lessonId}`, note.value.slice(0, 800));
      button.textContent = '已保存 ✓';
      completed.add(lessonId);
      localStorage.setItem(`${ROOT}:completed`, JSON.stringify([...completed]));
      setTimeout(() => { button.textContent = '保存我的答案'; }, 1400);
    });
  });

  document.querySelectorAll('[data-choice-group]').forEach((group) => {
    const feedback = group.querySelector('.feedback');
    group.querySelectorAll('.option').forEach((option) => {
      option.addEventListener('click', () => {
        group.querySelectorAll('.option').forEach((node) => {
          node.classList.remove('selected', 'correct', 'wrong');
        });
        const correct = option.dataset.correct === 'true';
        option.classList.add('selected', correct ? 'correct' : 'wrong');
        if (feedback) {
          feedback.classList.add('show');
          feedback.classList.toggle('success', correct);
          const title = feedback.querySelector('strong');
          const copy = feedback.querySelector('span:last-child');
          if (title) title.textContent = correct ? (option.dataset.success || '判断得很好') : (option.dataset.retry || '再想一步');
          if (copy) copy.textContent = correct
            ? (option.dataset.successCopy || '这个方向兼顾了用户价值、可落地性与验证速度。')
            : (option.dataset.retryCopy || '先回到用户任务，看看这个方案是否真的改善了关键结果。');
        }
      });
    });
  });

  document.querySelectorAll('.quiz-option').forEach((option) => {
    option.addEventListener('click', () => {
      const quiz = option.closest('.quiz');
      if (!quiz || quiz.dataset.answered === 'true') return;
      quiz.dataset.answered = 'true';
      const correct = option.dataset.correct === 'true';
      option.classList.add(correct ? 'correct' : 'wrong');
      const result = quiz.querySelector(correct ? '.quiz-correct' : '.quiz-wrong');
      if (result) result.classList.add('show');
      quiz.querySelectorAll('.quiz-option').forEach((node) => {
        node.disabled = true;
      });
    });
  });

  document.querySelectorAll('[data-hint-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const content = button.nextElementSibling;
      if (!content) return;
      const show = !content.classList.contains('show');
      content.classList.toggle('show', show);
      button.setAttribute('aria-expanded', String(show));
    });
  });

  const exerciseToggle = document.querySelector('[data-exercise-toggle]');
  const exerciseSection = document.querySelector('#code-exercise');
  if (exerciseToggle && exerciseSection) {
    const key = `${ROOT}:show-exercises`;
    let show = localStorage.getItem(key) !== '0';
    const apply = () => {
      exerciseSection.classList.toggle('exercise-hidden', !show);
      exerciseToggle.textContent = show ? '隐藏思考练习' : '显示思考练习';
      exerciseToggle.setAttribute('aria-pressed', String(show));
    };
    exerciseToggle.addEventListener('click', () => {
      show = !show;
      localStorage.setItem(key, show ? '1' : '0');
      apply();
    });
    apply();
  }

  document.querySelectorAll('[data-sortable]').forEach((list) => {
    list.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-move]');
      if (!button) return;
      const item = button.closest('.sort-item');
      if (!item) return;
      const direction = button.dataset.move;
      const sibling = direction === 'up' ? item.previousElementSibling : item.nextElementSibling;
      if (!sibling) return;
      if (direction === 'up') list.insertBefore(item, sibling);
      else list.insertBefore(sibling, item);
      [...list.children].forEach((node, index) => {
        const badge = node.querySelector('.sort-index');
        if (badge) badge.textContent = String(index + 1);
      });
    });
  });

  const dialog = document.querySelector('#course-map');
  const moveComplianceIntoDialog = () => {
    const complianceBar = document.querySelector('.site-compliance-bar');
    if (dialog?.open && complianceBar) dialog.appendChild(complianceBar);
  };
  const restoreComplianceToPage = () => {
    const complianceBar = dialog?.querySelector('.site-compliance-bar');
    if (complianceBar) document.body.appendChild(complianceBar);
  };
  document.querySelectorAll('[data-open-map]').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      if (dialog?.showModal) {
        dialog.showModal();
        moveComplianceIntoDialog();
      }
    });
  });
  document.querySelectorAll('[data-close-map]').forEach((button) => {
    button.addEventListener('click', () => dialog?.close());
  });
  dialog?.addEventListener('close', restoreComplianceToPage);

  document.querySelectorAll('[data-start-challenge]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelector('.learning-section:nth-of-type(2)')?.scrollIntoView({ behavior: 'smooth' });
    });
  });

})();
