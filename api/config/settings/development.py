from .base import *

# 開発環境の設定情報
DATABASES = {
  "default": {
    "ENGINE": env("DATABASE_ENGINE"),
    "NAME":  env("DATABASE_NAME"),
    "USER": env("DATABASE_USER"),
    "PASSWORD": env("DATABASE_PASSWORD"),
    "HOST": env("DATABASE_HOST"),
    "PORT": env("DATABASE_PORT"),
    "ATOMIC_REQUESTS": env("ATOMIC_REQUESTS"),
    }
}
