# CyberUniversity - 卒業研究リポジトリ

本リポジトリは、サイバー大学 卒業研究「テキストマイニングによるメール本文の分類実験」に関する成果物を整理したものです。
目的は、自然言語処理によるメール本文の自動分類処理と、ゆらぎ吸収・精度向上のための前処理技術の検証です。

---

## ディレクトリ構成

＊.gitignore で除外しているファイル・ディレクトリも含んでいます

```
$ tree -LFa 2 -I .git ./CyberUniversity

./CyberUniversity/
├── .gitignore                         # Git管理から除外するファイル・ディレクトリ設定
├── README.md                          # リポジトリ全体の説明ファイル（本ファイル）
├── mail_mask -> preprocess_sample_data/mail_mask/
│                                      # マスク済みメールディレクトリへのシンボリックリンク。他検証へのデータ共有
├── preprocess_fuzzy/                  
├── sample_mail_masked10/              # 実データは動的に変動してしまうため、サンプル開示用
│   ├── README.md                      # サンプルデータについての README
│   └── mail_data_001.txt 〜 mail_data_010.txt  # サンプルデータ
├── preprocess_fuzzy/
│   ├── README.md
│   ├── fuzzy_patterns.json
│   └── normalize_text.py
├── preprocess_sample_data/            # サンプルデータ作成（取得・マスク）の処理群
│   ├── README.md                      # このディレクトリ内専用の補足説明
│   ├── config                         # 自分の環境で実際に使用している config (.gitignore対象)
│   ├── config_sample                  # 公開用の設定テンプレート
│   ├── get_mail_imap.py*              # GmailからメールをIMAP経由で取得するスクリプト
│   ├── mail_data/                     # マスク前の実メールデータ (.gitignore対象)
│   ├── mail_mask/                     # マスク済みのメールデータ（個人情報など除去済）(.gitignore対象)
│   ├── mask_mail_texts.py*            # テキスト中の情報をマスク処理するスクリプト
│   ├── masked.log                     # マスキング処理の置換ログ（件数・種別など）(.gitignore対象)
│   ├── zip_mail_data.sh*              # 元データを ZIP 圧縮するシェルスクリプト
│   └── zip_mail_mask.sh*              # マスクデータを ZIP 圧縮するシェルスクリプト


```

.gitignore 内容

```
$ cat .gitignore 

# for this project
config
*.log
mail_data/
mail_mask/

以下略 (以降は一般的なignore設定)
```

---

## 実験内容の概要

- GmailからのIMAPメール取得、件名デコード、改行コード統一
- 正規表現による情報マスキング（名前・企業名・URL等）
- 処理後ログ（置換件数）の出力
- ゆらぎ表現対応のための正規化ルール設計（予定）

---

## 今後の予定

- ゆらぎ吸収ルールの作成と検証
- 教師あり分類モデル（SVMなど）の訓練と評価
- LLM（ChatGPTなど）との連携による精度改善の検討
