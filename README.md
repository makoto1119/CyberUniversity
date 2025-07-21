# CyberUniversity - 卒業研究リポジトリ

本リポジトリは、サイバー大学 卒業研究「テキストマイニングによるメール本文の分類実験」に関する成果物を整理したものです。
目的は、自然言語処理によるメール本文の自動分類処理と、ゆらぎ吸収・精度向上のための前処理技術の検証です。

---

## ディレクトリ構成

＊.gitignore で除外しているファイル・ディレクトリも含んでいます

```
./
├── README.md                                # リポジトリ全体の説明ファイル（本ファイル）
├── classification_ml/                       # 分類モデル関連のディレクトリ
│   ├── README.md                            # モデルの詳細説明
│   ├── features_tfidf/                      # TF-IDF特徴量データ
│   │   ├── mail_morphological_001.json 〜 100.json  # 形態素解析済みデータのTF-IDF特徴量
│   │   └── tfidf_vectorizer.pkl             # TF-IDFベクトル化モデル
│   ├── features_word2vec/                   # Word2Vec特徴量データ
│   │   ├── mail_morphological_001.json 〜 100.json  # 形態素解析済みデータのWord2Vec特徴量
│   │   └── word2vec.model                   # 学習済みWord2Vecモデル
│   ├── labels.csv                           # 教師データのラベル
│   ├── model_config.json                    # モデル設定ファイル
│   ├── models/                              # 学習用スクリプトディレクトリ
│   │   ├── compare_features_and_models.py   # 特徴量とモデルの組み合わせ評価スクリプト
│   │   ├── config_loader.py                 # モデル設定ファイル読み込みモジュール
│   │   ├── generate_tfidf.py                # TF-IDF特徴量生成スクリプト
│   │   └── generate_word2vec.py             # Word2Vec特徴量生成スクリプト
│   ├── results/                             # 評価結果
│   │   ├── sample_evaluation_summary.txt    # サンプル用の評価結果サマリーレポート
│   │   └── sample_feature_comparison.csv    # サンプル用の特徴量・性能比較データ
│   └── run_evaluation.sh*                   # 評価実行スクリプト
├── preprocess_nlp/                          # 自然言語処理（形態素解析・表記ゆれ）ツール
│   ├── README.md                            # 処理の詳細説明
│   ├── fuzzy_normalize.py*                  # テキスト正規化スクリプト
│   ├── fuzzy_patterns.json                  # 正規化パターン定義ファイル
│   ├── stopwords.txt                        # 形態素解析時のストップワード定義ファイル
│   ├── texts_fuzzy/                         # 表記ゆれ正規化済みテキストデータ
│   ├── texts_tokenize/                      # 形態素解析済みテキストデータ
│   │   └── mail_morphological_001.txt 〜 100.txt
│   └── tokenize_texts.py*                   # 形態素解析処理スクリプト
├── preprocess_rules/                        # サンプルデータ作成（取得・マスク）の処理群
│   ├── README.md                            # 処理の詳細説明
│   ├── config                               # 自分の環境で実際に使用している config (.gitignore対象)
│   ├── config_sample                        # 公開用の設定テンプレート
│   ├── get_mail_imap.py*                    # GmailからメールをIMAP経由で取得するスクリプト
│   ├── mail_data/                           # マスク前の実メールデータ (.gitignore対象)
│   │   └── mail_data_001.txt 〜 100.txt
│   ├── mail_mask/                           # 個人情報などマスク済みのメールデータ(.gitignore対象)
│   │   └── mail_mask_001.txt 〜 100.txt
│   ├── mask_mail_texts.py*                  # テキスト中の情報をマスク処理するスクリプト
│   └── masked.log                           # マスキング処理の置換ログ（件数・種別など）(.gitignore対象)
├── sample_mail_masked10/                    # 実データは動的に変動してしまうため、サンプル開示用
│   ├── README.md                            # サンプルデータについての README
│   └── mail_data_001.txt 〜 010.txt         # サンプルデータ（10件）
├── sample_program/                          # サンプルプログラム
│   ├── README.md                            # プログラムの説明
│   ├── ch1/                                 # 第1章：Pythonの基礎
│   ├── ch2/                                 # 第2章：データの扱い方
│   ├── ch3/                                 # 第3章：データの可視化
│   ├── ch4/                                 # 第4章：自然言語処理の基礎
│   ├── ch5/                                 # 第5章：機械学習の基礎
│   └── ch6/                                 # 第6章：実践的な機械学習
├── shared_mail_data -> preprocess_rules/mail_data/               # データ共有用シンボリックリンク
├── shared_mail_mask -> preprocess_rules/mail_mask/               # データ共有用シンボリックリンク
├── shared_results -> classification_ml/results/                  # 結果共有用シンボリックリンク
├── shared_texts_fuzzy -> preprocess_nlp/texts_fuzzy/             # 正規化テキスト共有用シンボリックリンク
└── shared_texts_tokenize -> preprocess_nlp/texts_tokenize/       # 形態素解析テキスト共有用シンボリックリンク
```

## .gitignore 

```
$ cat .gitignore 

# for this project
config
*.log
mail_data/
mail_mask/
texts_fuzzy/
texts_tokenize/
features_word2vec/
features_tfidf/
evaluation_summary.txt
feature_model_comparison.csv
old/
tmp/

以下略 (以降は一般的なignore設定)
```

## サンプルコード
- 元リポジトリ: https://github.com/kujirahand/book-mlearn-gyomu
- 書籍: 「Pythonによる AI・機械学習・深層学習アプリのつくり方」
- 取得範囲: 第4章〜第6章のサンプルコード（ch4〜ch6）
- 詳細な説明や使用方法については、ディレクトリ内のREADMEと元リポジトリのREADMEを参照してください

---

## 実験内容の概要

- Gmail から IMAP 経由でのメール取得、件名のデコード・改行統一
- 正規表現と辞書ベースによる情報マスキング（氏名・企業名・URL 等）
- 形態素解析（Janome）による語彙抽出・正規化・フィルタ処理
- 特徴量抽出：
  - Word2Vec（単純平均ベクトル）
  - TF-IDF（スパースベクトル）
- 複数の分類モデルによる自動分類実験：
  - Logistic Regression / SVM / Random Forest / Naive Bayes
- 分類精度の評価：F1スコアを中心に、分類レポートや混同行列などの指標で性能を分析（現時点では F1スコアを主軸に比較）
- 実験設定（ベクトル化・モデルパラメータ）をすべて `model_config.json` に集約
- それぞれの精度あげが最終的なF1スコアに繋がるはずなので、個別に精度あげできるよう調整

---

## 今後の予定

- 自作マスキング・フィルターの改善と誤検出率の低減
- 表記ゆらぎ吸収ルール（正規化パターン）の追加・精度向上
- TF-IDF 加重 Word2Vec の導入による特徴量の意味性強化
- 教師あり学習におけるモデル精度の向上とチューニング
- 今回検証できていない分類モデルなど別アプローチとの性能比較
- F1スコアを指標とした教師あり分類モデルの継続的な最適化
- LLM（ChatGPT など）との併用による分類補助・事後検証の試行

