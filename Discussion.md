# cc-hooks-py 設計ディスカッション議事録

## 概要

Claude Code の Hook スクリプトを Python で書くための型定義ライブラリ `cc-hooks-py` の設計を、
9 ラウンドの Q&A で詳細に詰めた記録。

---

## ラウンド 1: 基本設計方針

### 質問 1: 型システムの選択

**質問**: Hook ペイロードの型定義にどの型システムを使うか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **Pydantic v2 モデル** | ランタイムバリデーション、JSON シリアライズ内蔵、IDE 補完が優秀、`.model_dump_json()` | pydantic が hard dependency (~2MB) |
| TypedDict + dataclasses | 外部依存なし、stdlib のみ、軽量 | ランタイムバリデーションなし、手動 JSON シリアライズ |
| Pydantic + TypedDict フォールバック | 両方の良いとこ取り | 2 つのコードパスのメンテ、複雑化 |

**決定**: **Pydantic v2 モデル**

### 質問 2: 最低 Python バージョン

**質問**: サポートする最低 Python バージョンは？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| Python 3.10+ | match/case、`X \| Y` 型構文 | 古い環境を除外 |
| Python 3.11+ | ExceptionGroup、StrEnum、tomllib | より狭い互換性 |
| **Python 3.12+** | 型パラメータ構文、override デコレータ | 最も制限的 |

**決定**: **Python 3.12+**

### 質問 3: ヘルパー API のスタイル

**質問**: ボイラープレート削減のヘルパー API はどういうスタイルにするか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **デコレータベース** | Pythonic、クリーン、最小ボイラープレート | デコレータ内部のマジック |
| 関数ベース | 明示的、理解しやすい | フックごとのボイラープレートが多い |
| 両方 | 柔軟性 | API 表面積が大きい |

**決定**: **デコレータベース** (`@hook("PreToolUse")`)

### 質問 4: イベントスコープ

**質問**: 全 15 Hook イベントを最初からカバーするか、主要なものだけ先にやるか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **全 15 イベント** | 初日から完全 | 初期作業量が多い |
| コア 6 イベント | 早く出荷、ユースケースの 90% カバー | 不完全、後から追加が必要 |

**決定**: **全 15 イベント**（SessionStart, SessionEnd, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, Notification, SubagentStart, SubagentStop, Stop, TeammateIdle, TaskCompleted, ConfigChange, PreCompact）

---

## ラウンド 2: パッケージ構造と配布

### 質問 5: パッケージの内部構造

**質問**: パッケージ内部をどう構造化するか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| フラット: 単一パッケージ | シンプルな import、発見しやすい | 大きな `__init__.py` |
| **モジュラー: 関心事で分割** | 明確な分離、イベントごとのファイル | import パスがやや複雑 |
| 単一ファイル | 超シンプル、ベンダリング可能 | メンテが大変、サブ import 不可 |

**決定**: **モジュラー分割**

```
cc_hooks/
  models/       # イベントごとに分割
  tools/        # ツール入力型
  runner.py     # デコレータ
  registry.py   # ツール登録
  enums.py      # 列挙型
```

### 質問 6: 配布方法

**質問**: ライブラリの配布方法は？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| PyPI + GitHub | 標準的な Python 配布 | リリース/バージョン管理が必要 |
| GitHub のみ | PyPI アカウント不要 | インストールが遅い |
| **PyPI + GitHub + uv サポート** | 最大互換性（pip, uv, poetry） | 設定がやや多い |

**決定**: **PyPI + GitHub + uv サポート**（pyproject.toml ベース）

### 質問 7: デコレータ API の具体形

**質問**: デコレータ API の具体的な見た目は？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| `@hook` 単一デコレータ（型推論） | 最小 API | マジックが多い |
| **`@hook("PreToolUse")` 明示的** | 曖昧さなし、grep しやすい | やや冗長 |
| `run()` 関数（デコレータなし） | 最も明示的 | ボイラープレートが多い |

**決定**: **`@hook("PreToolUse")` 明示的イベント名指定**

```python
@hook("PreToolUse")
def on_pre_tool_use(input: PreToolUseInput) -> PreToolUseOutput:
    if input.tool_name == "Bash":
        return PreToolUseOutput.deny("No bash allowed")
    return PreToolUseOutput.allow()
```

---

## ラウンド 3: Output API とエラーハンドリング

### 質問 8: Output モデルの便利メソッド

**質問**: Output モデルにどのような便利メソッドを提供するか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **クラスメソッド（アクションごと）** | IDE で発見可能、型安全 | メソッド数が多い |
| ビルダーパターン | チェーン可能、柔軟 | 冗長、Pydantic 標準外 |
| 生の Pydantic 構築 | 標準的な Pydantic | ネスト構造を知る必要あり |

**決定**: **クラスメソッド**

```python
PreToolUseOutput.allow()
PreToolUseOutput.deny("理由")
PreToolUseOutput.modify(updated_input={...})
PostToolUseOutput.ok()
PostToolUseOutput.block("理由")
StopOutput.block("テストを追加して")
```

### 質問 9: エラーハンドリング

**質問**: ユーザーのハンドラ関数でエラーが発生した場合の動作は？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **exit(2) + stderr** | Hook プロトコルに準拠、エラーが可視化 | Claude のフローをブロック |
| exit(1) + stderr | ワークフローをブロックしない | エラーが見逃される可能性 |
| パラメータで設定可能 | フックごとに柔軟 | API 表面積が増える |

**決定**: **exit(2) + stderr**（未捕捉例外 → ブロッキングフィードバック）

### 質問 10: CLI スキャフォールド

**質問**: 新しいフックスクリプトを生成する CLI ツールを含めるか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **CLI なし** | スコープがシンプル、早く出荷 | スキャフォールドなし |
| 最小 CLI | オンボーディングが楽 | メンテするコードが増える |
| CLI + settings.json 統合 | 完全なワークフロー | スコープが大きすぎる |

**決定**: **CLI なし**（ライブラリ品質に集中）

---

## ラウンド 4: tool_input 型、テスト、命名

### 質問 11: tool_input の型付け

**質問**: PreToolUse/PostToolUse の tool_input をどう型付けするか？各ツール（Bash, Write, Edit 等）で入力スキーマが異なる。

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **dict[str, Any] + 型付きヘルパー** | 未知/MCP ツールに柔軟、既知ツールには型あり | 型付きアクセスが 2 ステップ |
| 判別共用体 | 1 ステップの型付きアクセス | Pydantic 判別ロジックが複雑 |
| 常に dict[str, Any] | シンプル | IDE 補完なし |

**決定**: **dict[str, Any] + 型付きヘルパー**

```python
# 汎用アクセス
cmd = input.tool_input.get("command")

# 型付きアクセス
bash = input.as_bash_input()
if bash:
    print(bash.command)  # str 型
```

### 質問 12: テストフレームワーク

**質問**: テスト戦略は？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **pytest + インラインフィクスチャ** | 標準的、高速 | なし |
| pytest + hypothesis | エッジケースを発見 | テストが遅い |
| pytest + スナップショット | JSON 構造の検証が簡単 | スナップショットのメンテ |

**決定**: **pytest + インラインフィクスチャ**

### 質問 13: PyPI パッケージ名

**質問**: PyPI 上のパッケージ名は？

| 選択肢 | import 名 | メリット | デメリット |
|--------|----------|---------|-----------|
| **cc-hooks-py** | `cc_hooks` | リポジトリ名と一致、Python 特有であることが明確 | やや長い |
| claude-code-hooks | `claude_code_hooks` | 自己説明的 | import パスが長い |
| cchooks | `cchooks` | 短い | 発見しにくい |

**決定**: **cc-hooks-py**（`import cc_hooks`）

---

## ラウンド 5: 実行モデルと async

### 質問 14: @hook の実行タイミング

**質問**: @hook デコレータはデコレーション時に即座に実行するか、明示的な `if __name__ == '__main__'` ガードが必要か？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **デコレーション時に自動実行** | ゼロボイラープレート | import で関数を使えない（ただし `__main__` チェックで対応可能） |
| 明示的な `run()` が必要 | import/テスト可能 | 追加の 1 行 |
| スマート検出 | 両方の良いところ | フレーム検査のマジック |

**決定**: **自動実行**（`__main__` のときだけ実行、import 時は実行しない）

### 質問 15: セッション停止制御

**質問**: `continue` と `stopReason` の汎用出力フィールド（Claude の処理全体を停止できる）をどう扱うか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **別メソッド: `Output.stop_session(reason)`** | 誤って発火しにくい、意図が明確 | メソッドが増える |
| 既存メソッドのパラメータ | メソッド数が少ない | 見逃しやすい |
| 無視（危険すぎる） | 安全 | API が不完全 |

**決定**: **`Output.stop_session(reason)`**（セッション停止用の専用メソッド）

### 質問 16: async サポート

**質問**: 非同期ハンドラをサポートするか？

**背景**: Claude Code の Hook 設定には `"async": true` フラグがあり、フックをバックグラウンドで実行できる。Python スクリプト内で httpx 等の async ライブラリを使いたい場面がある。

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| sync のみ | シンプル | await できない |
| **sync/async 両対応** | httpx 等の async ライブラリを使える | 若干の複雑化 |

**決定**: **sync/async 両対応**（`asyncio.iscoroutinefunction()` で自動検出、`asyncio.run()` で実行）

```python
# sync ハンドラ - OK
@hook("PreToolUse")
def handle_sync(input: PreToolUseInput) -> PreToolUseOutput:
    return PreToolUseOutput.allow()

# async ハンドラ - も OK
@hook("PostToolUse")
async def handle_async(input: PostToolUseInput) -> PostToolUseOutput:
    await notify_slack(input.tool_name)
    return PostToolUseOutput.ok()
```

---

## ラウンド 6: ツール型とバージョニング

### 質問 17: ツール型のカバー範囲

**質問**: tool_input の型付きヘルパーとして、どのツールまで型定義を提供するか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| Built-in ツールのみ | 実用的、安定したスキーマ | MCP ツールは型なし |
| Built-in + 主要 MCP ツール | 幅広いカバー | MCP ツールは多様でメンテが大変 |
| **Built-in + カスタム型登録 API** | 拡張可能 | 登録 API の設計が必要 |

**決定**: **Built-in 10 ツール + `register_tool_input()` API**

### 質問 18: バージョニング

**質問**: バージョニング戦略は？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| SemVer + CalVer ハイブリッド | 標準的 | なし |
| **0.x で素早くリリース** | API を柔軟に磨ける | 利用者は不安定さを覚悟 |
| 1.0.0 から開始 | 利用者に安心感 | API 変更がしにくい |

**決定**: **0.x**（0.1.0 から開始、安定したら 1.0.0 へ）

---

## ラウンド 7: カスタムツール型登録 API

### 質問 19: カスタムツール型の登録方法

**質問**: カスタム MCP ツールの型をどう登録するか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **関数ベースの登録** | シンプル、明示的 | 毎回呼ぶ必要 |
| デコレータベース | 宣言的 | デコレータの読み込み順依存 |
| Generic 型パラメータ | 登録不要、柔軟 | ツール名との紐付けがない |

**決定**: **関数ベース `register_tool_input()`**

```python
from cc_hooks import register_tool_input

class SlackPostInput(BaseModel):
    channel: str
    text: str

register_tool_input("mcp__slack__post_message", SlackPostInput)
```

---

## ラウンド 8: Spec レビュー（前方互換性・エイリアス・None 返却）

### 質問 20: 未知フィールドの扱い

**質問**: Claude Code が将来新しいフィールドを追加した場合の挙動は？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **`extra='allow'`** | 前方互換性、将来の更新で壊れない | 未知フィールドに型がない |
| `extra='ignore'` | クリーン | 新フィールドがライブラリ更新までアクセス不可 |

**決定**: **`extra='allow'`**

### 質問 21: JSON エイリアス戦略

**質問**: Claude Code の stdin/stdout は camelCase（hookSpecificOutput, permissionDecision）だが、Python は snake_case が標準。

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **snake_case フィールド + camelCase alias** | Python 流 + JSON 互換 | alias 設定が必要 |
| camelCase そのまま | JSON と同じ | Python の命名規約に反する |

**決定**: **snake_case フィールド + camelCase alias**（`model_dump(by_alias=True)` で切り替え）

### 質問 22: None 返却の許可

**質問**: ハンドラ関数が None を返す（何も出力しない）ことを許可するか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **None 許可** | ログ専用フックが簡潔に書ける | 型ヒントが `Output \| None` になる |
| Output 必須 | 型安全 | ログだけの場合も `.ok()` が必要 |

**決定**: **None 許可**

```python
@hook("PostToolUse")
def handle(input: PostToolUseInput) -> None:
    # ログだけ取って何も返さない → stdout 空、exit(0)
    with open("/tmp/hook.log", "a") as f:
        f.write(f"{input.tool_name}\n")
```

---

## ラウンド 9: テスタビリティ

### 質問 23: テストでのハンドラ直接呼び出し

**質問**: @hook が auto-execute なので、テストで handler(mock_input) を直接呼びたい場合はどうするか？

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **@hook は関数をそのまま返す** | ゼロコストでテスタブル | なし |
| 別途 `run()` 関数も提供 | 明示的な実行ポイントも選べる | API が 2 つ |

**決定**: **`@hook` は関数をそのまま返す**（`__main__` チェックで auto-execute、import 時は実行されない）

```python
# テストコード
from hook_script import handle  # 実行されない

def test_deny_rm():
    mock = PreToolUseInput(...)
    result = handle(mock)  # 直接呼び出し
    assert result.hook_specific_output.permission_decision == "deny"
```

---

## 全決定事項サマリー

| # | 項目 | 決定 |
|---|------|------|
| 1 | 型システム | Pydantic v2（hard dependency） |
| 2 | Python バージョン | 3.12+ |
| 3 | ヘルパー API | `@hook("EventName")` デコレータ |
| 4 | イベントスコープ | 全 15 イベント |
| 5 | パッケージ構造 | モジュラー分割 |
| 6 | 配布 | PyPI (`cc-hooks-py`) + GitHub + uv |
| 7 | Output API | クラスメソッド (`.allow()`, `.deny()`, `.block()`) |
| 8 | エラーハンドリング | exit(2) + stderr |
| 9 | CLI | なし |
| 10 | 実行モデル | デコレーション時に自動実行（`__main__` チェック） |
| 11 | セッション停止 | `Output.stop_session(reason)` |
| 12 | async サポート | sync/async 両対応 |
| 13 | ツール型 | Built-in 10 ツール + `register_tool_input()` |
| 14 | バージョニング | 0.x（0.1.0 開始） |
| 15 | 未知フィールド | `extra='allow'`（前方互換） |
| 16 | エイリアス | snake_case + camelCase alias |
| 17 | None 返却 | 許可 |
| 18 | カスタム型登録 | `register_tool_input()` 関数ベース |
| 19 | テスタビリティ | `@hook` は関数をそのまま返す |
