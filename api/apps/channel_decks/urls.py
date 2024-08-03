from django.urls import path
from . import views
from .views import ChannelDecksView

urlpatterns = [
    path('channels/', views.ChannelDecksView.as_view()),
    path('channels/<str:channel_id>/', views.ChannelDecksView.as_view())
]
