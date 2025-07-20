#!/bin/bash
# メール分類モデルの評価を実行するスクリプト

echo "===== メール分類モデル評価の開始 ====="
echo

# jqコマンドの確認
if ! command -v jq &> /dev/null; then
    echo "エラー: jqコマンドが見つかりません"
    echo "インストール方法: brew install jq"
    exit 1
fi

# 設定ファイルの確認と入力ディレクトリの表示
if [ ! -f model_config.json ]; then
    echo "エラー: model_config.json が見つかりません"
    exit 1
fi

data_source=$(jq -r '.input.data_source' model_config.json)
input_path=$(jq -r ".input.data_paths.$data_source" model_config.json)
echo "データソース: $data_source"
echo "入力パス: $input_path"
echo

echo "----------------------------------------"
echo "1. Word2Vec特徴量の生成"
echo "実行: python models/generate_word2vec.py"
echo "----------------------------------------"
python models/generate_word2vec.py
echo

echo "----------------------------------------"
echo "2. TF-IDF特徴量の生成"
echo "実行: python models/generate_tfidf.py"
echo "----------------------------------------"
python models/generate_tfidf.py
echo

echo "----------------------------------------"
echo "3. 特徴量とモデルの比較"
echo "実行: python models/compare_features_and_models.py"
echo "----------------------------------------"
python models/compare_features_and_models.py
echo

echo "===== 評価完了 ====="
echo "結果は ./results ディレクトリに保存されました"
echo "評価結果サマリー: ./results/evaluation_summary.txt"
echo "特徴量とモデルの比較: ./results/feature_model_comparison.csv"
echo "----------------------------------------"
