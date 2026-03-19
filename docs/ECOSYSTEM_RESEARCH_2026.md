# 2026 生态调研与维护结论

> 状态：Current
> 更新时间：2026-03-20

## 1. 调研目标

这份文档回答三个问题：

- 2026 年更成熟的 Claude / Codex 仓库都在怎么组织资产
- 官方文档已经确认了哪些原生能力
- 这些变化对 OhMyClaude 的仓库维护意味着什么

## 2. 主要参考来源

### 社区仓库

- `obra/superpowers`
  - GitHub: <https://github.com/obra/superpowers>
- `affaan-m/everything-claude-code`
  - GitHub: <https://github.com/affaan-m/everything-claude-code>

### Claude Code 官方文档

- Hooks: <https://code.claude.com/docs/en/hooks>
- Plugins reference: <https://code.claude.com/docs/en/plugins-reference>
- Memory / CLAUDE.md / rules: <https://code.claude.com/docs/en/memory>
- Subagents: <https://code.claude.com/docs/en/sub-agents>
- Slash commands: <https://code.claude.com/docs/en/slash-commands>

### OpenAI Codex 官方文档

- AGENTS.md: <https://developers.openai.com/codex/guides/agents-md>
- Config reference: <https://developers.openai.com/codex/config-reference>
- Skills: <https://developers.openai.com/codex/skills>
- Subagents: <https://developers.openai.com/codex/subagents>

## 3. 从 superpowers 借鉴什么

`superpowers` 最有价值的不是“模板数量”，而是 **强约束工作流**。

值得借鉴的点：

- 先设计、后计划、再执行，不让 agent 直接跳进编码
- 把 workflow 写成 skills，而不是只靠一份超长全局说明
- 对复杂工作使用明确的 handoff，例如 brainstorming → writing-plans → execution
- 对 Codex 使用原生 skill 发现机制，而不是默认假设需要桥接协议

不宜直接照搬的点：

- 对所有任务都强制完整 spec gate 的方法论过于重
- 当前 OhMyClaude 是配置 CLI，不是 workflow-first agent framework
- 仓库还没有原生 worktree / plan executor / subagent orchestrator 的产品层实现

## 4. 从 everything-claude-code 借鉴什么

`everything-claude-code` 的优势是 **资产组织和跨 harness 文档方法**。

值得借鉴的点：

- `rules / skills / hooks / agents / commands / troubleshooting` 分层清晰
- 对 Codex 采用原生 `.codex/config.toml`、`.codex/AGENTS.md`、`.agents/skills` 叙事
- 为 hooks、rules、skills、Codex 支持分别写独立说明，而不是塞进一个 README
- 大量加入 troubleshooting 和边界说明，减少用户误用

不宜直接照搬的点：

- 其产品已经是多 harness 大型资产库，表面积远大于 OhMyClaude
- 当前 OhMyClaude 没有插件打包、跨平台 hook 适配、Cursor/OpenCode 输出层
- 直接复制其目录规模会让本仓库“文档像大产品，代码像小工具”

## 5. Claude Code 官方文档带来的结论

根据 Claude Code 官方文档，以下能力已经是当前正式语境的一部分：

- `CLAUDE.md` 是项目级持久指令文件，官方还支持 `.claude/rules/` 做更细粒度拆分
- `/init` 会帮助生成起始 `CLAUDE.md`
- hooks 不再只是简单脚本触发，而是完整的生命周期系统，支持 command / http / prompt / agent 四类 handler
- plugins 已经是正式的一等机制，可打包 skills、agents、hooks、MCP、LSP
- skills 和 commands 在插件中都能被自动发现
- subagents 有正式的创建与管理方式，支持项目级和用户级目录

对 OhMyClaude 的影响：

- 文档不能再把 skills 当成“外挂技巧”，而应当视作 Claude 生态里的正式扩展层
- 文档不能继续把 commands 当成唯一推荐扩展方式
- hooks/agents 的写法应尽量贴近官方术语，而不是历史自创术语

## 6. Codex 官方文档带来的结论

根据 Codex 官方文档，以下能力已经是当前正式语境的一部分：

- `AGENTS.md` 是 Codex 的项目与用户级指导文件
- `~/.codex/config.toml` 与项目级 `.codex/config.toml` 是标准配置入口
- `approval_policy`、`sandbox_mode`、`web_search` 都是官方配置项
- Codex 有原生 skills，支持从仓库级 `.agents/skills` 与用户级 `$HOME/.agents/skills` 自动发现
- Codex skills 支持 symlink 目录
- Codex 已有 subagents，且部分批处理工作流仍标为 experimental

对 OhMyClaude 的影响：

- 不应再把 “Codex = 只能通过 CodexMCP 桥接来协作” 写成默认前提
- 文档层应该把“原生 Codex”和“Claude 内部的 Codex bridge”分开
- 如果后续扩展 Codex 支持，应优先从 reference-only 资产做起，而不是先改 CLI 自动写用户目录

## 7. 对 OhMyClaude 的仓库决策

基于以上调研，本仓库当前维护策略是：

### 保留

- 继续保留 Claude Code 配置 CLI 的产品主线
- 继续保留现有 commands / hooks / agents / skills 模板资产
- 继续保留 provider 切换与 backup / doctor / init 等工具能力
- 继续把默认安装主线放在 Claude Code

### 调整

- 文档统一改成 **Claude-first, Codex-aware**
- 产品叙事升级成 **Claude-first, multi-harness, local-safe**
- 历史 SuperClaude / CodexMCP 叙事降级为历史参考，不再当作现行架构
- README 与模板说明统一强调：
  - 当前实现有多个显式输出面
  - 默认不写真实 home 目录
  - Codex / Gemini 支持优先落到 bundle 输出而不是隐式同步

### 已落地的第一阶段

- `render` / `install` 显式目标路径写入
- `claude-home` / `claude-plugin` / `codex-project` / `gemini-extension` 四类 target
- `switch` 改成默认不触碰 Codex，只有显式 opt-in 才同步
- 可移植技能资产扩充为更适合 Codex / Gemini 输出的通用集合

### 已落地的第二阶段（精选内容吸收）

- 从外部生态中只吸收 **高复用、低状态、跨 harness 易解释** 的工程资产
- 新增精选 skills：`coding-standards`、`tdd-workflow`、`e2e-testing`、`worktree-isolation`
- 新增精选 agent：`security-reviewer`
- 新增 workflow commands：`/tdd`、`/worktree`
- 把 `coding-standards`、`tdd-workflow` 纳入 portable baseline，使 `codex-project` 与 `gemini-extension` 拿到更稳的通用技能层
- 修正 `skill-rules.json` 的实际落地链路，让 `full` preset 的 skill auto-activation 不再停留在文档层

### 暂不做

- 暂不做多 harness 的隐式 home 目录安装
- 暂不做 Gemini 全局配置合并
- 暂不把所有参考仓库的资产规模直接照搬进来
- 暂不引入 continuous learning / instinct 系统、多模型 control plane、PM2/loop/autopilot 等重型运行时能力

## 8. 后续维护建议

- 继续优先更新现行文档与模板，而不是继续扩写旧架构草案
- 优先加强 target-aware 验证和 troubleshooting，再扩资产数量
- 如果未来要增强 Gemini 支持，优先补 extension 级 hooks / commands / agents 兼容验证
- 如果未来要支持更深的原生 Codex，优先补项目级 `.codex` / `.agents/skills` 质量，而不是增加全局隐式写入
