#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
複数の特徴量抽出方法と分類モデルを比較し、F1スコアを評価するスクリプト
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from config_loader import ConfigLoader

def load_vectors(vec_dir):
    """ベクトルデータを読み込む"""
    vectors = []
    filenames = []
    for path in sorted(vec_dir.glob("*.json")):
        # モデルファイルを除外
        if not path.name.endswith(".pkl") and not path.name.endswith(".model"):
            with path.open(encoding="utf-8") as f:
                vec = json.load(f)
                vectors.append(vec)
                filenames.append(path.stem)
    return np.array(vectors), filenames

def load_labels(label_file):
    """ラベルデータを読み込む"""
    import csv
    labels = {}
    with label_file.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                fname, label = row
                labels[fname] = label
    return labels

def evaluate_model(model, X_train, X_test, y_train, y_test, model_name, feature_name):
    """モデルを評価し、結果を返す"""
    # モデルの学習
    model.fit(X_train, y_train)
    
    # 予測
    y_pred = model.predict(X_test)
    
    # 評価
    report = classification_report(y_test, y_pred, output_dict=True)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    # 混同行列
    cm = confusion_matrix(y_test, y_pred)
    
    return {
        'model_name': model_name,
        'feature_name': feature_name,
        'model': model,
        'report': report,
        'f1_score': f1,
        'confusion_matrix': cm,
        'y_pred': y_pred
    }

def save_results_to_csv(results, output_dir):
    """結果をCSVファイルに保存"""
    data = []
    for r in results:
        model_data = {
            'feature': r['feature_name'],
            'model': r['model_name'],
            'f1_score': r['f1_score']
        }
        # 各クラスの精度、再現率、F1スコアを追加
        for cls in r['report'].keys():
            if cls not in ['accuracy', 'macro avg', 'weighted avg']:
                prefix = f'class_{cls}_'
                model_data[prefix + 'precision'] = r['report'][cls]['precision']
                model_data[prefix + 'recall'] = r['report'][cls]['recall']
                model_data[prefix + 'f1-score'] = r['report'][cls]['f1-score']
        
        data.append(model_data)
    
    df = pd.DataFrame(data)
    df.to_csv(output_dir / 'feature_model_comparison.csv', index=False)

def save_evaluation_summary(results, output_dir):
    """評価結果のサマリーをテキストファイルに保存"""
    with open(output_dir / 'evaluation_summary.txt', 'w', encoding='utf-8') as f:
        f.write("=== メール分類モデル評価結果 ===\n\n")
        
        # 全モデルの結果を記録
        for r in results:
            f.write(f"\n{r['feature_name']} + {r['model_name']}\n")
            f.write("-" * 40 + "\n")
            f.write(f"F1スコア: {r['f1_score']:.4f}\n\n")
            f.write("分類レポート:\n")
            # 分類レポートを文字列形式で取得
            report = classification_report(r['y_pred'], r['y_pred'])
            f.write(report + "\n")
            f.write("-" * 40 + "\n")
        
        # 最良のモデルを記録
        best_result = max(results, key=lambda x: x['f1_score'])
        f.write("\n=== 最良モデル ===\n")
        f.write(f"特徴量: {best_result['feature_name']}\n")
        f.write(f"モデル: {best_result['model_name']}\n")
        f.write(f"F1スコア: {best_result['f1_score']:.4f}\n")

def tune_hyperparameters(X_train, y_train):
    """ハイパーパラメータチューニング"""
    # ロジスティック回帰のパラメータグリッド
    lr_param_grid = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100],
        'solver': ['liblinear', 'lbfgs'],
        'max_iter': [1000]
    }
    
    # SVMのパラメータグリッド
    svm_param_grid = {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto', 0.1, 1]
    }
    
    # ランダムフォレストのパラメータグリッド
    rf_param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5, 10]
    }
    
    # グリッドサーチの実行
    lr_grid = GridSearchCV(LogisticRegression(), lr_param_grid, cv=5, scoring='f1_weighted')
    lr_grid.fit(X_train, y_train)
    
    svm_grid = GridSearchCV(SVC(), svm_param_grid, cv=5, scoring='f1_weighted')
    svm_grid.fit(X_train, y_train)
    
    rf_grid = GridSearchCV(RandomForestClassifier(), rf_param_grid, cv=5, scoring='f1_weighted')
    rf_grid.fit(X_train, y_train)
    
    # 最適なパラメータを持つモデルを返す
    return {
        'LogisticRegression': lr_grid.best_estimator_,
        'SVM': svm_grid.best_estimator_,
        'RandomForest': rf_grid.best_estimator_
    }

def process_feature_set(feature_dir, feature_name, label_map, output_dir):
    """特徴量セットを処理し、評価する"""
    print("\n" + "="*50)
    print(f"{feature_name}の処理を開始...")
    print("="*50)
    
    # 特徴量とラベルの読み込み
    X, filenames = load_vectors(feature_dir)
    y = [label_map.get(name, "unknown") for name in filenames]
    
    # ラベルが設定されていないデータを除外
    valid_indices = [i for i, label in enumerate(y) if label != "unknown"]
    if len(valid_indices) < len(y):
        print(f"警告: {len(y) - len(valid_indices)}件のファイルにラベルが設定されていません。これらは除外されます。")
        X = X[valid_indices]
        y = [y[i] for i in valid_indices]
        filenames = [filenames[i] for i in valid_indices]
    
    if len(X) == 0:
        print(f"エラー: {feature_name}の有効なデータがありません。")
        return []
    
    # データの分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # クラスの一覧
    classes = sorted(list(set(y)))
    print(f"分類クラス: {classes}")
    
    # ハイパーパラメータチューニング
    print("\n" + "-"*50)
    print(f"{feature_name}を用いたパラメータ調整の実行中...")
    print("-"*50)
    tuned_models = tune_hyperparameters(X_train, y_train)
    
    # 評価するモデルのリスト
    models = [
        ('LogisticRegression', tuned_models['LogisticRegression']),
        ('SVM', tuned_models['SVM']),
        ('RandomForest', tuned_models['RandomForest']),
        ('NaiveBayes', GaussianNB())
    ]
    
    # 各モデルの評価
    results = []
    for name, model in models:
        print("\n" + "-"*50)
        print(f"{feature_name} + {name}の評価中...")
        print("-"*50)
        result = evaluate_model(model, X_train, X_test, y_train, y_test, name, feature_name)
        results.append(result)
        
        # 結果の表示
        print(f"\n{feature_name} + {name}の結果:")
        print("-"*30)
        print(f"F1スコア: {result['f1_score']:.4f}")
        print("\n分類レポート:")
        print(classification_report(y_test, result['y_pred']))
    
    return results

def main():
    # 設定の読み込み
    config = ConfigLoader()
    paths = config.get_paths()
    
    # 入出力パスの設定
    labels_file = Path(paths["input"]["labels_file"])
    word2vec_dir = Path(paths["output"]["word2vec"]["vectors_path"])
    tfidf_dir = Path(paths["output"]["tfidf"]["features_path"])
    results_dir = Path(paths["output"]["results"]["evaluation"])
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # ラベルの読み込み
    label_map = load_labels(labels_file)
    
    all_results = []
    
    # Word2Vec特徴量の処理
    if word2vec_dir.exists():
        word2vec_results = process_feature_set(word2vec_dir, "Word2Vec", label_map, results_dir)
        all_results.extend(word2vec_results)
    else:
        print(f"警告: {word2vec_dir}が存在しません。Word2Vec特徴量は処理されません。")
    
    # TF-IDF特徴量の処理
    if tfidf_dir.exists():
        tfidf_results = process_feature_set(tfidf_dir, "TF-IDF", label_map, results_dir)
        all_results.extend(tfidf_results)
    else:
        print(f"警告: {tfidf_dir}が存在しません。TF-IDF特徴量は処理されません。")
    
    if not all_results:
        print("エラー: 有効な結果がありません。")
        return
    
    # 結果をCSVに保存
    save_results_to_csv(all_results, results_dir)
    
    # 評価結果のサマリーを保存
    save_evaluation_summary(all_results, results_dir)
    
    # 最良のモデルを表示
    best_result = max(all_results, key=lambda x: x['f1_score'])
    print("\n" + "="*50)
    print("最終評価結果")
    print("="*50)
    print(f"最良のモデル: {best_result['feature_name']} + {best_result['model_name']}")
    print(f"F1スコア: {best_result['f1_score']:.4f}")
    
    print("\n" + "-"*50)
    print(f"結果は {results_dir} ディレクトリに保存されました")
    print("-"*50)

if __name__ == "__main__":
    main()
