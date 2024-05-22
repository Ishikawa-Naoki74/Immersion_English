from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import UserInfo
from .serializers import UserInfoSerializer

class Backend(APIView):
  def get(self, request, format=None):
    return Response({"message": "backend"})
# 実際にDBからデータを取得する
class UserInfoView(APIView):
  def get(self, request, format=None):
    return Response({"message": "backend"})