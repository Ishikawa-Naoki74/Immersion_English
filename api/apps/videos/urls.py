from django.urls import path
from . import views
from .views import VideosView, YoutubeTranscriptView, HighlightView, HighlightDetailView

urlpatterns = [
    path('videos/', views.VideosView.as_view()),
    path('videos/<str:video_id>/', views.VideosView.as_view()),
    path('videos/<str:video_id>/transcript/', views.YoutubeTranscriptView.as_view()),
    # ハイライト機能
    path('highlights/', views.HighlightView.as_view()),
    path('highlights/<int:highlight_id>/', views.HighlightDetailView.as_view()),
]