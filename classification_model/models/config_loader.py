import json
import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "../classification_model/model_config.json"):
        """設定ファイルを読み込むためのローダークラス

        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = self._load_config()

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
