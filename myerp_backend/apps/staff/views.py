from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentications import generate_jwt
from .serializers import LoginSerializer, StaffSerializer,ResetPasswordSerializer

from rest_framework.permissions import IsAuthenticated


class LoginView(APIView):
    """
    登录接口
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()

            token = generate_jwt(user)
            return Response({'token': token, 'user': StaffSerializer(user).data})

        else:

            detail = list(serializer.errors.values())[0][0]
            return Response(data={'detail': detail}, status=status.HTTP_401_UNAUTHORIZED)

class ResetPasswordView(APIView):
    """
    重置密码接口
    """
    permission_classes = [IsAuthenticated]

    def put(self,request):
        serializer = ResetPasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            password = serializer.validated_data.get('new_password')
            request.user.set_password(password)
            request.user.save()

            return Response(data={'message': '密码修改成功!'}, status=status.HTTP_200_OK)
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response(data={'detail': detail}, status=status.HTTP_403_FORBIDDEN)
