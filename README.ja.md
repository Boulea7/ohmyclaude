# OhMyClaude

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![CLI](https://img.shields.io/badge/interface-CLI-black)
![Claude First](https://img.shields.io/badge/focus-Claude%20First-6f42c1)
![Codex Aware](https://img.shields.io/badge/focus-Codex%20Aware-0a7ea4)
![Local Safe](https://img.shields.io/badge/testing-local%20safe-2ea44f)

**Language:** [English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | 日本語

**Claude を既定路線にしつつ、多 harness の明示的な出力にも対応した local-safe CLI。**

OhMyClaude は、実用的な Claude Code ワークフローを手早く整えるためのツールです。`settings.json` の生成、`CLAUDE.md` の生成、commands / hooks / agents / skills テンプレートの導入、provider の切り替え、shell 初期化、設定変更前後のバックアップをまとめて扱えます。

現在のプロジェクト方針は段階的です。

- **Claude-first**: 既定の導入対象は引き続き Claude Code
- **Multi-harness**: `claude-home`、`claude-plugin`、`codex-project`、`gemini-extension` bundle を明示的に render / install 可能
- **Local-safe**: リポジトリ開発とテストでは、実際の `~/.claude`、`~/.codex`、Gemini CLI 設定を不用意に触らない

## なぜ OhMyClaude なのか

Claude Code 設定系のリポジトリは、よく次のどちらかに寄りがちです。

- 小さすぎて、断片的な設定例しか残らない
- 逆に大きくなりすぎて、多 harness フレームワーク化し、コードと公開ドキュメントが乖離する

OhMyClaude が狙うのはその中間です。

- 焦点の合った Python CLI で、必要十分な Claude 資産を導入する
- 役立つだけのテンプレート量を持ちつつ、境界のないプラットフォーム化はしない
- **公開リポジトリの内容** と **ローカル AI 運用資料** を明確に分離する

## 主な特徴

| Area | What You Get |
|------|--------------|
| Claude setup | `~/.claude/settings.json`、`~/.claude/CLAUDE.md`、commands、hooks、agents、skills を生成 |
| Multi-harness bundles | `.claude-plugin/`、`.codex/`、`.agents/skills/`、Gemini extension bundle を明示的に render / install |
| Workflow assets | `7` 個の commands、`10` 個の agents、`12` 個の skills、`8` 個の hook script テンプレートを導入 |
| MCP bundles | `templates/mcp/mcp_packages.yaml` から MCP パッケージ群を構成 |
| Provider switching | 公式 / サードパーティ / カスタム provider を切り替え、Codex auth 同期は明示 opt-in |
| Shell integration | `omc init` で shell 初期化ブロックを追加・削除 |
| Config safety | `doctor`、`render`、`install`、`export`、`import`、バックアップ / 復元 |
| Codex / Gemini awareness | Claude 側の Codex bridge、ネイティブ Codex 資産、Gemini extension 出力を用語上きちんと区別 |

## 現在できること

現在すでに実装されている機能：

- Claude Code 設定とテンプレートの導入
- preset から `mcpServers` と hooks を生成
- commands / hooks / agents / skills テンプレートの導入
- `claude-home`、`claude-plugin`、`codex-project`、`gemini-extension` 向け bundle の明示 render
- API provider の管理
- OpenAI-compatible な Codex 認証設定は、明示要求がある場合にのみ同期
- health check、shell 初期化、export/import、更新確認

## 現在やらないこと

現時点での非目標：

- ホスト型のプラグイン marketplace / registry にはしない
- 生成した bundle を Claude Code / Gemini CLI に自動登録しない
- リポジトリ保守中に実際の `~/.codex` や `~/.gemini` を暗黙に書き換えない
- この段階では Gemini の全体 `settings.json` マージ管理はしない

## ここでいう「Codex-aware」とは

OhMyClaude における Codex には 2 つの層があります。

### 1. Claude 内部の互換 bridge

preset にある `codex` MCP パッケージは、**Claude ワークフロー内で使う Codex bridge 経路**を意味します。

向いている用途：

- Claude セッション中に Codex へ分析・review・試作案を依頼する
- 既存の Claude-first ワークフロー構造を保つ

これは次のものとは別です。

- Codex ネイティブの `AGENTS.md`
- Codex ネイティブの skills
- Codex ネイティブの `.codex/config.toml`

### 2. ネイティブ Codex 機能

ネイティブ Codex は `AGENTS.md`、skills、`.codex/config.toml`、subagents などの公式機能を持ちます。

このリポジトリは現在、それらを **明示的なターゲットディレクトリ** に render / install できますが、`setup` や日常的なリポジトリ保守で実際の `~/.codex` を暗黙に更新することはありません。

## セーフティモデル

このリポジトリを保守するだけで、実環境の設定を誤って変えたくない場合は、次を守ってください。

- provider 切り替えの確認には `omc switch <provider>` を使い、Codex auth 変更が必要なときだけ `--sync-codex-auth` を付ける
- 導入ロジックの確認は既存テストを使う。テストはパスを一時ディレクトリへ patch する
- 実際の `~/.claude`、`~/.codex`、Gemini ディレクトリに対して手動 smoke test をしない
- まず `omc render` を使い、必要なら `omc install --dest ... --confirm` を明示先に対して実行する
- `omc render` は実際の harness home ディレクトリへの書き込みを拒否する

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
# 1. preset を導入
omc setup --preset standard

# 2. 実際の home を触らずに Codex project bundle を render
omc render --target codex-project --output ./.tmp/codex-project

# 3. 明示ディレクトリへ Gemini extension bundle を install
omc install --target gemini-extension --preset standard --dest ./.tmp/gemini-extension --confirm

# 4. Claude 設定状態を確認
omc doctor

# 5. shell 初期化状態を確認
omc init --status

# 6. 既定では Codex を触らずに provider を切り替え
omc switch glm
```

## Commands

| Command | Purpose |
|---------|---------|
| `omc setup` | `starter` / `standard` / `full` preset を導入 |
| `omc doctor` | Claude home、plugin bundle、Codex project bundle、Gemini extension bundle を確認 |
| `omc init` | shell 初期化ブロックを追加・削除 |
| `omc render --target <target>` | target bundle を明示出力ディレクトリへ render |
| `omc install --target <target>` | target bundle を明示ディレクトリへ install し、確認を要求 |
| `omc switch <provider>` | API provider を切り替え |
| `omc switch --list` | 利用可能な provider を一覧表示 |
| `omc provider list/show/add/remove` | カスタム provider を管理 |
| `omc export <file>` | 現在の Claude 設定を export |
| `omc import <file>` | アーカイブから設定を復元 |
| `omc update` | パッケージ更新を確認 |

## Preset Comparison

| Preset | Positioning | Current Shape |
|--------|-------------|---------------|
| `starter` | 最小構成 | `basic` MCP、3 commands、2 agents、skill 導入なし |
| `standard` | 日常開発向け推奨構成 | `basic + reasoning + code + codex`、4 commands、5 agents、inline hooks |
| `full` | もっとも充実した Claude 資産セット | 7 基本 MCP グループ、3 optional MCP グループ、7 commands、10 agents、12 skills、8 hook scripts |

補足：

- この表は既定の `claude-home` 出力面を説明する
- `standard` と `full` の `codex` は **Claude 側 bridge**
- ネイティブ Codex 導入機能そのものではない
- 公開文言は新しい Claude / Codex 用語に合わせてあるが、実際の挙動は現行コードで決まる

## Target 出力面

現在サポートしている明示的な出力面：

| Target | 出力形態 | 典型的な用途 |
|--------|----------|--------------|
| `claude-home` | `settings.json`、`CLAUDE.md`、`commands/`、`hooks/`、`agents/`、`skills/` | 一時的な Claude ディレクトリや明示的な代替先への導入 |
| `claude-plugin` | `.claude-plugin/plugin.json` + `commands/`、`hooks/`、`agents/`、`skills/` | 配布可能な Claude plugin bundle の生成 |
| `codex-project` | `AGENTS.md`、`.codex/config.toml`、`.codex/agents/`、`.agents/skills/` | プロジェクトローカルなネイティブ Codex レイヤーの生成 |
| `gemini-extension` | `gemini-extension.json`、`GEMINI.md`、`commands/`、`hooks/`、`agents/`、`skills/` | Gemini CLI extension bundle の生成 |

既定位置以外を確認したい場合は、`omc doctor --target <target> --path <root>` を使って bundle ルートを指定してください。そうしない場合、CLI は `cwd` または `~/.claude` を基準に確認します。

plugin / Gemini 向け portable hooks は現在、完全版の一部だけを切り出した **self-contained subset** です。

- home ディレクトリ依存を避けるよう設計されている
- ただし `full` preset の Claude home 用 hook 群と完全に 1 対 1 対応しているわけではない

## Repository Layout

```text
src/ohmyclaude/
├── cli/            # Click CLI entrypoint
├── core/           # install, config, provider, shell, backup
├── models/         # Pydantic models
├── modules/        # MCP と provider 定義
├── templates/      # CLAUDE.md / commands / hooks / agents / skills templates
└── ui/             # Rich ベースの CLI 表示補助

templates/
├── presets/        # starter / standard / full YAML
└── mcp/            # MCP package registry

tests/
├── unit/
└── integration/
```

## 公開コンテンツとローカル専用資料

このリポジトリでは **公開 GitHub コンテンツ** と **ローカル AI 用資料** を分けています。

### Public

公開面の中心は次のとおりです。

- `README.md`
- `README.zh-CN.md`
- `README.zh-TW.md`
- `README.ja.md`
- `src/`
- `templates/`
- `tests/`
- `CHANGELOG.md`、`SECURITY.md`、`CONTRIBUTING.md`、`RELEASE_GUIDE.md`

### Local

ローカル専用資料は、無視されるパスに置きます。

- `.ai-notes/`
- `docs/`
- `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` のようなローカル未追跡のルート AI ファイル

これにより、調査メモ、変更追跡、AI 専用インデックスが公開 Git 履歴へ混入するのを防ぎます。

現在の整理方針では、これらのルート AI ファイルはローカルに残しつつ、Git 追跡対象から外します。

## FAQ / よくある質問

### このプロジェクトはネイティブ Codex を自動設定しますか？

現在は、プロジェクトスコープの Codex 資産を明示ディレクトリに render / install できますが、通常の保守フローで実際の `~/.codex` を自動更新することはありません。

### `switch` は Codex 設定を変更しますか？

`--sync-codex-auth` を明示したときだけです。

### なぜローカル AI 資料を公開しないのですか？

調査ノート、インデックス、AI 用作業コンテキストはローカルでは有用ですが、公開リポジトリではノイズになり、移植性やプライバシーの面でも不利だからです。

### これは多 harness 設定プラットフォームですか？

はい。ただし段階的に進めています。現段階の焦点は、明示的な bundle 出力と local-safe な導入であり、あらゆる harness の home ディレクトリを暗黙に書き換えることではありません。

## 開発

```bash
# 開発依存を導入
pip install -e ".[dev]"

# Ruff
ruff check .

# MyPy
python -m mypy src/ohmyclaude

# Pytest
pytest
```

## ロードマップ

現実的な次のステップ：

- Claude plugin と Gemini extension の target-specific 検証をさらに強化する
- 既定 preset を過度に膨らませず、共有 skill / agent 資産を拡充する
- target-aware な doctor チェックと troubleshooting ドキュメントを増やす
- local-safe を維持したまま multi-harness 対応を拡張する

## Acknowledgements

- [obra/superpowers](https://github.com/obra/superpowers) — ワークフロー規律、設計先行、skill 駆動
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — layered rules / skills / hooks / troubleshooting の構成
- [Claude Code Docs](https://code.claude.com/docs/en) — hooks、plugins、memory、subagents の最新仕様
- [OpenAI Codex Docs](https://developers.openai.com/codex/) — `AGENTS.md`、skills、subagents、config の最新仕様
- [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) — Gemini CLI の extension、commands、skills、context モード
