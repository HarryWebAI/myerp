from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentications import generate_jwt
from .serializers import LoginSerializer, StaffSerializer,ResetPasswordSerializer
from .models import ERPUser

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

class StaffListView(APIView):
    """
    获取员工列表接口
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 检查用户权限，只有老板或管理员才能获取员工列表
        if not (request.user.is_boss or request.user.is_manager):
            return Response(
                data={'detail': '您没有权限获取员工列表'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取所有员工
        staff_list = ERPUser.objects.filter(is_active=True)
        serializer = StaffSerializer(staff_list, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
