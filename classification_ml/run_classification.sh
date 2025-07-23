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

# 全データ数とラベル付きデータ数を計算
total_data=$(ls -1 ../shared_texts_fuzzy/*.txt 2>/dev/null | wc -l)
labeled_data=$(wc -l < labels.csv)

echo "全データ数: $total_data"
echo "ラベル付きデータ数: $labeled_data"
echo

echo "----------------------------------------"
echo "1. Word2Vec特徴量の生成"
echo "実行: python models/generate_word2vec.py"
echo "----------------------------------------"
if ! python models/generate_word2vec.py; then
    echo "エラー: Word2Vec特徴量の生成に失敗しました"
    exit 1
fi
echo

echo "----------------------------------------"
echo "2. TF-IDF特徴量の生成"
echo "実行: python models/generate_tfidf.py"
echo "----------------------------------------"
if ! python models/generate_tfidf.py; then
    echo "エラー: TF-IDF特徴量の生成に失敗しました"
    exit 1
fi
echo

echo "----------------------------------------"
echo "3. 特徴量とモデルの比較"
echo "実行: python models/compare_features_and_models.py"
echo "----------------------------------------"
if ! python models/compare_features_and_models.py; then
    echo "エラー: 特徴量とモデルの比較に失敗しました"
    exit 1
fi
echo

echo "===== 評価完了 ====="
echo "結果は ./results ディレクトリに保存されました"
echo "評価結果サマリー: ./results/evaluation_summary.txt"
echo "特徴量とモデルの比較: ./results/feature_model_comparison.csv"
echo ""
if [ -f "./results/classification_history.csv" ]; then
    echo "実験履歴: ./results/classification_history.csv"
    head -1 ./results/classification_history.csv
    tail -3 ./results/classification_history.csv
else
    echo "警告: 実験履歴ファイル (classification_history.csv) が生成されませんでした"
fi
echo "----------------------------------------"
