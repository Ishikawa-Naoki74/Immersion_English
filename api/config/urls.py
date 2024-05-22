from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
  SpectacularAPIView,
  SpectacularRedocView,
  SpectacularSwaggerView, 
  )
# プロジェクト全体の設定
urlpatterns = [
    path("admin/", admin.site.urls),
    # localhost/8000/api/schema にアクセスするとテキストファイルをダウンロードできる
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # SwaggerUIの設定→localhost/8000/api/docs にアクセスするとSwaggerUIが表示されるよう設定
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Redocの設定→localhost/8000/api/redoc にアクセスするとRedocが表示されるよう設定
    path("api/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/users/", include("apps.users.urls")),
]
# TODO extend_schemaでドキュメンテーションの追加設定