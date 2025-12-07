# OhMyClaude

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-157%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-53%25-yellow)]()

**Claude Code 一键配置工具** - One-click configuration tool for Claude Code.

帮助中国开发者快速配置 Claude Code，支持多种 API 提供商切换。

---

## Features

- **3 预设配置**: starter / standard / full - 渐进式功能集
- **4 API 提供商**: Official / GLM / 88Code / DeepSeek 一键切换
- **10 代理模板**: code-reviewer, debugger, test-engineer 等专业代理
- **7 斜杠命令**: /commit, /review, /test, /codex 等开发命令
- **配置备份**: 自动备份、恢复、清理管理
- **CodexMCP 集成**: Claude + Codex 无缝协作

---

## Installation

### pip (推荐)

```bash
pip install ohmyclaude
```

### pipx (隔离环境)

```bash
pipx install ohmyclaude
```

### 从源码安装

```bash
git clone https://github.com/your-repo/ohmyclaude.git
cd ohmyclaude
pip install -e .
```

---

## Quick Start

两个命令均可使用：`omc` (简写) 和 `ohmyclaude`

```bash
# 1. 运行配置向导
omc setup

# 2. 检查配置状态
omc doctor

# 3. 切换 API 提供商
omc switch glm

# 4. 初始化 Shell 环境
omc init
```

---

## Commands

| Command | Description |
|---------|-------------|
| `omc setup` | 运行交互式配置向导 |
| `omc setup -p full` | 直接安装 full 预设 |
| `omc doctor` | 检查配置健康状态 |
| `omc switch <provider>` | 切换 API 提供商 |
| `omc switch --list` | 列出所有可用提供商 |
| `omc init` | 配置 Shell 环境 |
| `omc init --status` | 查看 Shell 集成状态 |
| `omc export <file>` | 导出配置 |
| `omc import <file>` | 导入配置 |
| `omc provider list` | 列出提供商 |
| `omc provider add` | 添加自定义提供商 |

---

## Presets

| Preset | 描述 | Token 开销 | 适用场景 |
|--------|------|-----------|---------|
| **starter** | 最小化配置 | ~3,300 (~2%) | 入门用户 |
| **standard** | 推荐配置 | ~5,500 (~3.5%) | 日常开发 |
| **full** | 完整功能 | ~8,800 (~6%) | 高级用户 |

### Preset 功能对比

| Feature | starter | standard | full |
|---------|:-------:|:--------:|:----:|
| CLAUDE.md 模板 | basic | standard | full |
| MCP 服务器 | basic | basic + reasoning | all |
| 斜杠命令 | 3 | 5 | 7 |
| 代理模板 | 0 | 5 | 10 |
| Hooks | basic | standard | full |
| CodexMCP | - | - | ✓ |

---

## API Providers

| Provider | 描述 | Token 环境变量 |
|----------|------|---------------|
| `official` | Anthropic 官方 API | `ANTHROPIC_API_KEY` |
| `glm` | 智谱 AI (国内优化) | `GLM_ANTHROPIC_AUTH_TOKEN` |
| `88code` | 第三方代理 | `CODE88_ANTHROPIC_AUTH_TOKEN` |
| `deepseek` | DeepSeek V3 (高性价比) | `DEEPSEEK_AUTH_TOKEN` |

### 切换示例

```bash
# 切换到 GLM
export GLM_ANTHROPIC_AUTH_TOKEN="your-token"
omc switch glm

# 切换回官方
omc switch official

# 添加自定义提供商
omc provider add myvendor \
  --base-url https://api.example.com/v1 \
  --token-env MY_TOKEN
```

---

## File Structure

安装后创建的文件结构：

```
~/.claude/
├── settings.json      # Claude Code 设置
├── CLAUDE.md          # 工作指令
├── commands/          # 斜杠命令模板
├── hooks/             # Hook 脚本
└── agents/            # 代理定义

~/.ohmyclaude/
├── backups/           # 配置备份
├── providers.yaml     # 自定义提供商
└── env.sh             # 环境变量
```

---

## Development

### 运行测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 运行测试 + 覆盖率
pytest tests/ -v --cov=ohmyclaude --cov-report=term-missing
```

### 项目结构

```
ohmyclaude/
├── src/ohmyclaude/
│   ├── cli/           # CLI 命令
│   ├── core/          # 核心模块
│   ├── models/        # Pydantic 模型
│   ├── modules/       # MCP/Provider 模块
│   ├── templates/     # Jinja2 模板
│   └── ui/            # UI 组件
├── tests/
│   ├── unit/          # 单元测试
│   └── integration/   # 集成测试
└── docs/              # 文档
```

---

## Troubleshooting

### 常见问题

**Q: `omc` 命令找不到？**
```bash
# 确保已安装
pip show ohmyclaude

# 或添加到 PATH
export PATH="$HOME/.local/bin:$PATH"
```

**Q: API 切换后不生效？**
```bash
# 重启 Claude Code 或打开新终端
omc doctor  # 检查状态
```

**Q: 如何恢复备份？**
```bash
# 查看可用备份
ls ~/.ohmyclaude/backups/

# 导入备份
omc import ~/.ohmyclaude/backups/backup-xxx.tar.gz
```

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - 系统架构设计
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) - 实施计划
- [PRD](docs/PRD.md) - 产品需求文档
- [Changelog](CHANGELOG.md) - 版本更新记录

---

## Contributing

欢迎贡献代码！请参考以下步骤：

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 Pull Request

---

## License

MIT License - 详见 [LICENSE](LICENSE)

---

## Acknowledgements

- [SuperClaude Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) - PM Agent patterns
- [CodexMCP](https://github.com/GuDaStudio/codexmcp) - Claude + Codex collaboration
- [Claude Code Infrastructure Showcase](https://github.com/diet103/claude-code-infrastructure-showcase) - Production config examples

---

*Made with love for Chinese developers using Claude Code*
