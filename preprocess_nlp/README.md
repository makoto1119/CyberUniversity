# 自然言語処理（NLP）前処理ツール

テキストの自然言語処理（NLP）のための前処理ツールセット。形態素解析による分かち書き処理と表記ゆれの正規化を提供します。

---

## 概要

このツールセットは以下の2つの主要な処理を提供します：

1. **形態素解析処理**
   - Janomeライブラリによる日本語テキストの分かち書き
   - 品詞情報の付与
   - ストップワードの除去
   - トークン化（単語分割）

2. **テキスト正規化処理**
   - 表記ゆれの統一
   - 文字種の正規化（全角・半角の統一）
   - 特殊文字の処理

## ディレクトリ構成

```
preprocess_nlp/
├── README.md              # このドキュメント
├── nlp_config.json # 設定ファイル
├── fuzzy_normalize.py     # テキスト正規化スクリプト
├── fuzzy_patterns.json    # 正規化パターン定義ファイル
├── tokenize_texts.py      # 形態素解析・トークン化スクリプト
├── stopwords.txt         # ストップワード定義ファイル
├── texts_fuzzy/          # 正規化処理用テキストディレクトリ
└── texts_tokenize/       # トークン化処理用テキストディレクトリ
```

## 設定ファイル（nlp_config.json）

プログラムの設定は `nlp_config.json` で管理されています：

```json
{
    "process_input": {
        "value": {
            "tokenize": "../shared_mail_mask",
            "fuzzy": "texts_tokenize"
        },
        "description": "各処理の入力元ディレクトリ"
    },
    "process_output": {
        "value": {
            "tokenize": "texts_tokenize",
            "fuzzy": "texts_fuzzy"
        },
        "description": "各処理の出力先ディレクトリ"
    }
}
```

主な設定項目：
- process_input: 各処理の入力元ディレクトリ
- process_output: 各処理の出力先ディレクトリ
- fuzzy_patterns_file: 正規化パターン定義ファイル
- stopwords_file: ストップワード定義ファイル
- default_pos_filter: デフォルトの品詞フィルター

## 必要な環境

- Python 3.6以上
- 必要なライブラリ：
  - `janome`: 日本語形態素解析
  - `pathlib`: パス操作（Python 3.6以上では標準ライブラリ）
  - `json`（標準ライブラリ）
  - `re`（標準ライブラリ）
  - `argparse`（標準ライブラリ）
  - `os`（標準ライブラリ）

```bash
pip install janome
```

## 処理フロー

デフォルトの処理フロー：
```
マスク済みメールデータ（../shared_mail_mask/）
       ↓
形態素解析・トークン化（tokenize_texts.py）
       ↓
トークン化済みテキスト（texts_tokenize/）
       ↓
テキスト正規化処理（fuzzy_normalize.py）
       ↓
正規化済みテキスト（texts_fuzzy/）
```

処理順序は `nlp_config.json` の `process_input` の設定を変更することで変更可能です：

1. デフォルト順序（形態素解析 → 正規化）:
```json
"process_input": {
    "value": {
        "tokenize": "../shared_mail_mask",
        "fuzzy": "texts_tokenize"
    }
}
```

2. 逆順（正規化 → 形態素解析）:
```json
"process_input": {
    "value": {
        "fuzzy": "../shared_mail_mask",
        "tokenize": "texts_fuzzy"
    }
}
```

## 形態素解析処理（tokenize_texts.py）

### 基本的な使い方

```bash
# デフォルト設定で実行
python tokenize_texts.py

# 入力/出力ディレクトリを指定して実行
python tokenize_texts.py --indir ../shared_mail_mask --outdir texts_tokenize
```

### オプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--config` | 設定ファイルのパス | nlp_config.json |
| `--indir` | 入力ディレクトリのパス | 設定ファイルの値 |
| `--outdir` | 出力ディレクトリのパス | 設定ファイルの値 |
| `--stopwords` | ストップワードファイルのパス | 設定ファイルの値 |
| `--pos-filter` | 抽出する品詞（カンマ区切り） | 設定ファイルの値 |

## テキスト正規化処理（fuzzy_normalize.py）

### 正規化の処理順序

正規化処理は以下の順序で実行されます：

1. 技術用語の保護（technical_terms.jsonを使用）
   - 定義された技術用語を一時的なプレースホルダーに置換
   - カタカナの正規化から保護するため

2. 数字の正規化
   - 全角数字を半角数字に変換
   - 例：「１２３」→「123」

3. カタカナのひらがな化
   - カタカナをひらがなに変換
   - 例：「コンピュータ」→「こんぴゅーた」
   - ただし、technical_terms.jsonで定義された用語は変換されない

4. パターンによる正規化（fuzzy_patterns.jsonを使用）
   - 定義された置換パターンに基づいて文字列を変換
   - 例：「でございます」→「です」
   - 敬語表現の統一なども含む

5. 保護した技術用語の復元
   - 手順1で置換した技術用語を元に戻す
   - カタカナのまま保持される

これらの処理は nlp_config.json の normalize_params で制御できます：
```json
"normalize_params": {
    "value": {
        "enable_number_normalize": true,
        "enable_kana_normalize": true
    }
}
```

### 基本的な使い方

```bash
# デフォルト設定で実行
python fuzzy_normalize.py

# 入力/出力ディレクトリを指定して実行
python fuzzy_normalize.py --indir texts_tokenize --outdir texts_fuzzy
```

### オプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--config` | 設定ファイルのパス | nlp_config.json |
| `--indir` | 入力ディレクトリのパス | 設定ファイルの値 |
| `--outdir` | 出力ディレクトリのパス | 設定ファイルの値 |

## トラブルシューティング

### Janome形態素解析の問題
- 品詞フィルターの設定が適切か確認
  - デフォルトでは名詞、動詞、形容詞を抽出
  - 必要に応じて品詞フィルターを調整
- ストップワードの設定を確認
  - stopwords.txtの内容が適切か確認
  - 必要に応じてストップワードを追加・削除

### 正規化の問題
- パターン定義が正しいか確認
- 正規表現の構文が有効か確認
- パターンの優先順位を確認

## 今後の拡張予定

- Janomeの機能拡張
  - カスタム辞書対応
  - 品詞フィルターの詳細設定
  - 解析結果の統計情報出力
- テキスト処理の機能強化
  - バッチ処理機能
  - 並列処理による高速化
  - 解析結果の可視化

## ライセンス

このプロジェクトはMITライセンスの下で公開しています。
