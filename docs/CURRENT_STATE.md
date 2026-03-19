# 当前实现与边界

> 状态：Current
> 更新时间：2026-03-19

## 1. 仓库当前定位

OhMyClaude 当前是一个 **以 Claude 为默认主线、同时支持多 harness 显式输出的本地安全 CLI**。

它已经实现的是：

- 预设驱动的配置安装
- 模板资产安装
- 显式 target bundle 渲染与安装
- provider 切换
- shell 初始化
- 备份/导入/导出
- Claude 配置健康检查

它还没有实现的是：

- Claude / Gemini 官方市场注册与发布流程
- Gemini 全局 `settings.json` 合并管理
- Cursor / OpenCode / 其他 harness 的完整安装层
- 多 harness 的隐式 home 目录写入

## 2. 代码地图

| 路径 | 作用 |
|------|------|
| `src/ohmyclaude/cli/main.py` | Click CLI 入口 |
| `src/ohmyclaude/core/config.py` | 读取预设、渲染模板、生成 `settings.json` |
| `src/ohmyclaude/core/installer.py` | 把设置与模板写入 Claude 目录 |
| `src/ohmyclaude/core/provider.py` | provider 切换与可选 Codex auth 同步 |
| `src/ohmyclaude/core/shell.py` | shell RC 注入与移除 |
| `src/ohmyclaude/core/backup.py` | 备份、恢复、列举归档 |
| `src/ohmyclaude/core/targets.py` | 多 target bundle 渲染、显式安装与路径解析 |
| `src/ohmyclaude/modules/mcp.py` | MCP package registry 与 server 解析 |
| `src/ohmyclaude/modules/provider.py` | 内建 provider 定义 |
| `templates/presets/*.yaml` | starter / standard / full 预设 |
| `templates/mcp/mcp_packages.yaml` | MCP 包和 bundle 定义 |

## 3. 模板资产现状

当前模板库存量：

- `commands/`: 7 个
- `agents-showcase/`: 10 个
- `skills/`: 12 组
- `hooks/`: 8 个脚本
- `claude_md/`: 3 个主要模板

这些模板仍以 **Claude Code 工作流资产** 为核心，但现在已经能组合成多个显式输出面。

## 4. 预设的真实行为

### starter

- 安装基础 `CLAUDE.md`
- 安装基础 `settings.json`
- 安装 3 个 commands
- 安装 2 个 agents
- 不安装 skill 模板
- 不安装 hook 脚本

### standard

- 在 starter 基础上增加更多 MCP 包与 commands
- 安装 5 个 agents
- hooks 主要以内联 JSON 配置为主，不复制 hook 脚本

### full

- 安装最完整的模板资产
- 复制 8 个 hook 脚本到 `~/.claude/hooks/`
- 安装 12 组 skills
- 同一批模板资产也可被渲染到 Codex / Gemini / Claude plugin bundle
- 这里描述的是默认 `claude-home` 输出面；portable bundle 会做额外的可移植性裁剪

## 5. 显式输出面

当前已支持的 target：

- `claude-home`
  - 生成 `settings.json`、`CLAUDE.md`、`commands/`、`hooks/`、`agents/`、`skills/`
- `claude-plugin`
  - 生成 `.claude-plugin/plugin.json` 与对应 bundle 目录
- `codex-project`
  - 生成 `AGENTS.md`、`.codex/config.toml`、`.codex/agents/`、`.agents/skills/`
- `gemini-extension`
  - 生成 `gemini-extension.json`、`GEMINI.md`、`commands/`、`hooks/`、`agents/`、`skills/`

这些输出都要求显式目标路径，不会在命令内部自动推导真实 home 目录。

其中 `claude-plugin` 和 `gemini-extension` 的 hooks 目前采用可移植子集策略：

- 优先保证 bundle 内路径自包含
- 不再依赖 `~/.claude` 或 `${OHMYCLAUDE_ROOT}`
- 暂时不追求与 `full` 预设在 `claude-home` 下完全等价

## 6. Codex 相关边界

仓库当前对 Codex 的支持有两层，必须区分：

### 兼容桥接层

`templates/mcp/mcp_packages.yaml` 里定义了 `codex` MCP 包，用于在 Claude 工作流里接入一个 Codex 兼容桥接服务。

这不是 Codex 官方原生能力本身。

### 当前代码里的真实副作用

`src/ohmyclaude/core/provider.py` 的 `ProviderSwitcher.switch()` 只会在以下条件满足时尝试更新 `~/.codex/auth.json`：

- 目标 provider 带 `openai_base_url`
- 显式传了 `--sync-codex-auth`
- 找得到可用 token

这意味着：

- 维护仓库时要避免直接运行会命中真实 home 目录的 provider 切换
- 默认情况下不会改 Codex 配置
- 用户若确实要改 Codex 配置，需要显式传 `--sync-codex-auth`

## 7. Gemini 相关边界

仓库当前已经支持 **Gemini extension bundle** 的生成 / 显式安装，但仍然不做 Gemini 全局配置管理。

如果文档提到 Gemini，只应把它视为：

- 显式输出目标
- 外部生态参考
- 仍保持安全边界的安装面

不能把它写成“默认会改你的 `~/.gemini`”。

## 8. 测试安全模型

现有测试的安全前提是：

- 对 `~/.claude` / `~/.codex` 的路径常量进行 patch
- 对 Gemini 相关路径常量进行 patch
- 在临时目录创建替身目录
- 不依赖真实用户配置

因此，当前推荐的验证方式是：

```bash
ruff check .
python -m mypy src/ohmyclaude
pytest
```

不要用真实主目录做手工 smoke test，除非你已经准备好备份和自动恢复机制。

## 9. 历史文档与现状的差异

`docs/` 下保留了大量 2024 年的设计文档。它们常见的问题包括：

- 描述了并不存在的模块路径
- 把参考仓库路径写成了本仓库的真实源码
- 把 SuperClaude / CodexMCP 的研究内容写成当前实现
- 规划了多 harness 输出，但旧文档比真实代码领先太多

因此，维护本仓库时请遵循：

- 对实现真相有疑问时，先读 `src/ohmyclaude/`
- 对功能边界有疑问时，先读 `README.md` 和本文
- 对生态方向有疑问时，读 `docs/ECOSYSTEM_RESEARCH_2026.md`
