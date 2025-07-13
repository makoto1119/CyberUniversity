# サンプルプログラム - 形態素解析

## 概要

このディレクトリには、形態素解析の学習・検証用サンプルプログラムを格納しています。
これらのプログラムは、卒業研究「テキストマイニングによるメール本文の分類実験」における前処理技術の参考として使用します。

## 出典

- 元リポジトリ: https://github.com/kujirahand/book-mlearn-gyomu/tree/master/src/ch4/Morphological_Analysis
- 書籍: 「Pythonによる AI・機械学習・深層学習アプリのつくり方」第4章の2 形態素解析

## ファイル構成
* リポジトリ内のまま配置

```
sample_program/
├── README.md                    # 本ファイル
├── Morphological_Analysis.py    # 基本的な形態素解析サンプル
├── Morphological_Analysis2.py   # NEologd辞書を使用した形態素解析
├── Morphological_Analysis3.py   # ストップワードの除去
└── mecab-test.ipynb             # Jupyter Notebook形式のMeCab動作確認
```


## 卒業研究での活用予定

- ゆらぎ吸収の検証を開始するための事前処理用として適正改変予定
- 改変後のプログラムは `preprocess_sample_data` に格納、使用予定
- ゆらぎ吸収については、別途 `preprocess_fuzzy/` ディレクトリで開発予定  

