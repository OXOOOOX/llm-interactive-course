# 主页的服务器自动部署

生产网站为 `https://sdspeed.com.cn`。将确认好的代码推送到本仓库 `main` 后，
GitHub Actions 同步确切提交的源码，腾讯云服务器检查课程链接、打包静态资源镜像，
验证成功后切换版本。电脑不需要常开。

迁移以原线上 `codex/ai-pm-course-zeabur` 分支的
`a81186a5e98940301c05c5b70bff1a8fec10ac63` 为基础；该提交是原 `main` 的后继，
此次将已上线的课程内容顺接到 `main`。之后生产更新以 `main` 为准。

## 网站与数据

这是静态课程网站，不运行 Node、npm、数据库或实时 AI 接口。服务器打包的内容
包括 HTML、CSS、JavaScript、图片、Markdown 和课程练习文件。
源码快照只包含 Git 跟踪的文件，不会上传本地未提交的 `artifacts/`。
打包后的公开目录还会排除部署工具、Git 元数据、环境文件等运维内容。

学习进度、笔记和练习状态保存在用户浏览器的 localStorage。保持原 HTTPS 域名和
同一浏览器资料，才能继续使用这些内容；程序回退不能恢复浏览器已删除的数据。
当前没有服务器业务数据库或持久化业务文件卷，因此发布不创建服务器业务数据备份。
已验证的程序镜像和版本源码用于代码回退。

现有首页 302 跳转、课程页面、无扩展名文档路径、目录首页及文档回退规则均保留。
缺失的 JS/CSS 等资源返回 404。`_headers` 和 `_redirects` 在打包时转换成独立的
Caddy 配置；不再依赖 Zeabur 扩展来处理它们。当前解析器支持的配置语法以
`site-package.py` 为准，新增规则前先运行检查。

原音乐课程第 1 课的“下一课”指向尚不存在的 `02-beethoven/lesson.html`。
迁移保留这处原有占位链接，并在检查结果中明确记录；其他新缺失链接和资源仍会阻断发布。

## GitHub 设置

| 类型 | 名称 |
|---|---|
| Variables | `HOMEPAGE_DEPLOY_ENABLED`、`HOMEPAGE_DEPLOY_HOST`、`HOMEPAGE_DEPLOY_PORT`、`HOMEPAGE_DEPLOY_USER` |
| Secrets | `HOMEPAGE_SSH_PRIVATE_KEY`、`HOMEPAGE_SSH_KNOWN_HOSTS` |

沿用现有服务器共用的 SSH 部署密钥，各仓库分别保存 Secret。
`HOMEPAGE_DEPLOY_ENABLED=true` 才会运行服务器部署任务。
`main` 推送会自动上线；手动运行工作流时默认 `activate=false`，只打包和检查，
勾选 `activate` 才上线。PR 只做无秘密的源码检查。

## 服务器目录和资源

| 内容 | 位置 |
|---|---|
| 项目根目录 | `/opt/homepage` |
| 当前、上一成功版本 | `/opt/homepage/current`、`/opt/homepage/previous` |
| 版本源码和构建记录 | `/opt/homepage/releases/<完整 Git SHA>` |
| 私有运行配置 | `/opt/homepage/shared/runtime.env`，root 所有、权限 600 |
| 固定运行环境记录 | `/opt/homepage/shared/runtime-image.json` |
| 最近发布结果 | `/opt/homepage/shared/last-release.json` |
| 发布日志 | 对应版本目录下的 `activation.log` |
| 本机访问入口 | `127.0.0.1:4200`，转发到容器 `8080` |

共享 Caddy 网关 `/opt/site-gateway/Caddyfile` 负责公网域名与 HTTPS。
正常代码发布不改 DNS 或共享网关。站点运行环境沿用 Caddy 2.11.4，基础镜像
保存在服务器并固定镜像 ID，不需要每次从 Zeabur 下载。

构建与其他项目使用同一组锁，限制为 1 个 CPU、512 MiB 内存；运行容器为
0.5 个 CPU、128 MiB 内存，根文件系统只读。临时配置目录不保存业务数据。
开始构建时要求空闲磁盘超过 5 GiB、可用内存超过 512 MiB。
运行配方发生变化时，需要先审查并更新固定运行环境记录，不能直接绕过校验。

## 设置变量和修改课程

课程内容、跳转和响应头应修改仓库中的文件后提交发布。
当前页面没有服务端业务变量；`runtime.env` 不会被插入 HTML 或 JavaScript。
不要把密码或 API Key 写进网页、GitHub 源码或公开的 `_headers`。
未来若新增登录、数据库、上传或后端 API，先规划数据持久化和迁移，再扩展部署流程。

## 检查和回退

在本地仓库运行：

```sh
python deploy/site-package.py check .
python -B deploy/test-site-package.py
python -B deploy/test-release.py
```

服务器每次发布会检查专用健康响应、根路径 302、响应头和网站文件内容哈希，
不访问外部视频、缩略图或参考资料链接。访问这些第三方资源是否正常需另行确认。
`/api/health`、`/healthz` 可能回退为 HTML，不能只看它们的 200 状态判断健康。

```sh
curl -fsS https://sdspeed.com.cn/__deploy_health
# 必须返回 HOME_OK
```

回退上一成功版本，在 SSH 终端执行：

```sh
sudo -n bash /opt/homepage/previous/deploy.sh /opt/homepage/previous
```

这会短暂重启主页服务并重新校验站点。两个版本都须保留有效镜像和构建记录；
回退不清空浏览器学习进度，也不会撤回手动修改的运行配置。
