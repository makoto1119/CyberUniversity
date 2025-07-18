# テキスト正規化ツール（ゆらぎ処理）

自然言語処理のための前処理として、テキスト中の表記ゆれを正規化するPythonスクリプト。  

---

## ディレクトリ構成

```
preprocess_fuzzy/
├── README.md              # このドキュメント
├── normalize_text.py      # テキスト正規化スクリプト
└── fuzzy_patterns.json    # 正規化パターン定義ファイル
```


## 機能

- 定義されたパターンに基づくテキストの正規化
- 表記ゆれの統一（例：「ございます」「御座います」→「ございます」）
- 設定ファイル（JSON）による柔軟なパターン管理
- 入力ファイルと出力ファイルの指定による一括処理

## 必要な環境

- Python 3.6以上
- 必要なライブラリ：
  - `json`（標準ライブラリ）
  - `re`（標準ライブラリ）
  - `argparse`（標準ライブラリ）

## 設定

正規化パターンは `fuzzy_patterns.json` ファイルで定義されています。
このJSONファイルには、正規表現パターンとその置換先が定義されています。

### パターン定義の例

```json
{
  "patterns": [
    {
      "name": "敬語表現の統一",
      "description": "「御座います」を「ございます」に統一",
      "pattern": "御座います",
      "replacement": "ございます"
    },
    {
      "name": "数字表記の統一",
      "description": "全角数字を半角数字に統一",
      "pattern": "([０-９]+)",
      "replacement": "\\1",
      "function": "zen_to_han_digit"
    }
  ]
}
```

### パターン定義項目

| 項目 | 説明 | 必須 |
|------|------|------|
| `name` | パターンの名前 | ○ |
| `description` | パターンの説明 | ○ |
| `pattern` | 検索する正規表現パターン | ○ |
| `replacement` | 置換後のテキスト | ○ |
| `function` | 特殊な変換関数名（オプション） | × |

## 使用方法

### 基本的な使い方

```bash
python normalize_text.py --infile <入力ファイル> --outfile <出力ファイル>
```

### オプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--infile` | 入力ファイルのパス | 必須 |
| `--outfile` | 出力ファイルのパス | 必須 |
| `--patterns` | パターン定義ファイルのパス | fuzzy_patterns.json |
| `--verbose` | 詳細な処理情報を表示 | False |

### 使用例

```bash
# 基本的な使用方法
python normalize_text.py --infile mail_mask_001.txt --outfile normalized_001.txt

# 詳細情報を表示
python normalize_text.py --infile mail_mask_001.txt --outfile normalized_001.txt --verbose

# 別のパターンファイルを使用
python normalize_text.py --infile mail_mask_001.txt --outfile normalized_001.txt --patterns custom_patterns.json
```

## 処理フロー

```
マスク済みテキスト → 正規化処理 → 正規化済みテキスト
```

## ファイル構成

```
preprocess_fuzzy/
├── README.md                          # このファイル
├── normalize_text.py                  # テキスト正規化スクリプト
├── fuzzy_patterns.json                # 正規化パターン定義ファイル
└── sample_before_after/               # 変換事例サンプル
    ├── before_001.txt                 # 変換前テキスト例
    └── after_001.txt                  # 変換後テキスト例
```

## 正規化パターンの追加方法

1. `fuzzy_patterns.json` ファイルを開く
2. `patterns` 配列に新しいパターンを追加
3. 必要な項目（`name`, `description`, `pattern`, `replacement`）を設定
4. ファイルを保存

### 特殊変換関数

一部の変換では、単純な文字列置換ではなく関数による変換が必要な場合があります。
そのような場合は、`function` フィールドに関数名を指定します。

現在サポートされている特殊変換関数：

- `zen_to_han_digit`: 全角数字を半角数字に変換
- `zen_to_han_alpha`: 全角アルファベットを半角に変換
- `normalize_whitespace`: 連続する空白を1つに統一

## 正規化の例

| 変換前 | 変換後 | パターン名 |
|-------|-------|-----------|
| 御座います | ございます | 敬語表現の統一 |
| １２３４５ | 12345 | 数字表記の統一 |
| お問い合わせ | 問い合わせ | 接頭語の正規化 |
| です。  です。 | です。です。 | 空白正規化 |

## トラブルシューティング

### 正規化が適用されない場合
- パターン定義が正しいか確認
- 正規表現の構文が有効か確認

### 予期しない置換が発生する場合
- パターンの優先順位を確認（JSONファイル内の順序が適用順序）
- より具体的なパターンを先に配置

## 今後の拡張予定

- バッチ処理機能（ディレクトリ単位での処理）
- 正規化ログの出力
- パターン適用の選択的有効/無効化
- 正規化効果の統計情報出力

## ライセンス

このプロジェクトはMITライセンスの下で公開しています。
