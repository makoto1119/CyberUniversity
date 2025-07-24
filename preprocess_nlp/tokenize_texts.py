#!/usr/bin/env python3
import os
import json
import argparse
from pathlib import Path
from janome.tokenizer import Tokenizer
import re

def load_config(config_file='nlp_config.json'):
    """設定ファイルを読み込む"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_stopwords(stopwords_file):
    """ストップワードを読み込む"""
    with open(stopwords_file, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def get_number_from_filename(filename):
    """ファイル名から数字部分を抽出する"""
    if 'unknown' in filename.lower():
        return None
    match = re.search(r'mail_mask_(\d+)\.txt$', filename)
    return int(match.group(1)) if match else None

def process_file(input_file, output_file, stopwords, pos_filter, enable_stopwords=True):
    """単一ファイルの形態素解析を行う"""
    tokenizer = Tokenizer()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    tokens = []
    for token in tokenizer.tokenize(text):
        if any(pos in token.part_of_speech for pos in pos_filter):
            # ストップワードチェックを表層形で行う
            if not enable_stopwords or (token.surface not in stopwords and token.base_form not in stopwords):
                tokens.append(token.base_form)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(' '.join(tokens))

def process_directory(input_dir, output_dir, stopwords_file, pos_filter, enable_stopwords=True):
    """ディレクトリ内の全ファイルを処理"""
    stopwords = load_stopwords(stopwords_file) if enable_stopwords else set()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 出力ディレクトリの作成
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 入力ファイルの取得とソート
    input_files = sorted(list(input_path.glob('*.txt')), 
                        key=lambda x: get_number_from_filename(x.name))
    
    # 各ファイルの処理
    for input_file in input_files:
        # 入力ファイルの番号を維持して出力ファイル名を生成
        file_number = get_number_from_filename(input_file.name)
        if file_number is None:  # unknown ファイルの場合はスキップ
            print(f"Skipping: {input_file}")
            continue
        output_file = output_path / f'texts_tokenize_{file_number:03d}.txt'
        print(f"Processing: {input_file} -> {output_file}")
        process_file(str(input_file), str(output_file), stopwords, pos_filter, enable_stopwords)

def main():
    parser = argparse.ArgumentParser(description='テキストの形態素解析を行います')
    parser.add_argument('--config', default='nlp_config.json',
                      help='設定ファイルのパス')
    parser.add_argument('--indir',
                      help='入力ディレクトリのパス（設定ファイルの値を上書き）')
    parser.add_argument('--outdir',
                      help='出力ディレクトリのパス（設定ファイルの値を上書き）')
    parser.add_argument('--stopwords',
                      help='ストップワードファイルのパス（設定ファイルの値を上書き）')
    parser.add_argument('--pos-filter',
                      help='抽出する品詞（カンマ区切り、設定ファイルの値を上書き）')
    parser.add_argument('--enable-stopwords', type=bool,
                      help='ストップワードを使用するかどうか（設定ファイルの値を上書き）')
    
    args = parser.parse_args()
    
    # 設定の読み込み
    config = load_config(args.config)
    
    # コマンドライン引数で上書きされた場合はそちらを優先
    input_dir = args.indir or config['process_input']['value']['tokenize']
    output_dir = args.outdir or config['process_output']['value']['tokenize']
    stopwords_file = args.stopwords or config['stopwords_file']['value']
    pos_filter = args.pos_filter.split(',') if args.pos_filter else config['default_pos_filter']['value']
    enable_stopwords = args.enable_stopwords if args.enable_stopwords is not None else \
                      config['tokenize_params']['value'].get('enable_stopwords', True)
    
    process_directory(input_dir, output_dir, stopwords_file, pos_filter, enable_stopwords)
    print(f"全ファイルの形態素解析が完了しました")

if __name__ == '__main__':
    main()
