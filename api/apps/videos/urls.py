from django.urls import path
from . import views
from .views import VideosView, YoutubeTranscriptView

urlpatterns = [
    path('videos/', views.VideosView.as_view()),
    path('videos/<str:video_id>/', views.VideosView.as_view()),
    path('videos/<str:video_id>/transcript/', views.YoutubeTranscriptView.as_view()),
]