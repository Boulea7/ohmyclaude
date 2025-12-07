# OhMyClaude 实施计划

> 版本: 1.3.0
> 更新日期: 2024-12 (整合 SuperClaude 核心模式 + claude-code-infrastructure-showcase 精华)

---

## 1. 项目概览

### 1.1 项目目标

构建一个面向中国用户的 Claude Code 一键配置工具，实现：
- 5 分钟内完成完整配置
- 支持预设包 + 自定义微调
- 安全的凭证管理 (Keyring)
- 可选 CodexMCP 协作集成

### 1.2 里程碑规划 (已更新)

```
Phase 1 ──────► Phase 1.5 ────► Phase 2 ──────► Phase 2.5 ────► Phase 2.6 ────► Phase 3
核心框架        核心工具         基础配置        模板资源整合      SuperClaude      MCP配置
                                                                核心模式

Phase 4 ──────► Phase 5 ──────► Phase 6 ──────► Phase 7
斜杠命令       Hooks系统        供应商切换       Subagent

Phase 8 ──────► Phase 9 ──────► Phase 10
CodexMCP        测试文档         发布v1.0
```

### 1.3 新增核心组件 (来自技术调研)

| 组件 | 文件 | 功能 | 优先级 |
|------|------|------|--------|
| 原子写入 | `core/atomic.py` | 防止配置文件损坏 | P0 |
| 凭证管理 | `core/keyring.py` | 安全存储 API Token | P0 |
| Shell 集成 | `core/shell.py` | 哨兵块管理 RC 文件 | P1 |
| 深度合并 | `core/merge.py` | 配置递归合并 | P1 |
| init 命令 | `cli/init.py` | Shell 环境初始化 | P0 |

### 1.4 新增模板资源 (来自 claude-code-infrastructure-showcase) [NEW]

| 模板 | 目录 | 功能 | 整合方式 |
|------|------|------|----------|
| Skills 自动激活 | `templates/skill-activation/` | Hook + skill-rules.json | 完整复制 |
| Dev Docs 模板 | `templates/dev-docs/` | 三文件工作流模板 | 可选模板 |
| 代理模板 | `templates/agents-showcase/` | 10个专业代理 | 参考示例 |
| 命令模板 | `templates/commands-showcase/` | /dev-docs, /dev-docs-update | 参考示例 |

### 1.5 SuperClaude 核心模式 (来自 SuperClaude Framework v4.1.9) [NEW]

| 模式 | 用途 | Token 效率 | 文档 |
|------|------|-----------|------|
| ConfidenceChecker | 执行前信心评估 | ROI 25-250x | `docs/REFERENCE_SUPERCLAUDE.md` |
| SelfCheckProtocol | 执行后证据验证 | 94% 幻觉检测 | `docs/REFERENCE_SUPERCLAUDE.md` |
| ReflexionPattern | 错误学习与预防 | <10% 复发率 | `docs/REFERENCE_SUPERCLAUDE.md` |

---

## 2. 阶段划分

### Phase 1: 核心框架

**目标**: 搭建项目骨架，实现基础 CLI 和 ASCII Logo

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P1-1 | 初始化项目结构 (pyproject.toml, src/) | P0 | ✅ 完成 |
| P1-2 | 实现 CLI 入口 (click) | P0 | ✅ 完成 |
| P1-3 | 实现 ASCII Logo 和欢迎界面 | P1 | ✅ 完成 |
| P1-4 | 实现基础交互提示 (InquirerPy) | P1 | ✅ 完成 |
| P1-5 | 实现进度条和结果展示 (Rich) | P2 | ✅ 完成 |

**关键产出**:
- [x] 可运行的 `ohmyclaude` 命令
- [x] ASCII Logo 显示
- [x] 基础交互框架

**代码示例**:
```python
# P1-1: 项目初始化
# pyproject.toml 核心配置

# P1-2: CLI 入口
@click.group()
def cli():
    pass

@cli.command()
def setup():
    show_logo()
    console.print("Welcome to OhMyClaude!")

# P1-3: ASCII Logo
LOGO = """
╔═╗╦ ╦  ╔╦╗╦ ╦  ╔═╗╦  ╔═╗╦ ╦╔╦╗╔═╗
║ ║╠═╣  ║║║╚╦╝  ║  ║  ╠═╣║ ║ ║║╠╣
╚═╝╩ ╩  ╩ ╩ ╩   ╚═╝╩═╝╩ ╩╚═╝═╩╝╚═╝
"""
```

---

### Phase 1.5: 核心工具组件 [NEW]

**目标**: 实现基础设施组件（原子写入、凭证管理、Shell 集成）

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P1.5-1 | 实现原子写入上下文管理器 (atomic.py) | P0 | ✅ 完成 |
| P1.5-2 | 实现凭证管理器 (keyring.py) | P0 | ✅ 完成 |
| P1.5-3 | 实现 Shell 环境集成 (shell.py) | P1 | ✅ 完成 |
| P1.5-4 | 实现深度合并算法 (merge.py) | P1 | ✅ 完成 |
| P1.5-5 | 实现 `omc init` 命令 | P0 | ✅ 完成 |

**关键产出**:
- [x] 原子写入防止配置损坏
- [x] Keyring 安全存储 API Token
- [x] Shell 哨兵块管理
- [x] `ohmyclaude init` 初始化命令

**代码示例**:
```python
# P1.5-1: 原子写入
with atomic_write(settings_path) as f:
    json.dump(config, f)

# P1.5-2: 凭证管理
creds = CredentialManager()
token = creds.get("anthropic", env_var="ANTHROPIC_API_KEY")
creds.set("anthropic", new_token)

# P1.5-3: Shell 集成
shell = ShellIntegration()
shell.inject_source(Path.home() / ".ohmyclaude" / "env.sh")

# P1.5-4: 深度合并
merged = deep_merge(default_config, user_config)

# P1.5-5: init 命令
@cli.command()
def init():
    """Initialize OhMyClaude shell environment."""
    shell = ShellIntegration()
    shell.inject_source(ENV_FILE)
    console.print("[green]Shell environment configured![/]")
```

---

### Phase 2: 基础配置模块

**目标**: 实现 settings.json 和 CLAUDE.md 生成

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P2-1 | 定义 Pydantic 数据模型 | P0 | ✅ 完成 |
| P2-2 | 实现配置引擎 (ConfigEngine) | P0 | ✅ 完成 |
| P2-3 | 创建 CLAUDE.md 模板 (Jinja2) | P0 | ✅ 完成 |
| P2-4 | 实现安装器 (Installer) | P0 | ✅ 完成 |
| P2-5 | 实现备份管理器 | P1 | ✅ 完成 |
| P2-6 | 实现路径常量 (paths.py) | P1 | ✅ 完成 |

**关键产出**:
- [x] settings.json 生成功能
- [x] CLAUDE.md 模板系统
- [x] 配置备份/恢复

**代码示例**:
```python
# P2-1: 数据模型
class SettingsConfig(BaseModel):
    model: Literal["sonnet", "opus", "haiku"] = "sonnet"
    alwaysThinkingEnabled: bool = True

# P2-2: 配置引擎
class ConfigEngine:
    def load_preset(self, name: str) -> PresetConfig:
        ...

# P2-3: CLAUDE.md 模板
# templates/claude_md/general.md.j2

# P2-4: 安装器
class Installer:
    def install(self) -> dict:
        self._install_settings()
        self._install_claude_md()
```

---

### Phase 2.5: 模板资源整合 [NEW]

**目标**: 整合 claude-code-infrastructure-showcase 的精华模板资源

**背景**: 基于 Reddit 文章 "Claude Code is a Beast – Tips from 6 Months of Hardcore Use" 的实战经验

**任务清单**:

| 任务 | 描述 | 优先级 | 整合方式 |
|------|------|--------|----------|
| P2.5-1 | 整合 skill-rules.json (双语版) | P0 | 完整复制 + 本地化 |
| P2.5-2 | 整合 skill-activation-prompt.ts | P0 | 完整复制 |
| P2.5-3 | 整合 post-tool-use-tracker.sh | P0 | 完整复制 |
| P2.5-4 | 创建 Dev Docs 三文件模板 | P1 | 可选模板 |
| P2.5-5 | 整合代理模板 (10 个专业代理) | P1 | 参考示例 |
| P2.5-6 | 创建 /dev-docs 命令模板 | P2 | 参考示例 |

**核心模板结构**:
```
templates/
├── skill-activation/
│   ├── skill-rules.json        # 双语版技能触发规则
│   ├── skill-activation-prompt.ts
│   ├── post-tool-use-tracker.sh
│   └── README.md
│
├── dev-docs/
│   ├── plan-template.md
│   ├── context-template.md
│   ├── tasks-template.md
│   └── README.md
│
└── agents-showcase/
    ├── code-architecture-reviewer.md
    ├── auto-error-resolver.md
    ├── plan-reviewer.md
    ├── documentation-architect.md
    ├── web-research-specialist.md
    └── README.md
```

**双语 skill-rules.json 示例**:
```json
{
  "backend-dev-guidelines": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": [
        "backend", "controller", "service",
        "后端", "控制器", "服务", "接口"
      ],
      "intentPatterns": [
        "(create|add|创建|添加).*?(route|endpoint|路由|接口)"
      ]
    }
  }
}
```

**关键产出**:
- [x] Skills 自动激活系统（双语）
- [x] Dev Docs 三文件模板
- [x] 6 个通用代理模板
- [x] 模板整合 README

---

### Phase 2.6: SuperClaude 核心工作模式集成 [NEW]

**目标**: 将 SuperClaude PM Agent 的三大核心模式集成到 CLAUDE.md 模板中

**背景**: 来自 SuperClaude Framework v4.1.9 的 PM Agent 核心模式，经验证可显著提升代码质量和减少 Token 浪费

**任务清单**:

| 任务 | 描述 | 优先级 | 整合方式 |
|------|------|--------|----------|
| P2.6-1 | 创建 ConfidenceChecker 模板章节 | P0 | CLAUDE.md 注入 |
| P2.6-2 | 创建 SelfCheckProtocol 模板章节 | P0 | CLAUDE.md 注入 |
| P2.6-3 | 创建 ReflexionPattern 模板章节 | P0 | CLAUDE.md 注入 |
| P2.6-4 | 创建参考文档 REFERENCE_SUPERCLAUDE.md | P0 | 独立文档 |
| P2.6-5 | 更新 CLAUDE.md 模板生成器 | P1 | 模板引擎 |

**三大核心模式**:

| 模式 | 用途 | Token 效率 |
|------|------|-----------|
| **ConfidenceChecker** | 执行前信心评估 | ROI 25-250x 节省 |
| **SelfCheckProtocol** | 执行后证据验证 | 94% 幻觉检测率 |
| **ReflexionPattern** | 错误学习与预防 | <10% 错误复发率 |

**1. ConfidenceChecker 模板内容**:
```markdown
### 信心检查（执行前）
在开始任何实现前，评估信心等级:
- ≥90%: 继续执行
- 70-89%: 继续调查，提供选项
- <70%: 停止，向用户提问

检查维度:
1. 是否有重复实现？(25%)
2. 是否符合项目架构？(25%)
3. 是否验证了官方文档？(20%)
4. 是否参考了开源实现？(15%)
5. 是否确认了根本原因？(15%)
```

**2. SelfCheckProtocol 模板内容**:
```markdown
### 自我检查（执行后）
完成实现后，回答四个问题:
1. 所有测试通过了吗？→ 显示实际输出
2. 所有需求满足了吗？→ 列出对比
3. 有未验证的假设吗？→ 检查文档
4. 有证据吗？→ 提供结果

幻觉红旗（禁止出现）:
- 声称测试通过但不显示输出
- 声称一切正常但无证据
- "probably works" 等不确定性措辞
```

**3. ReflexionPattern 模板内容**:
```markdown
### 错误学习
遇到错误时:
1. 检查是否是已知错误 → 应用已知解决方案
2. 如果不是 → 调查并记录解决方案
3. 存储位置: docs/mistakes/*.md
```

**代码示例**:
```python
# P2.6-5: CLAUDE.md 模板生成器更新
CORE_PATTERNS_TEMPLATE = """
## 核心工作模式

### 信心检查（执行前）
{{ confidence_checker_content }}

### 自我检查（执行后）
{{ self_check_content }}

### 错误学习
{{ reflexion_content }}
"""

class ClaudeMdGenerator:
    def generate(self, config: Config) -> str:
        template = self.env.get_template("claude_md.j2")
        return template.render(
            core_patterns=CORE_PATTERNS_TEMPLATE if config.include_pm_patterns else "",
            ...
        )
```

**关键产出**:
- [x] CLAUDE.md 模板包含三大核心模式
- [x] 独立参考文档 `docs/REFERENCE_SUPERCLAUDE.md`
- [x] 模板生成器支持可选注入
- [x] 检查维度和权重清晰列出

**参考文档**: [docs/REFERENCE_SUPERCLAUDE.md](REFERENCE_SUPERCLAUDE.md)

---

### Phase 3: MCP 模块

**目标**: 实现 MCP 服务器配置和包管理系统

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P3-1 | 实现 MCP 预设包配置 (mcp_packages.yaml) | P0 | ✅ 完成 |
| P3-2 | 更新预设文件使用新 MCP 分类 | P0 | ✅ 完成 |
| P3-3 | 实现 MCP 配置生成 (modules/mcp.py) | P0 | ✅ 完成 |
| P3-4 | 添加国内 MCP (智谱 AI - 可选付费) | P1 | ✅ 完成 |
| P3-5 | Codex 代码审查和错误处理增强 | P2 | ✅ 完成 |

**MCP 包分类 (实际实现)**:

| 包名 | 服务器 | 费用层级 | 说明 |
|------|--------|----------|------|
| basic | filesystem, context7 | 免费 | 基础文件操作和文档查询 |
| reasoning | sequential-thinking | 免费 | 多步推理 |
| browser | playwright, chrome-devtools | 免费 | 浏览器自动化 |
| code | serena | 免费 | 语义代码理解 |
| codex | codexmcp | 免费 | Claude + Codex 协作 |
| web-free | tavily | 免费额度 | Web 搜索 |
| web-glm | web-reader, web-search-prime, zai-mcp-server | 付费 | 智谱 AI (可选) |
| ui | magic | 付费 | UI 组件生成 (可选) |
| transform | morphllm-fast-apply | 付费 | 代码转换 (可选) |
| diff | unified-diff | 免费 | 差异可视化 |

**预设包配置**:

| 预设 | 包含包 | Token 开销 | 月预算 |
|------|--------|-----------|--------|
| starter | basic | ~3,300 | $80 |
| standard | basic + reasoning + code + codex | ~5,500 | $100 |
| full | 所有免费包 + 可选付费包 | ~8,800+ | $130+ |

**关键产出**:
- [x] MCP 预设包选择和配置 (10 包, 14 服务器, 4 套装)
- [x] 国内 MCP 支持 (智谱 AI 作为可选付费服务)
- [x] 自动生成 MCP 配置 (settings.json 格式)
- [x] McpPackageRegistry 加载和解析系统
- [x] 增强的错误处理和验证 (Codex 审查)

---

### Phase 4: 斜杠命令模块

**目标**: 实现预设斜杠命令安装

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P4-1 | 创建命令模板 (/commit, /review, /test) | P0 | ✅ 完成 |
| P4-2 | 命令安装逻辑（已在 installer.py 中实现） | P0 | ✅ 完成 |
| P4-3 | 添加高级命令 (/codex, /dev-docs, /update-docs, /strategic-planning) | P1 | ✅ 完成 |
| P4-4 | 实现自定义命令支持 | P2 | P4-2 |

**命令模板示例**:
```markdown
# templates/commands/commit.md.j2
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: 智能 Git 提交 (Conventional Commits)
---

## 任务
分析代码变更并生成规范的提交信息

## 流程
1. 运行 `git status` 和 `git diff`
2. 分析变更内容
3. 生成 Conventional Commits 格式的中文提交信息
4. 执行 `git add` 和 `git commit`
```

---

### Phase 5: Hooks 模块

**目标**: 实现 Hooks 系统配置

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P5-1 | 定义 Hooks 配置模型 | P0 | ✅ 完成 |
| P5-2 | 创建预设 Hooks (SessionStart, PostToolUse, Stop) | P0 | ✅ 完成 |
| P5-3 | 实现 Hooks 配置生成 (_install_hooks) | P0 | ✅ 完成 |
| P5-4 | 添加通知钩子 (macOS) | P1 | ✅ 完成 |
| P5-5 | 添加日志钩子 | P1 | ✅ 完成 |

**实际实现**:
- Hooks 数据模型: `HookPreset`, `HookMatcherPreset` (presets.py), `HookConfig` (settings.py)
- 脚本安装: `_install_hooks()` 方法复制脚本到 `~/.claude/hooks/`
- 环境变量: `OHMYCLAUDE_ROOT` 指向 `~/.claude`
- 预设分布: starter (0 脚本), standard (0 脚本), full (8 脚本)

**预设 Hooks**:
```json
{
  "SessionStart": [
    {
      "hooks": [
        {"type": "command", "command": "git status --short"}
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {"type": "command", "command": "echo '[LOG]' >> ~/.claude/cmd.log"}
      ]
    }
  ]
}
```

---

### Phase 6: API 供应商切换模块 (Provider Switcher)

**目标**: 实现 API 供应商一键切换功能，支持官方订阅和第三方 API

**任务清单**:

| 任务 | 描述 | 优先级 | 依赖 |
|------|------|--------|------|
| P6-1 | 定义 Provider 数据模型 | P0 | P2 |
| P6-2 | 实现内置供应商配置 (official/glm/88code/deepseek) | P0 | P6-1 |
| P6-3 | 实现 ProviderSwitcher 切换引擎 | P0 | P6-2 |
| P6-4 | 实现 `ohmyclaude switch` 命令 | P0 | P6-3 |
| P6-5 | 实现 `ohmyclaude provider` 管理命令 | P1 | P6-4 |
| P6-6 | 实现自定义供应商支持 | P1 | P6-4 |
| P6-7 | 实现 shell 别名注入 (omc) | P2 | P6-4 |
| P6-8 | 实现 Codex auth.json 同步更新 | P1 | P6-3 |

**内置供应商**:

| 供应商 | API 类型 | Token 环境变量 |
|--------|----------|----------------|
| official | Anthropic 官方 | ANTHROPIC_AUTH_TOKEN |
| glm | Anthropic 兼容 | GLM_ANTHROPIC_AUTH_TOKEN |
| 88code | Anthropic + OpenAI | CODE88_ANTHROPIC_AUTH_TOKEN |
| deepseek | OpenAI 兼容 | DEEPSEEK_API_KEY |

**代码示例**:
```python
# P6-1: Provider 数据模型
class ProviderConfig(BaseModel):
    name: str
    display_name: str
    anthropic_base_url: Optional[str] = None
    anthropic_token_env: str
    openai_base_url: Optional[str] = None
    extra_env: dict[str, str] = Field(default_factory=dict)

# P6-3: 切换引擎
class ProviderSwitcher:
    def switch(self, provider_name: str, token: str = None):
        # 1. 备份 settings.json
        # 2. 更新 env 配置
        # 3. 可选：更新 codex auth.json
        pass

# P6-4: CLI 命令
@cli.command()
@click.argument("provider")
def switch(provider: str):
    """切换 API 供应商"""
    switcher = ProviderSwitcher()
    switcher.switch(provider)
```

**关键产出**:
- [x] 一键切换 API 供应商
- [x] 支持 4+ 内置供应商
- [x] 自定义供应商配置
- [x] 自动备份配置文件
- [x] 双命令入口 (omc/ohmyclaude)

---

### Phase 7: Subagent 模块 ✅ 完成

**目标**: 实现 Subagent 系统配置

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P7-1 | 研究 Claude Code Subagent 机制 | P0 | ✅ 完成 |
| P7-2 | 创建预设 Agent 模板 (5个新模板) | P0 | ✅ 完成 |
| P7-3 | 实现 `_install_agents()` 安装方法 | P0 | ✅ 完成 |
| P7-4 | 更新 `ensure_claude_dirs()` 创建 agents 目录 | P1 | ✅ 完成 |

**关键产出**:
- [x] 5 个新代理模板 (code-reviewer, debugger, test-engineer, refactor-expert, doc-writer)
- [x] `_install_agents()` 方法实现路径遍历保护
- [x] 预设级别代理分配 (starter: 2, standard: 5, full: 10)
- [x] 代理安装到 `~/.claude/agents/` 目录

**预设 Agent 列表**:

| 代理名称 | 预设级别 | 用途 |
|---------|---------|------|
| `code-reviewer` | starter | 代码审查专家 |
| `debugger` | starter | 调试专家 |
| `test-engineer` | standard | 测试工程师 |
| `refactor-expert` | standard | 重构专家 |
| `doc-writer` | standard | 文档撰写 |
| `code-architecture-reviewer` | full | 架构审查 |
| `auto-error-resolver` | full | 错误修复 |
| `web-research-specialist` | full | 网络调研 |
| `documentation-architect` | full | 文档架构 |
| `plan-reviewer` | full | 计划审查 |

---

### Phase 8: CodexMCP 集成 ✅ 完成

**目标**: 实现可选的 CodexMCP 协作功能

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P8-1 | 实现 CodexMCP 自动安装 | P0 | ✅ 完成 |
| P8-2 | 生成协作协议到 CLAUDE.md | P0 | ✅ 完成 |
| P8-3 | 添加 /codex 命令 | P0 | ✅ 完成 |
| P8-4 | 配置 MCP 权限 | P1 | ✅ 完成 |

**关键产出**:
- [x] CodexMCP 包定义 (`mcp_packages.yaml:71-81`)
- [x] Codex CLI 检测 (`mcp.py:359-364`)
- [x] /codex 命令模板 (`commands/codex.md.j2`, 119行)
- [x] CLAUDE.md 协作协议 (`claude_md/full.md.j2:102-140`)
- [x] Codex auth.json 同步 (`provider.py:229-276`)
- [x] 完整参考文档 (`REFERENCE_CODEXMCP.md`, 424行)

**预设支持**:

| 预设 | include_codex | codex MCP包 | /codex 命令 |
|-----|--------------|-------------|-------------|
| starter | false | ❌ | ❌ |
| standard | false | ✅ | ✅ |
| full | **true** | ✅ | ✅ |

**备注**: Phase 8 功能已在 Phase 3 (MCP) 和 Phase 4 (命令) 开发中提前完成

---

### Phase 9: 测试与文档 ✅ (2024-12-07)

**目标**: 完善测试覆盖和用户文档

**任务清单**:

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| P9-1 | 单元测试 (pytest) - 6个文件 | P0 | ✅ 完成 |
| P9-2 | 集成测试 - 2个文件 | P0 | ✅ 完成 |
| P9-3 | 增强 README.md | P0 | ✅ 完成 |
| P9-4 | 创建 CHANGELOG.md | P0 | ✅ 完成 |
| P9-5 | Codex 审查 (2次) | P0 | ✅ 完成 |
| P9-6 | Provider 切换功能测试 | P0 | ✅ 完成 |

**测试结果**: 157 tests passed, 53% coverage (核心模块 85%+)

---

### Phase 10: 发布 v1.0

**目标**: 发布稳定版本

**任务清单**:

| 任务 | 描述 | 优先级 | 依赖 |
|------|------|--------|------|
| P10-1 | 发布到 PyPI | P0 | P9 |
| P10-2 | 创建 install.sh 脚本 | P0 | P10-1 |
| P10-3 | 设置 GitHub Actions CI | P1 | P10-1 |
| P10-4 | 创建 Release Notes | P1 | P10-1 |
| P10-5 | 推广宣传 | P2 | P10-4 |

---

## 3. 依赖关系图

```
                         ┌──────────┐
                         │ Phase 1  │
                         │ 核心框架 │
                         └────┬─────┘
                              │
                         ┌────▼─────┐
                         │ Phase 2  │
                         │ 基础配置 │
                         └────┬─────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
    │ Phase 3 │         │ Phase 4 │         │ Phase 5 │
    │   MCP   │         │  命令   │         │  Hooks  │
    └────┬────┘         └────┬────┘         └────┬────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
               ┌────▼─────┐       ┌────▼─────┐
               │ Phase 6  │       │ Phase 7  │
               │ Provider │       │ Subagent │
               │ Switcher │       │          │
               └────┬─────┘       └────┬─────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                         ┌────▼─────┐
                         │ Phase 8  │
                         │ CodexMCP │
                         └────┬─────┘
                              │
                         ┌────▼─────┐
                         │ Phase 9  │
                         │ 测试文档 │
                         └────┬─────┘
                              │
                         ┌────▼─────┐
                         │ Phase 10 │
                         │ 发布1.0  │
                         └──────────┘
```

---

## 4. 风险管理

### 4.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| Claude Code 配置格式变更 | 高 | 中 | 版本检测 + 兼容层 |
| MCP 工具不可用 | 中 | 低 | 可选安装 + 错误处理 |
| Codex CLI 不兼容 | 中 | 低 | 版本检测 + 降级方案 |

### 4.2 进度风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 需求变更 | 中 | 中 | 模块化设计，易于调整 |
| 测试不充分 | 高 | 低 | 持续集成 + 覆盖率要求 |

---

## 5. 质量保证

### 5.1 代码质量

- **Linting**: Ruff (line-length=100)
- **Type Checking**: mypy (strict mode)
- **Testing**: pytest (coverage > 80%)
- **Pre-commit**: ruff + mypy hooks

### 5.2 文档质量

- README 包含快速开始指南
- 所有公开 API 有 docstring
- 每个 Phase 有详细说明

---

## 6. 版本规划

### v1.0.0 (当前)

- 核心配置向导
- 预设包 (Starter/Standard/Full)
- MCP 配置
- 斜杠命令
- Hooks 系统
- API 供应商切换 (official/glm/88code/deepseek)
- Subagent 系统
- CodexMCP 集成 (可选)

### v1.1.0 (未来)

- 配置导出/导入
- 更多 CLAUDE.md 模板
- 国际化支持

### v2.0.0 (未来)

- TUI 界面 (Textual)
- 配置同步
- 社区模板市场

### v3.0.0 (未来)

- Web UI
- VSCode 扩展
- 团队配置管理

---

## 7. 资源参考

### 7.1 代码参考

| 资源 | 路径 | 用途 |
|------|------|------|
| SuperClaude | `/ohmyclaude/superclaude/` | 命令/Agent 模板 |
| CodexMCP | `/ohmyclaude/codexmcp/` | Codex 集成 |
| Claude Docs | `/ohmyclaude/claudedocs/` | API/配置文档 |
| CCSW | `/ohmyclaude/ccsw/` | Provider 切换参考实现 |
| 用户配置 | `~/.claude/` | 配置参考 |

### 7.2 关键文件

**SuperClaude**:
- `plugins/superclaude/commands/` - 命令模板
- `plugins/superclaude/agents/` - Agent 模板
- `plugins/superclaude/hooks/` - Hook 配置
- `install.sh` - 安装脚本参考

**用户配置**:
- `~/.claude/settings.json` - 完整配置示例
- `~/.claude/commands/` - 命令示例
- `~/.claude/CLAUDE.md` - 规则模板

---

## 8. 检查清单

### Phase 完成检查

- [x] Phase 1: CLI 可运行，Logo 显示正常 ✅ (2024-12-03)
- [x] Phase 1.5: 原子写入、凭证管理、Shell 集成正常 ✅ (2024-12-03)
- [x] Phase 2: settings.json 和 CLAUDE.md 生成正确 ✅ (2024-12-04)
- [x] Phase 2.5: Skills 自动激活、Dev Docs 模板、代理模板整合完成 ✅ (2024-12-04)
- [x] Phase 2.6: SuperClaude 核心模式集成到 CLAUDE.md 模板 ✅ (2024-12-04)
- [x] Phase 3: MCP 包管理系统 (10包, 14服务器, 智谱AI可选付费) ✅ (2024-12-04)
- [x] Phase 4: 斜杠命令模板 (7个命令, 双语支持, Codex审查) ✅ (2024-12-04)
- [x] Phase 5: Hooks 系统 (脚本安装, OHMYCLAUDE_ROOT 环境变量, Codex审查) ✅ (2024-12-04)
- [x] Phase 2.7: CLI 命令集成 (setup/doctor/export/import, 安全提取, 回滚机制) ✅ (2024-12-04)
- [x] Phase 6: API 供应商切换 (4供应商, switch/provider命令, Codex同步, 备份机制) ✅ (2024-12-06)
- [x] Phase 7: Subagent 配置 (10代理模板, 预设级别分配, 路径安全保护) ✅ (2024-12-07)
- [x] Phase 8: CodexMCP 集成 (MCP包, /codex命令, 协作协议, auth同步) ✅ (2024-12-07)
- [x] Phase 9: 测试覆盖 53% (核心模块85%+), 文档完整 ✅ (2024-12-07)
- [ ] Phase 10: PyPI 发布成功，install.sh 可用

### 发布检查

- [ ] 所有测试通过
- [ ] README 完整
- [ ] CHANGELOG 更新
- [ ] 版本号正确
- [ ] PyPI 发布成功
- [ ] install.sh 测试通过
