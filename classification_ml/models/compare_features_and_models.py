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
from datetime import datetime
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
    
    print(f"\nベクトルデータの読み込みを開始: {vec_dir}")
    
    # まず全てのベクトルを読み込む
    for i, path in enumerate(sorted(vec_dir.glob("*.json"))):
        # モデルファイルを除外
        if not path.name.endswith(".pkl") and not path.name.endswith(".model"):
            # 最初の5件のみ表示
            if i < 5:
                print(f"処理中のファイル: {path.name}")  # デバッグ出力
            with path.open(encoding="utf-8") as f:
                vec = json.load(f)
                if isinstance(vec, list):  # ベクトルがリスト形式であることを確認
                    vectors.append(vec)
                    # 拡張子を除いたファイル名を保存
                    base_name = path.stem
                    filenames.append(base_name)
                    if i < 5:
                        print(f"読み込み成功: {base_name}")  # デバッグ出力
    
    print(f"\n合計で{len(vectors)}個のベクトルを読み込みました")
    
    if not vectors:
        return np.array([]), []
    
    # 全てのベクトルを同じ次元数にする
    max_dim = max(len(vec) for vec in vectors)
    padded_vectors = []
    for vec in vectors:
        if len(vec) < max_dim:
            # 不足している次元を0で埋める
            padded_vec = vec + [0.0] * (max_dim - len(vec))
            padded_vectors.append(padded_vec)
        else:
            padded_vectors.append(vec)
    
    return np.array(padded_vectors), filenames

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
    
    # 評価（zero_division=1を設定して警告を抑制）
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=1)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=1)
    
    # 混同行列
    cm = confusion_matrix(y_test, y_pred)
    
    return {
        'model_name': model_name,
        'feature_name': feature_name,
        'model': model,
        'report': report,
        'f1_score': f1,
        'confusion_matrix': cm,
        'y_pred': y_pred,
        'y_test': y_test  # 評価サマリー用に正解ラベルも保存
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

def save_history(best_result, config, output_dir):
    """最良の結果を履歴として保存"""
    # 出力ディレクトリが存在することを確認
    output_dir.mkdir(parents=True, exist_ok=True)
    
    history_file = output_dir / 'classification_history.csv'
    now = datetime.now()
    
    # 入力データ種別を取得
    data_source = config.get_paths()["input"]["data_source"]
    
    # モデルのパラメータを取得
    model_params = config.get_model_params()
    test_size = model_params.get('test_size', 0.3)  # デフォルト値として0.3を使用
    
    # 全データ数を計算
    total_samples = int(len(best_result['y_test']) / test_size)
    
    # 特徴量の種類に応じたパラメータを取得
    feature_params = ""
    if best_result['feature_name'] == "Word2Vec":
        w2v_params = config.get_word2vec_params()
        feature_params = f"vec_size={w2v_params['vector_size']},window={w2v_params['window']},min_count={w2v_params['min_count']}"
    elif best_result['feature_name'] == "TF-IDF":
        tfidf_params = config.get_tfidf_params()
        feature_params = f"max_feat={tfidf_params['max_features']},min_df={tfidf_params['min_df']},max_df={tfidf_params['max_df']}"
    
    # クラス数を計算
    unique_classes = set(best_result['y_test'])
    num_classes = len(unique_classes)
    
    # stopwordsとゆらぎ処理の設定を取得
    stopwords_enabled = config.get_stopwords_enabled()
    normalize_enabled = config.get_normalize_enabled()
    print(f"\n保存時の設定:")
    print(f"- stopwords設定: {'あり' if stopwords_enabled else 'なし'}")
    print(f"- ゆらぎ処理: {'あり' if normalize_enabled else 'なし'}")
    
    # 新しい結果の行を作成
    new_row = {
        '日付': now.strftime('%Y-%m-%d'),
        '時間': now.strftime('%H:%M:%S'),
        '特徴量手法': best_result['feature_name'],
        '分類モデル': best_result['model_name'],
        '入力データ種別': data_source,
        'サンプル数': total_samples,
        'テストデータ比率': f"{test_size:.2f}",
        '特徴量パラメータ': feature_params,
        'ストップワード設定': 'あり' if stopwords_enabled else 'なし',
        'ゆらぎ補正': 'あり' if normalize_enabled else 'なし',
        'F1スコア': f"{best_result['f1_score']:.4f}",
        'クラス数': num_classes,
        '備考・変更点': ''
    }
    
    # CSVファイルが存在する場合は追記、存在しない場合は新規作成
    columns = [
        '日付', '時間', '特徴量手法', '分類モデル', '入力データ種別',
        'サンプル数', 'テストデータ比率', '特徴量パラメータ',
        'ストップワード設定', 'ゆらぎ補正', 'F1スコア', 'クラス数',
        '備考・変更点'
    ]
    
    if history_file.exists():
        df = pd.read_csv(history_file)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row], columns=columns)
    
    # CSVファイルに保存（カラム順序を維持）
    df.to_csv(history_file, index=False, columns=columns)
    print(f"\n履歴が {history_file} に保存されました")

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
            # 分類レポートを文字列形式で取得（zero_division=1を設定）
            report = classification_report(r['y_test'], r['y_pred'], zero_division=1)
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
    # 設定の読み込み
    config = ConfigLoader()
    model_params = config.get_model_params()

    # デフォルトのパラメータグリッド
    default_lr_params = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100],
        'solver': ['liblinear', 'lbfgs'],
        'max_iter': [1000]
    }

    default_svm_params = {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto', 0.1, 1],
        'probability': [True]
    }

    default_rf_params = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5, 10]
    }

    default_nb_params = {
        'var_smoothing': [1e-9, 1e-8, 1e-7, 1e-6]
    }

    # 設定ファイルのパラメータでデフォルト値を上書き
    lr_config = model_params.get('logistic_regression', {})
    lr_param_grid = default_lr_params.copy()
    if 'C' in lr_config: lr_param_grid['C'] = lr_config['C']
    if 'solver' in lr_config: lr_param_grid['solver'] = lr_config['solver']
    if 'max_iter' in lr_config: lr_param_grid['max_iter'] = [lr_config['max_iter']]

    svm_config = model_params.get('svm', {})
    svm_param_grid = default_svm_params.copy()
    if 'C' in svm_config: svm_param_grid['C'] = svm_config['C']
    if 'kernel' in svm_config: svm_param_grid['kernel'] = svm_config['kernel']
    if 'gamma' in svm_config: svm_param_grid['gamma'] = svm_config['gamma']

    rf_config = model_params.get('random_forest', {})
    rf_param_grid = default_rf_params.copy()
    if 'n_estimators' in rf_config: rf_param_grid['n_estimators'] = rf_config['n_estimators']
    if 'max_depth' in rf_config: rf_param_grid['max_depth'] = rf_config['max_depth']
    if 'min_samples_split' in rf_config: rf_param_grid['min_samples_split'] = rf_config['min_samples_split']

    # GaussianNBのパラメータグリッド
    nb_config = model_params.get('naive_bayes', {})
    nb_param_grid = default_nb_params.copy()
    if 'var_smoothing' in nb_config: nb_param_grid['var_smoothing'] = nb_config['var_smoothing']
    
    # グリッドサーチの実行
    common_params = {
        'cv': 5,                    # 5分割交差検証
        'scoring': 'f1_weighted',   # 評価指標
        'verbose': 1,              # 進捗表示
        'n_jobs': -1,              # 全CPU使用
        'return_train_score': True  # 訓練スコアも記録
    }
    
    # ロジスティック回帰
    lr_grid = GridSearchCV(
        LogisticRegression(),
        lr_param_grid,
        **common_params
    )
    print("\nロジスティック回帰のパラメータ探索中...")
    lr_grid.fit(X_train, y_train)
    print(f"最適パラメータ: {lr_grid.best_params_}")
    print(f"最良スコア: {lr_grid.best_score_:.4f}")
    
    # SVM
    svm_grid = GridSearchCV(
        SVC(),
        svm_param_grid,
        **common_params
    )
    print("\nSVMのパラメータ探索中...")
    svm_grid.fit(X_train, y_train)
    print(f"最適パラメータ: {svm_grid.best_params_}")
    print(f"最良スコア: {svm_grid.best_score_:.4f}")
    
    # ランダムフォレスト
    rf_grid = GridSearchCV(
        RandomForestClassifier(),
        rf_param_grid,
        **common_params
    )
    print("\nランダムフォレストのパラメータ探索中...")
    rf_grid.fit(X_train, y_train)
    print(f"最適パラメータ: {rf_grid.best_params_}")
    print(f"最良スコア: {rf_grid.best_score_:.4f}")

    # GaussianNB
    nb_grid = GridSearchCV(
        GaussianNB(),
        nb_param_grid,
        **common_params
    )
    print("\nGaussianNBのパラメータ探索中...")
    nb_grid.fit(X_train, y_train)
    print(f"最適パラメータ: {nb_grid.best_params_}")
    print(f"最良スコア: {nb_grid.best_score_:.4f}")
    
    # 最適なパラメータを持つモデルを返す
    return {
        'LogisticRegression': lr_grid.best_estimator_,
        'SVM': svm_grid.best_estimator_,
        'RandomForest': rf_grid.best_estimator_,
        'NaiveBayes': nb_grid.best_estimator_
    }

def process_feature_set(feature_dir, feature_name, label_map, output_dir):
    """特徴量セットを処理し、評価する"""
    print("\n" + "="*50)
    print(f"{feature_name}の処理を開始...")
    print("="*50)
    
    # 特徴量とラベルの読み込み
    X, filenames = load_vectors(feature_dir)
    
    if len(X) == 0:
        print(f"エラー: {feature_name}の有効なデータがありません。")
        return []
    
    print("\nデバッグ情報:")
    print(f"読み込んだファイル数: {len(filenames)}")
    print(f"最初の5つのファイル名: {filenames[:5]}")
    print(f"ラベルマップのエントリ数: {len(label_map)}")
    print(f"ラベルマップの最初の5つのエントリ: {dict(list(label_map.items())[:5])}")
        
    y = []
    for name in filenames:
        # 元のファイル名をそのまま使用（.txtを付加）
        label = label_map.get(f"{name}.txt", "unknown")
        y.append(label)
    
    # デバッグ: マッチしなかったファイル名を表示
    unmatched_files = [(name, name + ".txt") for i, name in enumerate(filenames) if y[i] == "unknown"]
    if unmatched_files:
        print("\nラベルが見つからなかったファイル（最初の5件）:")
        for orig_name, search_name in unmatched_files[:5]:
            print(f"元のファイル名: {orig_name}")
            print(f"検索したキー: {search_name}")
    
    # ラベルが設定されていないデータを除外
    valid_indices = [i for i, label in enumerate(y) if label != "unknown"]
    if len(valid_indices) < len(y):
        print(f"\n警告: {len(y) - len(valid_indices)}件のファイルにラベルが設定されていません。これらは除外されます。")
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
        print(classification_report(y_test, result['y_pred'], zero_division=1))
    
    return results

def main():
    # 設定の読み込み
    config = ConfigLoader()
    paths = config.get_paths()
    
    # stopwords設定の確認
    stopwords_enabled = config.get_stopwords_enabled()
    print(f"\nstopwords設定: {'有効' if stopwords_enabled else '無効'}")
    print("-"*50)
    
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
    
    # 履歴の保存
    save_history(best_result, config, results_dir)
    
    print("\n" + "-"*50)
    print(f"結果は {results_dir} ディレクトリに保存されました")
    print("-"*50)

if __name__ == "__main__":
    main()
