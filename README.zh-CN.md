# OhMyClaude

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![CLI](https://img.shields.io/badge/interface-CLI-black)
![Claude First](https://img.shields.io/badge/focus-Claude%20First-6f42c1)
![Codex Aware](https://img.shields.io/badge/focus-Codex%20Aware-0a7ea4)
![Local Safe](https://img.shields.io/badge/testing-local%20safe-2ea44f)

**Language:** [English](README.md) | 简体中文 | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

**一个以 Claude 为默认主线、同时支持多 harness 显式输出的本地安全 CLI。**

OhMyClaude 用来帮你快速落地一套实用的 Claude Code 工作流：生成 `settings.json`、生成 `CLAUDE.md`、安装 commands / hooks / agents / skills 模板、切换 provider、初始化 shell 集成，并对配置变更做备份与恢复。

它现在采用分阶段定位：

- **Claude-first**：默认安装主线仍然是 Claude Code
- **Multi-harness**：已经支持显式渲染 / 安装 `claude-home`、`claude-plugin`、`codex-project`、`gemini-extension` bundle
- **Local-safe**：仓库开发与测试默认不碰你真实的 `~/.claude`、`~/.codex`、Gemini CLI 配置

## 为什么选择 OhMyClaude

很多 Claude Code 配置仓库有两个常见问题：

- 要么太轻，只给零散片段
- 要么太重，长成一个多 harness 大框架，结果代码和公开文档脱节

OhMyClaude 想做的是中间地带：

- 用一个聚焦的 Python CLI 安装一组清晰、够用的 Claude 资产
- 对 Codex 生态保持感知，但不盲目扩张边界
- 把公开仓库内容和本地 AI 维护资料明确分层

## 亮点

| Area | What You Get |
|------|--------------|
| Claude setup | 生成 `~/.claude/settings.json`、`~/.claude/CLAUDE.md`、commands、hooks、agents、skills |
| Multi-harness bundles | 可显式渲染或安装 `.claude-plugin/`、`.codex/`、`.agents/skills/`、Gemini extension bundle |
| Workflow assets | 安装 `9` 个 commands、`11` 个 agents、`16` 个 skills、`8` 个 hook 脚本模板 |
| Curated phase 2 | 新增 `coding-standards`、`tdd-workflow`、`e2e-testing`、`worktree-isolation` 与独立的 `security-reviewer` |
| MCP bundles | 通过 `templates/mcp/mcp_packages.yaml` 组合 MCP 包和 bundle |
| Provider switching | 切换官方 / 第三方 / 自定义 provider，并把 Codex auth 同步改成显式 opt-in |
| Shell integration | 通过 `omc init` 注入或移除 shell 初始化块 |
| Config safety | `doctor`、`render`、`install`、`export`、`import`、备份与恢复 |
| Codex / Gemini awareness | 区分 Claude 侧 Codex bridge、原生 Codex 项目资产和 Gemini extension 输出 |

## 当前已实现

当前已经实现的能力：

- 安装 Claude Code 配置与模板
- 通过预设生成 `mcpServers` 与 hooks 配置
- 安装 commands / hooks / agents / skills 模板
- 渲染显式 target bundle：`claude-home`、`claude-plugin`、`codex-project`、`gemini-extension`
- 管理 API provider
- 只在显式请求时同步 OpenAI-compatible 的 Codex 认证文件
- 运行健康检查、shell 初始化、导入导出和更新检查

## 当前不做的事

当前不做的事：

- 不做托管式插件市场或注册服务
- 不自动帮你把生成的 bundle 注册到 Claude Code / Gemini CLI
- 不在仓库维护过程中隐式改写真实 `~/.codex` 或 `~/.gemini`
- 当前阶段不做 Gemini 全局 `settings.json` 合并管理

## 这里的 “Codex-aware” 是什么意思

OhMyClaude 里提到的 Codex 有两层，必须区分：

### 1. Claude 内部的兼容桥接

预设里的 `codex` MCP 包表示 **Claude 工作流里的 Codex bridge 路径**。

它适合：

- 在 Claude 会话里请求 Codex 做分析、review、原型辅助
- 保持现有 Claude-first 的工作流结构

它不等于：

- Codex 官方原生的 `AGENTS.md`
- Codex 官方原生 skills
- Codex 官方原生 `.codex/config.toml`

### 2. 原生 Codex 能力

原生 Codex 支持 `AGENTS.md`、skills、`.codex/config.toml`、subagents 等官方能力。

本仓库现在已经支持把这些能力渲染或安装到**显式目标目录**，但不会在 `setup` 或仓库维护流程里隐式写你的真实 `~/.codex`。

## 安全模型

如果你只是想维护本仓库，而不想误改自己的真实工具配置，请遵循下面的做法：

- 测试 provider 切换时直接用 `omc switch <provider>`；只有传 `--sync-codex-auth` 才会动 Codex
- 测试安装逻辑时只使用仓库现有测试，它们会把路径 patch 到临时目录
- 不直接对真实 `~/.claude`、`~/.codex`、Gemini 目录做手工 smoke test
- 优先用 `omc render` 和显式 `omc install --dest ... --confirm` 在临时目录里验收
- `omc render` 默认会拒绝写入真实 harness home 目录
- `setup` 现在会保留已存在的同名 skills 和 `skill-rules.json`，不会静默覆盖用户自定义内容

## Installation

### `pip`

```bash
pip install ohmyclaude
```

### `pipx`

```bash
pipx install ohmyclaude
```

### From Source

```bash
git clone https://github.com/Boulea7/ohmyclaude.git
cd ohmyclaude
pip install -e .
```

## Quick Start

```bash
# 1. 安装一个预设
omc setup --preset standard

# 2. 渲染一个 Codex 项目 bundle，不碰真实 home
omc render --target codex-project --output ./.tmp/codex-project

# 3. 安装一个 Gemini extension bundle 到显式目录
omc install --target gemini-extension --preset standard --dest ./.tmp/gemini-extension --confirm

# 4. 检查 Claude 配置状态
omc doctor

# 5. 查看 shell 注入状态
omc init --status

# 6. 安全地切换 provider，默认不改 Codex 配置
omc switch glm
```

## Commands

| Command | Purpose |
|---------|---------|
| `omc setup` | 安装 `starter`、`standard`、`full` 预设 |
| `omc doctor` | 检查 Claude home、plugin bundle、Codex project bundle 或 Gemini extension bundle |
| `omc init` | 写入或移除 shell 初始化块 |
| `omc render --target <target>` | 将目标 bundle 渲染到显式输出目录 |
| `omc install --target <target>` | 将目标 bundle 安装到显式目录，并要求确认 |
| `omc switch <provider>` | 切换 API provider |
| `omc switch --list` | 列出可用 provider |
| `omc provider list/show/add/remove` | 管理自定义 provider |
| `omc export <file>` | 导出当前 Claude 配置 |
| `omc import <file>` | 从归档恢复配置 |
| `omc update` | 检查包更新 |

## Preset Comparison

| Preset | Positioning | Current Shape |
|--------|-------------|---------------|
| `starter` | 最小可用配置 | `basic` MCP、3 个 commands、2 个 agents、无 skill 安装 |
| `standard` | 日常开发推荐 | `basic + reasoning + code + codex`、5 个 commands、6 个 agents、2 个精选 skills、inline hooks |
| `full` | 最完整的 Claude 资产集 | 7 个基础 MCP 组、3 个 optional MCP 组、9 个 commands、11 个 agents、16 个 skills、8 个 hook 脚本 |

补充说明：

- 这张表描述的是默认 `claude-home` 输出面
- `standard` 现在默认带一组轻量精选资产：`coding-standards`、`tdd-workflow`、`/tdd` 和 `security-reviewer`
- `full` 进一步加入浏览器测试与隔离工作流资产，例如 `e2e-testing`、`worktree-isolation` 与 `/worktree`
- `standard` 和 `full` 里的 `codex` 仍然是 **Claude 侧 bridge**
- 它不等于原生 Codex 安装能力
- 公开文案已经改用更现代的 Claude / Codex 术语，但运行行为仍以当前代码实现为准

## Target 输出面

当前支持的显式输出面：

| Target | 输出形态 | 典型用途 |
|--------|----------|----------|
| `claude-home` | `settings.json`、`CLAUDE.md`、`commands/`、`hooks/`、`agents/`、`skills/` | 安装到临时 Claude 目录或显式替代目录 |
| `claude-plugin` | `.claude-plugin/plugin.json` + `commands/`、`hooks/`、`agents/`、`skills/` | 生成可分享的 Claude plugin bundle |
| `codex-project` | `AGENTS.md`、`.codex/config.toml`、`.codex/agents/`、`.agents/skills/` | 为项目生成原生 Codex 层 |
| `gemini-extension` | `gemini-extension.json`、`GEMINI.md`、`commands/`、`hooks/`、`agents/`、`skills/` | 生成 Gemini CLI extension bundle |

如果输出不在默认位置，记得用 `omc doctor --target <target> --path <root>`
指定 bundle 根目录；否则 CLI 会回退到 `cwd` 或 `~/.claude` 做检查。

当前 plugin / Gemini 的 portable hooks 是一组“可移植子集”：
它们已经去掉了对 `OHMYCLAUDE_ROOT` 的直接依赖，并会优先解析 bundle-local 资源；但仍保留部分 Claude 导向的 fallback，暂时也不会与 `full` 预设在 Claude home 下的 hook 行为完全一一对应。

## Repository Layout

```text
src/ohmyclaude/
├── cli/            # Click CLI 入口
├── core/           # 安装、配置、provider、shell、backup
├── models/         # Pydantic 模型
├── modules/        # MCP 与 provider 定义
├── templates/      # CLAUDE.md / commands / hooks / agents / skills 模板
└── ui/             # 基于 Rich 的 CLI 展示辅助

templates/
├── presets/        # starter / standard / full YAML
└── mcp/            # MCP package registry

tests/
├── unit/
└── integration/
```

## 公开内容与本地私有资料

这个仓库明确区分 **公开 GitHub 内容** 和 **本地 AI 私有资料**。

### Public

公开层主要包括：

- `README.md`
- `README.zh-CN.md`
- `README.zh-TW.md`
- `README.ja.md`
- `docs/`
- 已跟踪的维护文档，例如 `AGENTS.md`、`CLAUDE.md`
- `src/`
- `templates/`
- `tests/`
- `CHANGELOG.md`、`SECURITY.md`、`CONTRIBUTING.md`、`RELEASE_GUIDE.md`

### Local

本地私有资料应放在被忽略的路径中，例如：

- `.ai-notes/`
- 机器相关的临时索引、scratch 文件
- 任何不适合进入 Git 历史的 AI 工作笔记

这样可以把真正私有的工作上下文留在忽略路径里，同时允许仓库把经过整理的公开维护文档保留在版本控制中。

## 常见问题

### 这个项目会自动帮我配置原生 Codex 吗？

现在可以把项目级 Codex 资产渲染或安装到显式目录里，但不会在普通维护流程中自动写你的真实 `~/.codex`。

### `switch` 会不会改我的 Codex 配置？

只有你显式传了 `--sync-codex-auth` 才会。

### 为什么本地 AI 资料不公开？

因为研究笔记、索引文件、AI 工作上下文在本地很有用，但会让公开仓库更嘈杂、可移植性更差，也更容易泄露隐私信息。

### 这是一个多 harness 配置平台吗？

是，但还处在第一阶段：重点是显式 bundle 输出和安全安装，而不是对所有 harness 做隐式 home 目录写入。

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# Ruff
ruff check .

# MyPy
python -m mypy src/ohmyclaude

# Pytest
pytest
```

## 路线图

当前更现实的下一阶段是：

- 继续增强 Claude plugin 和 Gemini extension 的 target-specific 验证
- 在不把 CLI 做成重运行时框架的前提下，补一层轻量 install-state 与 troubleshooting 支撑
- 继续扩充精选共享 skill / agent 资产，同时控制默认预设的膨胀速度
- 补齐更多 target-aware 的 doctor 检查和 troubleshooting 文档
- 在保持 local-safe 前提下继续扩展多 harness 支持

## Acknowledgements

- [obra/superpowers](https://github.com/obra/superpowers) — 强工作流约束、设计先行、技能驱动
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 分层 rules / skills / hooks / troubleshooting 组织方式
- [Claude Code Docs](https://code.claude.com/docs/en) — 当前官方 hooks、plugins、memory、subagents 能力
- [OpenAI Codex Docs](https://developers.openai.com/codex/) — 当前官方 `AGENTS.md`、skills、subagents、config 能力
- [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) — 当前 Gemini CLI 的 extension、commands、skills、context 模式
