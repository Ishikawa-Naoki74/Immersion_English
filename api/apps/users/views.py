from rest_framework.views import APIView
import firebase_admin
from firebase_admin import auth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Users

@method_decorator(csrf_exempt, name='dispatch')
class FirebaseLoginView(APIView):

    def post(self, request):
        return self.firebase_login(request)

    def firebase_login(self, request):
        token = request.data.get('token')
        
        try:
            # Verify the token with Firebase Admin SDK
            decode_token = auth.verify_id_token(token)
            firebase_uid = decode_token['uid']
            # Get or create the user in the Django database
            user, created = Users.objects.get_or_create(user_id=firebase_uid)
            return JsonResponse({'message': 'User logged in', 'user_id': user.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
