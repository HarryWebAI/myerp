from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .authentications import generate_jwt
from .models import ERPUser

from rest_framework.permissions import IsAuthenticated


class LoginView(APIView):
    """
    登录接口
    """

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()

            token = generate_jwt(user)
            return Response({'token': token, 'user': serializers.StaffSerializer(user).data})

        else:

            detail = list(serializer.errors.values())[0][0]
            return Response(data={'detail': detail}, status=status.HTTP_401_UNAUTHORIZED)

class ResetPasswordView(APIView):
    """
    重置密码接口
    """
    permission_classes = [IsAuthenticated]

    def put(self,request):
        serializer = serializers.ResetPasswordSerializer(data=request.data, context={'request': request})

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
        staff_list = ERPUser.objects.filter(is_active=True).order_by('-is_boss', '-is_manager', '-is_storekeeper').all()
        serializer = serializers.StaffSerializer(staff_list, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateStaffView(APIView):
    """
    创建员工接口
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 只有老板可以创建员工
        if not request.user.is_boss:
            return Response({"detail": "只有老板可以创建员工"}, status=status.HTTP_403_FORBIDDEN)
        
        # 序列化验证表单数据(传入 account name telephone)
        serializer = serializers.CreateStaffSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建员工(初始密码111111)
        try:
            staff = serializer.save()
            # 返回数据
            return Response(
                serializers.StaffSerializer(staff).data, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateStaffView(APIView):
    """
    更新员工接口
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, uid):
        # 仅老板可以修改员工角色
        if not request.user.is_boss:
            return Response({"detail": "您没有权限修改员工信息"}, status=status.HTTP_403_FORBIDDEN)
        
        # 查找要修改的员工
        try:
            staff = ERPUser.objects.get(uid=uid)
        except ERPUser.DoesNotExist:
            return Response({"detail": "员工不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 禁止修改老板角色
        if staff.is_boss:
            return Response({"detail": "不能修改老板的角色"}, status=status.HTTP_403_FORBIDDEN)
        
        # 使用序列化器验证数据
        serializer = serializers.StaffUpdateSerializer(staff, data=request.data, partial=True)
        
        if serializer.is_valid():
            # 保存更新
            serializer.save()
            return Response(serializers.StaffSerializer(staff).data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

