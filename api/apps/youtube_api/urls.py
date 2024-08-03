from django.urls import path
from . import views
from .views import ChannelSearchView
from .views import ChannelVideosView

urlpatterns = [
    path('channels/', ChannelSearchView.as_view()),
    path('videos/', ChannelVideosView.as_view()),
]