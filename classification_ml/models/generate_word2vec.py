#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール形態素データからWord2Vec文書ベクトルを生成して特微量ディレクトリに保存
"""

from gensim.models import Word2Vec
from pathlib import Path
import numpy as np
import os
import json
from config_loader import ConfigLoader

def read_tokenized_docs(input_dir):
    """形態素解析済みのテキストファイルを読み込む"""
    docs = []
    filenames = []
    for path in sorted(input_dir.glob("*.txt")):
        with path.open(encoding="utf-8") as f:
            tokens = f.read().strip().split()
            if tokens:
                docs.append(tokens)
                filenames.append(path.stem)
    return docs, filenames

def compute_doc_vectors(docs, model):
    """文書ベクトルを計算（単語ベクトルの平均）"""
    doc_vectors = []
    for tokens in docs:
        vectors = [model.wv[token] for token in tokens if token in model.wv]
        if vectors:
            vec = np.mean(vectors, axis=0)
        else:
            vec = np.zeros(model.vector_size)
        doc_vectors.append(vec)
    return np.array(doc_vectors)

def main():
    # 設定の読み込み
    config = ConfigLoader()
    paths = config.get_paths()
    word2vec_params = config.get_word2vec_params()

    # 入出力パスの設定
    data_source = paths["input"]["data_source"]
    input_path = paths["input"]["data_paths"][data_source]
    input_dir = Path(input_path.replace("*.txt", ""))
    output_dir = Path(paths["output"]["word2vec"]["vectors_path"])
    model_path = Path(paths["output"]["word2vec"]["model_path"])

    # ディレクトリの作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # 文書の読み込み
    print("形態素解析済みテキストの読み込み中...")
    docs, filenames = read_tokenized_docs(input_dir)
    
    if not docs:
        raise ValueError("テキストファイルが見つからないか、すべてが空です")

    print(f"読み込み完了: {len(docs)}件の文書")

    # Word2Vecモデルの学習
    print("Word2Vecモデルの学習中...")
    model = Word2Vec(min_count=word2vec_params["min_count"],
                    window=word2vec_params["window"],
                    vector_size=word2vec_params["vector_size"],
                    workers=word2vec_params["workers"])
    
    # 語彙の構築
    model.build_vocab(docs)
    
    # モデルの学習
    model.train(docs, total_examples=model.corpus_count, epochs=model.epochs)
    
    # モデルの保存
    print(f"モデルを保存中: {model_path}")
    model.save(str(model_path))

    # 文書ベクトルの計算と保存
    print("文書ベクトルを生成中...")
    vectors = compute_doc_vectors(docs, model)

    for vec, fname in zip(vectors, filenames):
        outpath = output_dir / f"{fname}.json"
        with outpath.open("w", encoding="utf-8") as f:
            json.dump(vec.tolist(), f, ensure_ascii=False, indent=2)

    print(f"Word2Vec: {len(vectors)}件の文書ベクトルを生成しました")

if __name__ == "__main__":
    main()
