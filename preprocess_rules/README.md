# メール前処理・データ準備ツール

メールデータの取得から前処理までを自動化するPythonツール群です。Gmail IMAPを使用してメールを取得し、ルールベースでのフィルターにより個人情報のマスク処理などの前処理を行います。

## 主な機能

- Gmail IMAPによるメール取得
- ルールベースでの個人情報自動マスク処理
  - 正規表現パターンによる柔軟なフィルタリング
  - カスタマイズ可能なマスクルール
- 設定ファイルによる柔軟なカスタマイズ

## ディレクトリ構成

```
./
├── README.md                          # 本ドキュメント
├── get_mail_imap.py                   # メール取得スクリプト
├── mask_mail_texts.py                 # マスク処理スクリプト
├── rule_config_sample.json            # 設定テンプレート
├── rule_config.json                   # 実際の設定ファイル（非Git管理）
├── masked.log                         # マスキングログ（非Git管理）
├── mail_data/                         # 生メールデータ（非Git管理）
└── mail_mask/                         # マスク済みデータ（非Git管理）
```

## システム要件

- Python 3.6以上
- 必要なライブラリ
  ```bash
  pip install imapclient
  ```

## セットアップ手順

1. 設定ファイルの準備
   ```bash
   cp rule_config_sample.json rule_config.json
   ```

2. `rule_config.json`ファイルの編集
   ```json
   {
     "email_address": "your-email@gmail.com",
     "email_password": "your-app-password",
     "date_since": "01-Jul-2025",
     "max_mails": 10,
     "label_name": "",
     "save_dir": "./mail_data",
     "masked_dir": "./mail_mask"
   }
   ```

## 使い方

1. メールの取得
   ```bash
   python get_mail_imap.py
   ```

2. マスク処理の実行（ルールベースフィルター適用）
   ```bash
   python mask_mail_texts.py
   ```

## 設定項目の詳細

| 設定項目 | 説明 | デフォルト値 |
|---------|------|-------------|
| email_address | Gmailアドレス | 必須 |
| email_password | アプリパスワード | 必須 |
| date_since | 取得開始日 | 01-Jul-2025 |
| max_mails | 最大取得件数 | 10 |
| label_name | 対象ラベル | 空（INBOX） |
| save_dir | 生メール保存先 | ./mail_data |
| masked_dir | マスク後保存先 | ./mail_mask |

## マスク処理の仕組み

ルールベースのフィルタリングシステムにより、以下のような個人情報を自動的に検出・マスク処理します：
- メールアドレス
- 電話番号
- 個人名
- その他設定可能な正規表現パターン

## Gmailアプリパスワードの取得方法

1. [Googleアカウント設定](https://myaccount.google.com/)で2段階認証を有効化
2. セキュリティ → アプリパスワードを選択
3. アプリ:「メール」、デバイス:「その他」で生成
4. 生成されたパスワードを`rule_config.json`の`email_password`に設定

## トラブルシューティング

認証エラーの場合:
- アプリパスワードの確認
- 2段階認証の有効化確認

メール取得エラーの場合:
- 日付形式の確認（DD-MMM-YYYY）
- ネットワーク接続の確認

## プロジェクトとの連携

他のモジュールからは以下のシンボリックリンクでアクセス:
- `../shared_mail_data` → `./mail_data/`
- `../shared_mail_mask` → `./mail_mask/`

## ライセンス

MIT License
