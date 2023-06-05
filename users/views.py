from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomTokenObtainPairSerializer, Userserializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions


class Userview(APIView):
    def post(self, request):
      serializer = Userserializer(data=request.data)
      if serializer.is_valid():
        serializer.save()
        return Response({"message":"회원가입완료"}, status=status.HTTP_201_CREATED)
      else:
        return Response({"message":f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class mockview(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        print("로그인된 유저")
        print(request)
        return Response({"로그인된 유저이름 /// "+f"{request.user}"}, status=status.HTTP_200_OK)