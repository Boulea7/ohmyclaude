# OhMyClaude

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![CLI](https://img.shields.io/badge/interface-CLI-black)
![Claude First](https://img.shields.io/badge/focus-Claude%20First-6f42c1)
![Codex Aware](https://img.shields.io/badge/focus-Codex%20Aware-0a7ea4)
![Local Safe](https://img.shields.io/badge/testing-local%20safe-2ea44f)

**Language:** [English](README.md) | [简体中文](README.zh-CN.md) | 繁體中文 | [日本語](README.ja.md)

**一個以 Claude 為預設主線、同時支援多 harness 顯式輸出的本地安全 CLI。**

OhMyClaude 幫你在本機快速建立一套實用的 Claude Code 工作流：產生 `settings.json`、產生 `CLAUDE.md`、安裝 commands / hooks / agents / skills 模板、切換 provider、初始化 shell 整合，並在配置變更前後保留備份。

目前專案採用分階段定位：

- **Claude-first**：預設安裝主線仍然是 Claude Code
- **Multi-harness**：已支援顯式渲染 / 安裝 `claude-home`、`claude-plugin`、`codex-project`、`gemini-extension` bundle
- **Local-safe**：倉庫開發與測試預設不碰你真實的 `~/.claude`、`~/.codex`、Gemini CLI 配置

## 為什麼選擇 OhMyClaude

很多 Claude Code 設定倉庫常落在兩個極端：

- 太小，只提供零散的 copy-paste 片段
- 太大，膨脹成多 harness 框架，最後讓程式碼與公開文件逐漸脫節

OhMyClaude 的目標是中間地帶：

- 用一個聚焦的 Python CLI 安裝一組清楚、可用的 Claude 資產
- 讓模板數量足夠實用，但不盲目擴張成無邊界平台
- 把 **公開倉庫內容** 和 **本地 AI 維護資料** 明確分層

## 亮點

| Area | What You Get |
|------|--------------|
| Claude setup | 產生 `~/.claude/settings.json`、`~/.claude/CLAUDE.md`、commands、hooks、agents、skills |
| Multi-harness bundles | 可顯式渲染或安裝 `.claude-plugin/`、`.codex/`、`.agents/skills/`、Gemini extension bundle |
| Workflow assets | 安裝 `7` 個 commands、`10` 個 agents、`12` 個 skills、`8` 個 hook script 模板 |
| MCP bundles | 透過 `templates/mcp/mcp_packages.yaml` 組合 MCP 套件群組 |
| Provider switching | 切換官方 / 第三方 / 自訂 provider，並把 Codex auth 同步改成顯式 opt-in |
| Shell integration | 透過 `omc init` 注入或移除 shell 初始化區塊 |
| Config safety | `doctor`、`render`、`install`、`export`、`import`、備份與還原 |
| Codex / Gemini awareness | 區分 Claude 側 Codex bridge、原生 Codex 專案資產，以及 Gemini extension 輸出 |

## 目前已實作

目前已經落地的能力：

- 安裝 Claude Code 配置與模板
- 透過 preset 產生 `mcpServers` 與 hooks 設定
- 安裝 commands / hooks / agents / skills 模板
- 顯式渲染 target bundle：`claude-home`、`claude-plugin`、`codex-project`、`gemini-extension`
- 管理 API provider
- 只在顯式要求時同步 OpenAI-compatible 的 Codex 認證檔
- 執行健康檢查、shell 初始化、匯入匯出與更新檢查

## 目前不做的事

目前的非目標：

- 不做託管式插件市場或註冊服務
- 不會自動把產生的 bundle 註冊到 Claude Code / Gemini CLI
- 不會在倉庫維護過程中隱式改寫真實 `~/.codex` 或 `~/.gemini`
- 目前階段不處理 Gemini 全域 `settings.json` 合併

## 這裡的「Codex-aware」是什麼意思

OhMyClaude 裡提到的 Codex 有兩層，必須分清：

### 1. Claude 內部的相容橋接

preset 中的 `codex` MCP 套件表示 **Claude 工作流中的 Codex bridge 路徑**。

它適合：

- 在 Claude 對話裡請 Codex 協助分析、review、原型草案
- 保持既有 Claude-first 工作流結構

它不等於：

- Codex 官方原生的 `AGENTS.md`
- Codex 官方原生 skills
- Codex 官方原生 `.codex/config.toml`

### 2. 原生 Codex 能力

原生 Codex 支援 `AGENTS.md`、skills、`.codex/config.toml`、subagents 等官方能力。

本倉庫現在已支援把這些能力渲染或安裝到 **顯式目標目錄**，但不會在 `setup` 或倉庫維護流程裡隱式寫入你的真實 `~/.codex`。

## 安全模型

如果你只是想維護這個倉庫，而不想誤改自己的真實工具配置，請遵循下面做法：

- 測試 provider 切換時直接用 `omc switch <provider>`；只有傳 `--sync-codex-auth` 才會動 Codex
- 測試安裝邏輯時只使用倉庫現有測試，它們會把路徑 patch 到暫存目錄
- 不直接對真實 `~/.claude`、`~/.codex`、Gemini 目錄做手動 smoke test
- 優先用 `omc render` 與顯式 `omc install --dest ... --confirm` 在暫存目錄裡驗收
- `omc render` 預設會拒絕寫入真實 harness home 目錄

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
# 1. 安裝一個 preset
omc setup --preset standard

# 2. 渲染一個 Codex project bundle，不碰真實 home
omc render --target codex-project --output ./.tmp/codex-project

# 3. 安裝一個 Gemini extension bundle 到顯式目錄
omc install --target gemini-extension --preset standard --dest ./.tmp/gemini-extension --confirm

# 4. 檢查 Claude 配置狀態
omc doctor

# 5. 檢查 shell 注入狀態
omc init --status

# 6. 安全切換 provider，預設不改 Codex 配置
omc switch glm
```

## Commands

| Command | Purpose |
|---------|---------|
| `omc setup` | 安裝 `starter`、`standard`、`full` preset |
| `omc doctor` | 檢查 Claude home、plugin bundle、Codex project bundle 或 Gemini extension bundle |
| `omc init` | 寫入或移除 shell 初始化區塊 |
| `omc render --target <target>` | 將 target bundle 渲染到顯式輸出目錄 |
| `omc install --target <target>` | 將 target bundle 安裝到顯式目錄，並要求確認 |
| `omc switch <provider>` | 切換 API provider |
| `omc switch --list` | 列出可用 provider |
| `omc provider list/show/add/remove` | 管理自訂 provider |
| `omc export <file>` | 匯出目前的 Claude 配置 |
| `omc import <file>` | 從封存檔還原配置 |
| `omc update` | 檢查套件更新 |

## Preset Comparison

| Preset | Positioning | Current Shape |
|--------|-------------|---------------|
| `starter` | 最小可用配置 | `basic` MCP、3 個 commands、2 個 agents、無 skill 安裝 |
| `standard` | 日常開發推薦 | `basic + reasoning + code + codex`、4 個 commands、5 個 agents、inline hooks |
| `full` | 最完整的 Claude 資產集 | 7 個基礎 MCP 群組、3 個 optional MCP 群組、7 個 commands、10 個 agents、12 個 skills、8 個 hook scripts |

補充說明：

- 這張表描述的是預設 `claude-home` 輸出面
- `standard` 和 `full` 裡的 `codex` 仍然是 **Claude 側 bridge**
- 它不等於原生 Codex 安裝能力
- 公開文案已改用較新的 Claude / Codex 術語，但實際行為仍以目前程式碼為準

## Target 輸出面

目前支援的顯式輸出面：

| Target | 輸出形態 | 典型用途 |
|--------|----------|----------|
| `claude-home` | `settings.json`、`CLAUDE.md`、`commands/`、`hooks/`、`agents/`、`skills/` | 安裝到暫存 Claude 目錄或顯式替代目錄 |
| `claude-plugin` | `.claude-plugin/plugin.json` + `commands/`、`hooks/`、`agents/`、`skills/` | 產生可分享的 Claude plugin bundle |
| `codex-project` | `AGENTS.md`、`.codex/config.toml`、`.codex/agents/`、`.agents/skills/` | 為專案產生原生 Codex 層 |
| `gemini-extension` | `gemini-extension.json`、`GEMINI.md`、`commands/`、`hooks/`、`agents/`、`skills/` | 產生 Gemini CLI extension bundle |

如果輸出不在預設位置，記得使用 `omc doctor --target <target> --path <root>` 指定 bundle 根目錄；否則 CLI 會回退到 `cwd` 或 `~/.claude` 做檢查。

目前 plugin / Gemini 的 portable hooks 是一組「可攜子集」：

- 它們會避免依賴 home 目錄假設
- 但暫時不會與 `full` preset 在 Claude home 下的 hook 行為完全一一對應

## Repository Layout

```text
src/ohmyclaude/
├── cli/            # Click CLI 入口
├── core/           # 安裝、配置、provider、shell、backup
├── models/         # Pydantic 模型
├── modules/        # MCP 與 provider 定義
├── templates/      # CLAUDE.md / commands / hooks / agents / skills 模板
└── ui/             # 基於 Rich 的 CLI 顯示輔助

templates/
├── presets/        # starter / standard / full YAML
└── mcp/            # MCP package registry

tests/
├── unit/
└── integration/
```

## 公開內容與本地私有資料

這個倉庫明確區分 **公開 GitHub 內容** 與 **本地 AI 私有資料**。

### Public

公開層主要包括：

- `README.md`
- `README.zh-CN.md`
- `README.zh-TW.md`
- `README.ja.md`
- `src/`
- `templates/`
- `tests/`
- `CHANGELOG.md`、`SECURITY.md`、`CONTRIBUTING.md`、`RELEASE_GUIDE.md`

### Local

本地私有資料應放在被忽略的路徑中，例如：

- `.ai-notes/`
- `docs/`
- 本地未追蹤的根級 AI 檔案，例如 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`

這樣可以避免研究筆記、變更追蹤與 AI 專用索引檔進入公開 Git 歷史。

目前清理策略下，這些根級 AI 檔案會繼續保留在本地，但從 Git 追蹤中移除。

## 常見問題

### 這個專案會自動幫我配置原生 Codex 嗎？

現在可以把專案級 Codex 資產渲染或安裝到顯式目錄裡，但不會在一般維護流程中自動寫入你的真實 `~/.codex`。

### `switch` 會不會改我的 Codex 配置？

只有你顯式傳了 `--sync-codex-auth` 才會。

### 為什麼本地 AI 資料不公開？

因為研究筆記、索引檔與 AI 工作上下文在本地很有用，但會讓公開倉庫更嘈雜、可攜性更差，也更容易暴露隱私資訊。

### 這是一個多 harness 配置平台嗎？

是，但仍然分階段推進。現階段重點是顯式 bundle 輸出與安全安裝，而不是對所有 harness 做隱式 home 目錄寫入。

## 開發

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# Ruff
ruff check .

# MyPy
python -m mypy src/ohmyclaude

# Pytest
pytest
```

## 路線圖

較現實的下一階段包括：

- 進一步增強 Claude plugin 與 Gemini extension 的 target-specific 驗證
- 在不讓預設膨脹過快的前提下擴充共享 skill / agent 資產
- 補齊更多 target-aware 的 doctor 檢查與 troubleshooting 文件
- 在維持 local-safe 前提下繼續擴展多 harness 支援

## Acknowledgements

- [obra/superpowers](https://github.com/obra/superpowers) — 強工作流約束、設計先行、技能驅動
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — 分層 rules / skills / hooks / troubleshooting 組織方式
- [Claude Code Docs](https://code.claude.com/docs/en) — 當前官方 hooks、plugins、memory、subagents 能力
- [OpenAI Codex Docs](https://developers.openai.com/codex/) — 當前官方 `AGENTS.md`、skills、subagents、config 能力
- [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) — 當前 Gemini CLI 的 extension、commands、skills、context 模式
