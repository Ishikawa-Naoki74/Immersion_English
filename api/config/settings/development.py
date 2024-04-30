from .base import *
# 開発環境の設定情報
# データベースの設定情報など
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# TODO 環境変数に設定を書くようにする
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.mysql",
    "NAME":  "immersion-english",
    "USER": "Naoki74hub",
    "PASSWORD": "67HHa4ABC2j",
    "HOST": "host.docker.internal",
    "PORT": "53306",# ホストマシンの53306にアクセスされると、Dockerコンテナ内のポート3306にアクセスされる
    "ATOMIC_REQUESTS": True
    }
}
