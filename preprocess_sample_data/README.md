# メール前処理・データ準備ツール

Gmail IMAPを使用してメールを取得し、マスク処理、形態素解析などの前処理を行うPythonスクリプト群。

---

## ディレクトリ構成

```
preprocess_sample_data/
├── README.md                          # このファイル
├── get_mail_imap.py*                  # GmailからメールをIMAP経由で取得するスクリプト
├── mask_mail_texts.py*                # テキスト中の情報をマスク処理するスクリプト
├── morphological_mail_texts.py*       # 形態素解析まわりを処理するスクリプト
├── zip_mail_data.sh*                  # 元データを ZIP 圧縮するシェルスクリプト
├── zip_mail_mask.sh*                  # マスクデータを ZIP 圧縮するシェルスクリプト
├── config_sample                      # 公開用の設定テンプレート
├── config                             # 実際の設定ファイル (.gitignore対象)
├── stopwords.txt                      # 日本語ストップワード一覧
├── masked.log                         # マスキング処理の置換ログ（件数・種別など）(.gitignore対象)
├── mail_data/                         # マスク前の実メールデータ (.gitignore対象)
│   ├── mail_data_001.txt 〜 mail_data_100.txt
├── mail_mask/                         # 個人情報などマスク済みのメールデータ(.gitignore対象)
│   ├── mail_mask_001.txt 〜 mail_mask_100.txt
└── mail_morphological/                # 形態素解析済みのメールデータ (.gitignore対象)
    ├── mail_morphological_001.txt 〜 mail_morphological_100.txt
```

## プロジェクト全体との関連

このディレクトリは卒業研究プロジェクト「テキストマイニングによるメール本文の分類実験」の一部として、以下の役割を担っています：

1. メールデータの取得と前処理
2. 個人情報のマスク処理
3. 形態素解析による単語分割

処理済みデータは、プロジェクトのルートディレクトリにあるシンボリックリンク経由で他の処理モジュールからも参照できます：
- `../shared_mail_mask` → `./mail_mask/`
- `../shared_mail_morphological` → `./mail_morphological/`

## 機能

- Gmail IMAPサーバーに接続してメールを取得
- 指定した日付以降のメールをフィルタリング
- 個人情報などをマスク処理
- 形態素解析による単語分割と品詞タグ付け
- ストップワード除去
- 設定ファイルによる柔軟な設定管理

## 必要な環境

- Python 3.6以上
- 必要なライブラリ：
  - `imapclient` (メール取得用)
  - `janome` (形態素解析用)

## インストール

```bash
$ pip install imapclient janome
```

## 設定

1. `config_sample`を`config`にコピー
2. `config`ファイルを編集して以下の項目を設定：

```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
DATE_SINCE=01-Jul-2025
MAX_MAILS=10
LABEL_NAME=
SAVE_DIR=./mail_data
MASKED_DIR=./mail_mask
MORPHOLOGICAL_DIR=./mail_morphological
STOPWORDS_PATH=./stopwords.txt
ENABLE_POS_FILTER=true
ENABLE_BASE_FORM=true
```

### 設定項目

| 項目 | 説明 | デフォルト値 | 使用プログラム |
|------|------|-------------|---------------|
| `EMAIL_ADDRESS` | Gmailアドレス | 必須 | get_mail_imap.py |
| `EMAIL_PASSWORD` | Gmailアプリパスワード | 必須 | get_mail_imap.py |
| `DATE_SINCE` | 取得開始日 | 01-Jul-2025 | get_mail_imap.py |
| `MAX_MAILS` | 最大取得件数 | 10 | get_mail_imap.py |
| `LABEL_NAME` | 取得対象ラベル | 空（INBOX） | get_mail_imap.py |
| `SAVE_DIR` | 生メール保存先 | ./mail_data | get_mail_imap.py |
| `MASKED_DIR` | マスク済み保存先 | ./mail_mask | mask_mail_texts.py |
| `MORPHOLOGICAL_DIR` | 形態素解析結果保存先 | ./mail_morphological | morphological_mail_texts.py |
| `STOPWORDS_PATH` | ストップワードファイル | ./stopwords.txt | morphological_mail_texts.py |
| `ENABLE_POS_FILTER` | 品詞フィルター有効/無効 | true | morphological_mail_texts.py |
| `ENABLE_BASE_FORM` | 原形正規化有効/無効 | true | morphological_mail_texts.py |

### 形態素解析オプション

#### 品詞フィルター（ENABLE_POS_FILTER）
- `true`: 名詞・動詞・形容詞のみを抽出
- `false`: 全品詞を対象とする

#### 原形正規化（ENABLE_BASE_FORM）
- `true`: 単語を原形（base_form）に正規化（例: "走った" → "走る"）
- `false`: 表層形（surface）をそのまま使用（例: "走った" → "走った"）

#### 実験パターン例
| 品詞フィルター | 原形正規化 | 効果 |
|---------------|-----------|------|
| true | true | 名詞・動詞・形容詞の原形のみ（推奨） |
| true | false | 名詞・動詞・形容詞の表層形 |
| false | true | 全品詞の原形 |
| false | false | 全品詞の表層形 |

### ラベル指定について

`LABEL_NAME`を設定することで、特定のラベルが付いたメールのみを取得可能。

- 空の場合：INBOX（受信トレイ）からメールを取得
- ラベル名を指定：そのラベルが付いたメールを取得

**注意**: 指定したラベルが存在しない場合は、自動的にINBOXが使用される。

## Gmailアプリパスワードの設定

**重要**: Gmailの通常のログインパスワードではなく、専用の「アプリパスワード」が必要。アプリパスワードは16文字のランダムな文字列で、サードパーティアプリがGoogleサービスにアクセスするために使用する。

### アプリパスワード作成手順

1. **2段階認証を有効にする**
   - [Googleアカウント設定](https://myaccount.google.com/)にアクセス
   - 「セキュリティ」タブを選択
   - 「2段階認証プロセス」を有効にする

2. **アプリパスワードを生成する**
   - 同じく「セキュリティ」タブで「アプリパスワード」を選択
   - アプリを選択：「メール」
   - デバイスを選択：「その他（カスタム名）」→「PythonScript」など
   - 「生成」をクリック
   - 表示された16文字のパスワードをコピー

3. **設定ファイルに追加**
   - 生成されたアプリパスワードを`config`ファイルの`EMAIL_PASSWORD`に設定
   - スペースは含めずに入力

### 参考リンク
- [Googleアプリパスワード公式ガイド](https://support.google.com/accounts/answer/185833)
- [2段階認証の設定方法](https://support.google.com/accounts/answer/185839)
- [アプリパスワードのトラブルシューティング](https://support.google.com/mail/answer/185833)

## 使用方法

### 1. メール取得
```bash
python get_mail_imap.py
```

### 2. 個人情報マスク処理
```bash
python mask_mail_texts.py
```

### 3. 形態素解析・ストップワード除去
```bash
python morphological_mail_texts.py
```

### 4. データ圧縮（必要に応じて）
```bash
./zip_mail_data.sh    # 元データを圧縮
./zip_mail_mask.sh    # マスク済みデータを圧縮
```

## 処理フロー

```
1. Gmail (IMAP) → get_mail_imap.py → 生メール (SAVE_DIR)
2. 生メール → mask_mail_texts.py → マスク済みメール (MASKED_DIR)
3. マスク済みメール → morphological_mail_texts.py → 形態素解析済みメール (MORPHOLOGICAL_DIR)
4. [オプション] 表記ゆれ正規化 → ../preprocess_fuzzy/normalize_text.py → 正規化済みテキスト
```

## 出力ファイル

- ファイル名：`mail_data_001.txt`, `mail_data_002.txt`, ...（生メール）
- ファイル名：`mail_mask_001.txt`, `mail_mask_002.txt`, ...（マスク済み）
- ファイル名：`mail_morphological_001.txt`, `mail_morphological_002.txt`, ...（形態素解析済み）
- 形式：
  ```
  Subject: メールの件名

  メール本文
  ```

## .gitignore設定

機密情報や不要なファイルをバージョン管理から除外するため、以下を.gitignoreに追加：

```
# for this project
config
*.log
mail_data/
mail_mask/
mail_morphological/
```

## トラブルシューティング

### 認証エラーが発生する場合
- アプリパスワードが正しく設定されているか確認
- 2段階認証が有効になっているか確認

### メールが取得できない場合
- `DATE_SINCE`の日付形式が正しいか確認（DD-MMM-YYYY形式）
- ネットワーク接続を確認

### マスク処理が不十分な場合
- `mask_mail_texts.py`の正規表現パターンを確認・追加

## 参考資料・出典

### 日本語ストップワード一覧
- ファイル: `stopwords.txt`
- 出典: https://github.com/stopwords-iso/stopwords-ja
- 用途: 形態素解析後のストップワード除去処理で使用

## ライセンス

このプロジェクトはMITライセンスの下で公開しています。
