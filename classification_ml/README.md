# メール分類モデル

形態素解析済みのメールテキストを使用して、Word2VecとTF-IDFによる文書ベクトル化と機械学習による分類を行い、その性能を比較するモジュール。

## ディレクトリ構成

```
./
├── README.md                          # このファイル
├── run_classification.sh              # 分類実行スクリプト
├── model_config.json                  # モデルパラメータの設定
├── labels.csv                         # 文書カテゴリのラベルファイル
├── models/                            # モデル関連のファイル
│   ├── config_loader.py              # 設定ファイル読み込みクラス
│   ├── generate_word2vec.py          # Word2Vecモデル学習と文書ベクトル生成
│   ├── generate_tfidf.py             # TF-IDF特徴量生成
│   └── compare_features_and_models.py # 特徴量とモデルの比較
├── features_word2vec/                 # Word2Vec特徴量
│   ├── word2vec.model                # 学習済みWord2Vecモデル
│   └── *.json                        # 文書ベクトル
├── features_tfidf/                    # TF-IDF特徴量
│   ├── tfidf_vectorizer.pkl          # TF-IDFベクトライザーモデル
│   └── *.json                        # TF-IDF特徴量
├── results/                           # 評価結果
│   ├── evaluation_summary.txt         # 評価結果のサマリー
│   ├── feature_model_comparison.csv   # 特徴量とモデルの比較データ
│   └── classification_history.csv     # 実験結果の履歴データ
└── old/                              # 過去のバージョン（参考用）
```

## プロジェクト構造の詳細

### models/
- `config_loader.py`: JSONファイルからモデルの設定を読み込むためのユーティリティクラス
- `generate_word2vec.py`: Word2Vecモデルの学習と文書ベクトル生成を行う
- `generate_tfidf.py`: TF-IDF特徴量生成を行う
- `compare_features_and_models.py`: 各特徴量と分類モデルの組み合わせで性能評価を行う

### features_word2vec/
Word2Vec関連のファイルを格納：
- `word2vec.model`: 学習済みのWord2Vecモデル
- `*.json`: 各文書のWord2Vecベクトル（文書ID.json）

### features_tfidf/
TF-IDF関連のファイルを格納：
- `tfidf_vectorizer.pkl`: 学習済みのTF-IDFベクトライザー
- `*.json`: 各文書のTF-IDFベクトル（文書ID.json）

### results/
評価結果を格納：
- `evaluation_summary.txt`: 全モデルの評価指標
- `feature_model_comparison.csv`: 特徴量とモデルの組み合わせごとの性能データ

## 設定ファイル（model_config.json）

### 入力データの設定
model_config.jsonで入力データのソースを指定できます：

```json
{
    "input": {
        "data_source": "fuzzy",  // "fuzzy" または "tokenize" を指定
        "data_paths": {
            "fuzzy": "../shared_texts_fuzzy/*.txt",
            "tokenize": "../shared_texts_tokenize/*.txt"
        },
        "labels_file": "labels.csv"
    }
}
```

- `data_source`: 使用するデータソースを指定（"fuzzy" または "tokenize"）
- `data_paths`: 各データソースのファイルパスを定義
  - `fuzzy`: ファジー検索用のテキストファイル
  - `tokenize`: 形態素解析済みのテキストファイル

### その他の設定パラメータ
```json
{
    "word2vec_params": {
        "vector_size": 100,
        "window": 5,
        "min_count": 1,
        "workers": 4
    },
    "tfidf_params": {
        "max_features": 1000,
        "min_df": 2,
        "max_df": 0.95
    },
    "model_params": {
        "logistic_regression": {
            "max_iter": 1000
        },
        "svm": {
            "C": [0.1, 1, 10],
            "kernel": ["linear", "rbf"],
            "gamma": ["scale", "auto", 0.1, 1]
        },
        "test_size": 0.3
    }
}
```

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

## 使用方法

### データソースの切り替え
1. model_config.jsonの`data_source`を変更：
   - ファジー検索用テキスト: `"data_source": "fuzzy"`
   - 形態素解析済みテキスト: `"data_source": "tokenize"`

### すべての評価を実行

```bash
./run_classification.sh
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
- テキストファイル: model_config.jsonの`data_paths`で指定されたパス
- ラベルファイル: `./labels.csv` (形式: ファイル名,カテゴリ)

### 出力
- Word2Vecモデル: `./features_word2vec/word2vec.model`
- Word2Vec文書ベクトル: `./features_word2vec/*.json`
- TF-IDFベクトライザー: `./features_tfidf/tfidf_vectorizer.pkl`
- TF-IDF特徴量: `./features_tfidf/*.json`
- 分類結果と評価指標: `./results/evaluation_summary.txt`

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
