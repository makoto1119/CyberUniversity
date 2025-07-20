#!/bin/bash

# エラーが発生したら停止
set -e

echo "NLP前処理を開始します..."

# 出力ディレクトリをクリーンアップ
echo "出力ディレクトリをクリーンアップ中..."
rm -rf texts_tokenize texts_fuzzy

# 形態素解析の実行
echo "形態素解析を実行中..."
python tokenize_texts.py

# テキスト正規化の実行
echo "テキスト正規化を実行中..."
python fuzzy_normalize.py

echo "前処理が完了しました"
