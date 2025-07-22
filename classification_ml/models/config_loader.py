import json
import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "model_config.json"):
        """設定ファイルを読み込むためのローダークラス

        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # 前処理の設定ファイルを読み込む
        current_dir = os.path.dirname(os.path.abspath(self.config_path))
        preprocess_config_path = os.path.join(os.path.dirname(current_dir), 'preprocess_nlp', 'preprocess_config.json')
        print(f"\n前処理設定ファイルのパス: {preprocess_config_path}")
        
        try:
            with open(preprocess_config_path, 'r', encoding='utf-8') as f:
                self.preprocess_config = json.load(f)
                stopwords_enabled = self.get_stopwords_enabled()
                print(f"前処理設定ファイルを読み込みました")
                print(f"tokenize_params: {self.preprocess_config.get('tokenize_params', {}).get('value', {})}")
                print(f"stopwords設定: {'有効' if stopwords_enabled else '無効'}")
        except FileNotFoundError:
            print(f"警告: 前処理設定ファイルが見つかりません: {preprocess_config_path}")
            self.preprocess_config = {}
            print("デフォルト設定を使用します: stopwords=False")

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む

        Returns:
            Dict[str, Any]: 設定内容を含む辞書
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_word2vec_params(self) -> Dict[str, Any]:
        """Word2Vecのパラメータを取得

        Returns:
            Dict[str, Any]: Word2Vecのパラメータ
        """
        return self.config["word2vec_params"]

    def get_tfidf_params(self) -> Dict[str, Any]:
        """TF-IDFのパラメータを取得

        Returns:
            Dict[str, Any]: TF-IDFのパラメータ
        """
        return self.config["tfidf_params"]

    def get_model_params(self) -> Dict[str, Any]:
        """モデルのパラメータを取得

        Returns:
            Dict[str, Any]: モデルのパラメータ
        """
        return self.config["model_params"]

    def get_paths(self) -> Dict[str, Any]:
        """入出力パスの設定を取得

        Returns:
            Dict[str, Dict[str, str]]: パス設定
        """
        return {
            "input": self.config["input"],
            "output": self.config["output"]
        }

    def get_visualization_settings(self) -> Dict[str, bool]:
        """可視化の設定を取得

        Returns:
            Dict[str, bool]: 可視化設定
        """
        return self.config["visualization"]

    def get_stopwords_enabled(self) -> bool:
        """前処理設定からstopwordsの有効/無効を取得

        Returns:
            bool: stopwordsが有効な場合True
        """
        try:
            return self.preprocess_config.get('tokenize_params', {}).get('value', {}).get('enable_stopwords', False)
        except (AttributeError, KeyError):
            return False
    def get_normalize_enabled(self) -> bool:
        """前処理設定からゆらぎ処理の有効/無効を取得

        Returns:
            bool: 数値正規化または仮名正規化が有効な場合True
        """
        try:
            normalize_params = self.preprocess_config.get('normalize_params', {}).get('value', {})
            return normalize_params.get('enable_number_normalize', False) or \
                   normalize_params.get('enable_kana_normalize', False)
        except (AttributeError, KeyError):
            return False
