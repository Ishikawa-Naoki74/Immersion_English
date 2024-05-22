from .base import *
# firebase admin SDKの初期化
cred = credentials.Certificate(os.path.join(BASE_DIR, "config/firebase/firebase-adminsdk.json"))
firebase_admin.initialize_app(cred)

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
