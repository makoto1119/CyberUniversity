# メール分類モデル

形態素解析済みのメールテキストを使用して、Word2VecとTF-IDFによる文書ベクトル化と機械学習による分類を行い、その性能を比較するモジュール。

---

## ディレクトリ構成

```
classification_model/
├── README.md                          # このファイル
├── run_evaluation.sh                  # 評価実行スクリプト
├── model_config.json                  # モデルパラメータの設定
├── labels.csv                         # 文書カテゴリのラベルファイル
├── models/                           # モデル関連のファイル
│   ├── config_loader.py              # 設定ファイル読み込みクラス
│   ├── generate_word2vec.py         # Word2Vecモデル学習と文書ベクトル生成
│   ├── generate_tfidf.py            # TF-IDF特徴量生成
│   └── compare_features_and_models.py # 特徴量とモデルの比較
├── features_word2vec/               # Word2Vec特徴量
│   ├── word2vec.model              # 学習済みWord2Vecモデル
│   └── *.json                      # 文書ベクトル
├── features_tfidf/                 # TF-IDF特徴量
│   └── *.json                      # TF-IDF特徴量
├── results/                        # 評価結果
│   ├── evaluation_summary.txt      # 評価結果のサマリー
│   └── feature_model_comparison.csv # 特徴量とモデルの比較データ
└── old/                           # 過去のバージョン（参考用）
```

## プロジェクト構造の詳細

### models/
- `config_loader.py`: JSONファイルからモデルの設定を読み込むためのユーティリティクラス
- `generate_word2vec.py`: Word2Vecモデルの学習と文書ベクトル生成を行う
- `generate_tfidf.py`: TF-IDFベクトル生成を行う
- `compare_features_and_models.py`: 各特徴量と分類モデルの組み合わせで性能評価を行う
- `visualize_results.py`: 評価結果の可視化を行う

### features_word2vec/
Word2Vec関連のファイルを格納：
- `word2vec.model`: 学習済みのWord2Vecモデル
- `*.json`: 各文書のWord2Vecベクトル（文書ID.json）

### features_tfidf/
TF-IDF関連のファイルを格納：
- `*.json`: 各文書のTF-IDFベクトル（文書ID.json）

### results/
評価結果を格納：
- `evaluation_summary.txt`: 全モデルの評価指標
- `feature_model_comparison.csv`: 特徴量とモデルの組み合わせごとの性能データ

## 機能

- 形態素解析済みテキストからWord2Vecモデルの学習
- TF-IDFによる特徴量生成
- 文書ごとの特徴ベクトル（文書ベクトル）の生成
- ロジスティック回帰による文書分類
- 分類性能の評価（F1スコアなど）
- 特徴量手法の比較

## 必要な環境

- Python 3.6以上
- 必要なライブラリ：
  - `gensim` (Word2Vec用)
  - `scikit-learn` (機械学習アルゴリズム、TF-IDF用)
  - `numpy` (数値計算用)
  - `pandas` (データ処理用)

## インストール

```bash
$ pip install gensim scikit-learn numpy pandas
```

## 処理フロー

```
1. 形態素解析済みテキスト → generate_word2vec.py → Word2Vecモデル + 文書ベクトル
2. 形態素解析済みテキスト → generate_tfidf.py → TF-IDF特徴量
3. 特徴量 + ラベル → compare_features_and_models.py → 分類結果 + 評価指標
```

## 使用方法

### すべての評価を実行

```bash
./run_evaluation.sh
```

### 個別に実行する場合

1. Word2Vec特徴量生成
```bash
python models/generate_word2vec.py
```

2. TF-IDF特徴量生成
```bash
python models/generate_tfidf.py
```

3. 特徴量とモデルの比較
```bash
python models/compare_features_and_models.py
```

## 入出力ファイル

### 入力
- 形態素解析済みテキスト: `../shared_mail_morphological/*.txt`
- ラベルファイル: `./labels.csv` (形式: ファイル名,カテゴリ)

### 出力
- Word2Vecモデル: `./features_word2vec/word2vec.model`
- Word2Vec文書ベクトル: `./features_word2vec/*.json`
- TF-IDF特徴量: `./features_tfidf/*.json`
- 分類結果と評価指標: `./results/evaluation_summary.txt`

## 特徴量生成パラメータ

### Word2Vec
- `vector_size`: 100 (ベクトルの次元数)
- `window`: 5 (コンテキストウィンドウサイズ)
- `min_count`: 1 (出現回数の最小値)
- `workers`: 4 (並列処理数)

### TF-IDF
- `max_features`: 1000 (使用する特徴量の数)
- `min_df`: 2 (最小文書頻度)
- `max_df`: 0.95 (最大文書頻度)

## 文書ベクトル化手法

### Word2Vec
各文書のベクトル表現は、文書内の単語ベクトルの平均として計算されます：
1. 文書内の各単語のWord2Vecベクトルを取得
2. それらのベクトルの平均を計算
3. 文書内にWord2Vecモデルに含まれる単語がない場合はゼロベクトルを使用

### TF-IDF
scikit-learnのTfidfVectorizerを使用して文書をベクトル化します：
1. 文書全体からボキャブラリを構築
2. 各文書をTF-IDF重み付けされた特徴ベクトルに変換

## 分類モデル

現在の実装では以下のモデルを使用：
- ロジスティック回帰（LogisticRegression）
  - `max_iter`: 1000 (最大反復回数)
- サポートベクターマシン（SVM）
- ランダムフォレスト（RandomForest）
- ナイーブベイズ（NaiveBayes）

## 評価指標

分類性能の評価には以下の指標を使用：
- 精度（Precision）
- 再現率（Recall）
- F1スコア（F1-score）
- サポート（Support）
- 混同行列（Confusion Matrix）

## 注意事項

- ラベルファイル（labels.csv）は手動で作成する必要があります
- 全てのファイルにラベルが設定されていない場合、警告が表示されます
- 現在の実装ではテストデータを30%としています（train_test_split(test_size=0.3)）

## ライセンス

このプロジェクトはMITライセンスの下で公開しています。
