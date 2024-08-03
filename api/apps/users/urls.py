from django.urls import path
from . import views
from .views import  FirebaseLoginView

urlpatterns = [
    path('login/', FirebaseLoginView.as_view(), name='firebase_login'),
]