from rest_framework.views import APIView
from django.http import JsonResponse

class FirebaseLoginView(APIView):
    def post(self, request):
        return JsonResponse({'message': 'Firebase authentication disabled'}, status=400)