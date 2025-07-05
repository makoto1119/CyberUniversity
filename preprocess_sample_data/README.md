# Gmail IMAP メール取得ツール

Gmail IMAPを使用してメールを取得し、ローカルにテキストファイルとして保存するPythonスクリプト。

## 機能

- Gmail IMAPサーバーに接続してメールを取得
- 指定した日付以降のメールをフィルタリング
- 件名と本文をテキストファイルとして保存
- 設定ファイルによる柔軟な設定管理

## 必要な環境

- Python 3.6以上
- 必要なライブラリ：
  - `imapclient`

## インストール

```bash
$ pip install imapclient
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
SAVE_DIR=./mails
```

### 設定項目

| 項目 | 説明 | デフォルト値 |
|------|------|-------------|
| `EMAIL_ADDRESS` | Gmailアドレス | 必須 |
| `EMAIL_PASSWORD` | Gmailアプリパスワード | 必須 |
| `DATE_SINCE` | 取得開始日 | 01-Jul-2025 |
| `MAX_MAILS` | 最大取得件数 | 10 |
| `LABEL_NAME` | 取得対象ラベル | 空（INBOX） |
| `SAVE_DIR` | 保存先ディレクトリ | ./mails |

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

```bash
python get_mail_imap.py
```

実行すると：
1. 設定ファイルから認証情報を読み込み
2. Gmail IMAPサーバーに接続
3. 指定条件のメールを取得
4. `SAVE_DIR`で指定したディレクトリに保存

## 出力ファイル

- ファイル名：`mail_001.txt`, `mail_002.txt`, ...
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
mails/
```

## 注意事項

- Gmailの通常パスワードではなく、アプリパスワードを使用すること
- `config`ファイルには機密情報が含まれるため、バージョン管理から除外すること
- 大量のメール取得時はGmailのAPI制限に注意

## ファイル構成

```
.
├── README.md              # このファイル
├── get_mail_imap.py       # メイン実行スクリプト
├── config_sample          # 設定ファイルのサンプル
├── config                 # 実際の設定ファイル（要作成）
└── mails/                 # メール保存ディレクトリ（自動作成）
```

## トラブルシューティング

### 認証エラーが発生する場合
- アプリパスワードが正しく設定されているか確認
- 2段階認証が有効になっているか確認

### メールが取得できない場合
- `DATE_SINCE`の日付形式が正しいか確認（DD-MMM-YYYY形式）
- ネットワーク接続を確認

## ライセンス

このプロジェクトはMITライセンスの下で公開しています。
