#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール形態素データからTF-IDF特徴量を生成して特徴量ディレクトリに保存
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
import numpy as np
import os
import json
import pickle
from config_loader import ConfigLoader

def read_tokenized_docs(input_dir):
    """形態素解析済みのテキストファイルを読み込む"""
    docs = []
    filenames = []
    for path in sorted(input_dir.glob("*.txt")):
        with path.open(encoding="utf-8") as f:
            tokens = f.read().strip().split()
            if tokens:
                docs.append(" ".join(tokens))  # TF-IDFのために空白区切りのテキストに変換
                filenames.append(path.stem)
    return docs, filenames

def main():
    # 設定の読み込み
    config = ConfigLoader()
    paths = config.get_paths()
    tfidf_params = config.get_tfidf_params()
    
    # 入出力パスの設定
    data_source = paths["input"]["data_source"]
    input_path = paths["input"]["data_paths"][data_source]
    input_dir = Path(input_path.replace("*.txt", ""))
    output_dir = Path(paths["output"]["tfidf"]["features_path"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 形態素解析済みテキストの読み込み
    docs, filenames = read_tokenized_docs(input_dir)
    
    # TF-IDF特徴量の生成
    vectorizer = TfidfVectorizer(
        max_features=tfidf_params["max_features"],
        min_df=tfidf_params["min_df"],
        max_df=tfidf_params["max_df"],
        sublinear_tf=True   # サブリニアTF変換（log(1+tf)）
    )
    
    # 文書をベクトル化
    X = vectorizer.fit_transform(docs)
    
    # ベクトル化モデルを保存
    with open(output_dir / "tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    # 特徴量の次元数を表示
    print(f"特徴量の次元数: {X.shape[1]}")
    print(f"文書数: {X.shape[0]}")
    
    # 各文書のTF-IDF特徴量をJSONファイルとして保存
    for i, fname in enumerate(filenames):
        # scipy.sparse行列からnumpy配列に変換
        vec = X[i].toarray()[0]
        
        # JSONファイルとして保存
        outpath = output_dir / f"{fname}.json"
        with outpath.open("w", encoding="utf-8") as f:
            json.dump(vec.tolist(), f, ensure_ascii=False, indent=2)
    
    print(f"TF-IDF: {X.shape[0]}件の文書ベクトルを生成しました")

if __name__ == "__main__":
    main()
