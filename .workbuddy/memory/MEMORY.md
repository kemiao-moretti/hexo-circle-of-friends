# MEMORY.md — hexo-circle-of-friends 项目长期事实

## 项目性质
- 这是 **hexo-circle-of-friends（友链朋友圈）** 的副本，v6.0.6（Rust + Python 重写版）。
- 本地 `css_rules.yaml` 改动前与上游 `Rock-Candy-Tea/hexo-circle-of-friends@main` **逐字节一致**。
- 本仓库 remote：`kemiao-moretti/hexo-circle-of-friends`。
- 上游活跃度（2026-09-13 查）：最后提交 2026-06-22，未归档，304 stars，节奏慢。

## 用户博客（喵洛阁）
- 部署仓库：`kemiao-moretti/meowloge`，站点 `https://blog.518339.xyz/`，CF Pages + Hugo 0.166。
- 主题：`kemiao-moretti/blog` 的 solitude **fork**（不跟随 `everfu/hugo-solitude`），已含 tombstone 自定义。
- 友链页：`/links/`，`content/links/_index.md` → `type: links`；数据在 `data/links.yaml`。
- 友链数据分组：`网上邻居`（type: item，活站）+ `友链墓碑`（type: lost，只渲染 `tombstone-*`）。
- 已存在 Workflow：`.github/workflows/fcircle.yml` + `.github/scripts/gen_fcircle.py` → 由 `data/links.yaml` 生成 `static/fcircle.json`（`[name, link, linkpage, avatar]`）。

## 本次完成（2026-09-13）
- 新增 `link_page_rules.hugo-solitude`，插在 `stellar` 之后、`anzhiyu` 之前。
- `fc_settings.yaml`：`LINK` 首次启用，指向 `https://blog.518339.xyz/links/`，theme=`hugo-solitude`。
- 新增 `tools/verify_css_rules.py`（CSS 规则实测校验脚本）。

## 关键结论（可复用）
- Hugo Solitude 友链页在 `item` 与 `card` 两种模式下**都用** `.cf-friends-name` / `a.cf-friends-link` / `.cf-friends-avatar` 三件套 → 等同 `common2` 但带兜底。
- **陷阱**：`card` 模式里第一个 `<a class="img">` 的 `img` 是 `topimg` 封面图、**没有** `cf-friends-avatar` 类；必须限定 `.cf-friends-avatar` 才能取到真头像。
- **陷阱**：项目模式下站点名也在 `<a title>` 上，若用 `text` 选择器命中 `<a>` 会取到空 → `author` 用 `.cf-friends-name` 取 `text`。
- `type: lost` 墓碑分组**不会被**抓取（无 `cf-friends-*` 类）——这是期望行为。
- 与 Hexo 版 `hexo-theme-solitude` 的友链页 HTML 结构不同，theme 名不可混用。

## 约定 / 偏好
- 不允许对 `css_rules.yaml` 做全文件 reformat（会污染与上游的 diff）。
- 新增条目风格跟随现状：`selector` 与 `attr` 的值都带双引号。
- YAML flow-mapping 中含 `&` 的 URL（如 favicon 服务）必须加双引号。
