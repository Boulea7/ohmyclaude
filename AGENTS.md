# OhMyClaude 项目说明书（Agent Guide）

## 1. 项目简介（功能描述）
OhMyClaude 是一个用于 **一键配置 Claude Code** 的命令行工具，主要能力包括：
- 生成并安装 `~/.claude/settings.json`、`~/.claude/CLAUDE.md`
- 安装 Slash Commands、Hooks、Agents 等模板资源
- 管理/切换 API Provider（官方/第三方/自定义），并可同步 Codex 相关配置
- 提供 `doctor` 健康检查与 `init` Shell 集成（向 RC 文件写入可幂等的 sentinel block）

代码位于 `src/ohmyclaude/`，测试位于 `tests/`。

---

## 2. 使用方法（CLI）
安装后可使用 `ohmyclaude` 或 `omc`。

### 常用命令
- `omc setup`
  - 作用：交互式安装预设（starter/standard/full）
  - 常用参数：
    - `--preset/-p {starter,standard,full}`：跳过交互，直接选择预设
    - `--no-interactive/-y`：非交互模式，使用默认值
- `omc init`
  - 作用：在 shell RC 文件中注入/移除 ohmyclaude 的环境变量 source 片段（幂等）
  - 常用参数：
    - `--status`：查看是否已注入
    - `--remove`：移除注入块
- `omc doctor`
  - 作用：检查 `~/.claude` 下关键文件/目录是否就绪
- `omc switch`
  - 作用：切换 API Provider（支持 list 模式与交互选择）
- `omc provider ...`
  - 作用：管理自定义 provider（list/show/add/remove 等）

---

## 3. 关键模块与参数/返回值说明

### 3.1 `ohmyclaude.core.installer.Installer`
- `install(skip_mcp: bool = False) -> dict[str, Any]`
  - 返回结构（示例）：
    - `installed`: `list[dict[str, Any]]`
    - `skipped`: `list[dict[str, Any]]`
    - `errors`: `list[dict[str, Any]]`
    - `success`: `bool`
    - `summary`: `dict[str, int]`

### 3.2 `ohmyclaude.core.shell.get_shell_info()`
- 返回 `ShellInfo`（TypedDict）：
  - `shell: str`
  - `rc_path: str`
  - `is_installed: bool`

### 3.3 `ohmyclaude.core.provider.ProviderSwitcher`
- `switch(...) -> SwitchResult`：执行 provider 切换并返回结果模型（见 `ohmyclaude.models.provider.SwitchResult`）

---

## 4. 开发与验证
- 运行 mypy（严格模式）：`python -m mypy src/ohmyclaude`
- 运行测试：`pytest`

---

## 5. 变更记录（Changelog）
- 2025-12-13：修复全量 mypy 严格模式类型错误（补全泛型参数、补齐缺失注解、修复 `no-any-return`/第三方库类型问题），并确保 `pytest` 全量通过。
- 2025-12-13：修复 23 个 Ruff `E501` 行长问题（函数签名/多重 `patch`/长断言拆行），并确保 `ruff check` 与 `pytest` 全量通过。

---

## 6. 规划/待办（Roadmap）
- 提升覆盖率：为 `ui/progress.py`、`ui/theme.py`、`modules/mcp.py` 等补充单测，降低对 coverage 阈值的敏感度。
- 类型依赖收敛：评估是否将 `types-PyYAML` 固定到开发依赖（减少 `import-untyped` 相关处理）。
- Provider 与模板：补充更多预设与模板（含中文说明），并完善 `doctor` 的诊断建议。
