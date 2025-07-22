#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import argparse
from pathlib import Path
import os

def load_config(config_file):
    """設定ファイルを読み込む"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_patterns(json_path):
    """正規化パターンを読み込む"""
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)

def load_technical_terms(json_path='technical_terms.json'):
    """技術用語リストを読み込む"""
    try:
        with open(json_path, encoding='utf-8') as f:
            return set(json.load(f)['protected_terms'])
    except FileNotFoundError:
        print(f"警告: 技術用語リストファイル {json_path} が見つかりません")
        return set()

def normalize_text(text, patterns, params):
    """テキストを正規化する"""
    # 技術用語リストの読み込み
    tech_terms = load_technical_terms()
    
    # 技術用語を一時的にプレースホルダーに置換
    placeholder_map = {}
    for i, term in enumerate(tech_terms):
        if term in text:
            placeholder = f"__TECH_TERM_{i}__"
            text = text.replace(term, placeholder)
            placeholder_map[placeholder] = term
    
    # 数字の正規化
    if params.get('enable_number_normalize', True):
        for half, full in zip('0123456789', '０１２３４５６７８９'):
            text = text.replace(full, half)
    
    # カタカナの正規化
    if params.get('enable_kana_normalize', True):
        text = re.sub(r'[ァ-ン]', lambda x: x.group(0).translate(str.maketrans('ァ-ン', 'ぁ-ん')), text)
    
    # パターンによる正規化
    for standard, variants in patterns.items():
        for variant in variants:
            text = text.replace(variant, standard)
    
    # プレースホルダーを元の技術用語に戻す
    for placeholder, term in placeholder_map.items():
        text = text.replace(placeholder, term)
    
    return text

def get_number_from_filename(filename):
    """ファイル名から数字部分を抽出する"""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 0

def process_directory(input_dir, output_dir, patterns, params):
    """ディレクトリ内の全ファイルを処理"""
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 入力ファイルの取得とソート
    input_files = sorted(list(Path(input_dir).glob('*.txt')),
                        key=lambda x: get_number_from_filename(x.name))
    
    # 入力ディレクトリ内の全ファイルを処理
    for i, file_path in enumerate(input_files, 1):
        # 出力ファイルパスの生成（texts_fuzzy_001.txt の形式）
        output_path = Path(output_dir) / f'texts_fuzzy_{i:03d}.txt'
        
        # ファイルの処理
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        # テキストの正規化
        normalized = normalize_text(content, patterns, params)
        
        # 結果の出力
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(normalized)
        
        print(f"Processing: {file_path} -> {output_path}")

def main():
    parser = argparse.ArgumentParser(description='テキストの正規化を行います')
    parser.add_argument('--config', default='preprocess_config.json', help='設定ファイルのパス')
    parser.add_argument('--indir', help='入力ディレクトリのパス（設定ファイルの値を上書き）')
    parser.add_argument('--outdir', help='出力ディレクトリのパス（設定ファイルの値を上書き）')
    
    args = parser.parse_args()
    
    # 設定の読み込み
    config = load_config(args.config)
    
    # コマンドライン引数で上書きされた場合はそちらを優先
    input_dir = args.indir or config['process_input']['value']['fuzzy']
    output_dir = args.outdir or config['process_output']['value']['fuzzy']
    patterns_file = config['fuzzy_patterns_file']['value']
    normalize_params = config['normalize_params']['value']
    
    # パターンの読み込み
    patterns = load_patterns(patterns_file)
    
    # ディレクトリ内の全ファイルを処理
    process_directory(input_dir, output_dir, patterns, normalize_params)

if __name__ == '__main__':
    main()
