(() => {
  const styleId = 'site-compliance-styles';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      :root { --site-compliance-height: 48px; }
      html {
        scroll-padding-bottom: calc(var(--site-compliance-height) + env(safe-area-inset-bottom));
      }
      body {
        padding-bottom: calc(var(--site-compliance-height) + env(safe-area-inset-bottom)) !important;
      }
      .site-compliance-bar {
        position: fixed !important;
        z-index: 2147483647 !important;
        right: 0 !important;
        bottom: 0 !important;
        left: 0 !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        transform: none !important;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100% !important;
        max-width: 100vw !important;
        min-height: var(--site-compliance-height);
        padding: 8px 20px calc(8px + env(safe-area-inset-bottom));
        box-sizing: border-box;
        overflow: visible !important;
        pointer-events: auto !important;
        color: #5f6673;
        border-top: 1px solid rgba(17, 24, 39, .12);
        background: rgba(251, 250, 247, .96);
        box-shadow: 0 -6px 24px rgba(17, 24, 39, .06);
        backdrop-filter: blur(12px);
        font-family: Inter, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
        font-size: 12px;
        line-height: 1.4;
        text-align: center;
      }
      .site-compliance-bar a {
        color: inherit;
        text-decoration: none;
      }
      .site-compliance-bar a:hover {
        color: #1557e8;
        text-decoration: underline;
      }
      .site-compliance-separator { color: rgba(17, 24, 39, .28); }
      .site-compliance-copy {
        min-width: 0;
        overflow-wrap: anywhere;
      }
      @media (max-width: 700px) {
        :root { --site-compliance-height: 68px; }
        .site-compliance-bar {
          display: grid !important;
          align-content: center;
          gap: 1px;
          padding: 8px 14px calc(8px + env(safe-area-inset-bottom));
        }
        .site-compliance-separator { display: none; }
      }
    `;
    document.head.appendChild(style);
  }

  let footer = document.querySelector('.site-compliance-bar, .icp-footer');
  if (!footer) {
    footer = document.createElement('footer');
    document.body.appendChild(footer);
  }

  footer.className = 'site-compliance-bar';
  footer.setAttribute('aria-label', '网站备案与服务说明');
  footer.innerHTML = `
    <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">沪ICP备2026035574号</a>
    <span class="site-compliance-separator" aria-hidden="true">·</span>
    <span class="site-compliance-copy">本网站仅提供静态课程内容，不提供生成式人工智能实时服务</span>
  `;
})();
