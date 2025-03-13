from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from apps.staff.permissions import IsBoss,IsManager

from .models import Client, FollowUpRecord
from .serializers import (
    ClientListSerializer, 
    ClientDetailSerializer, 
    ClientCreateSerializer,
    FollowUpRecordSerializer,
    FollowUpCreateSerializer
)
from .paginations import ClientPagination


class ClientModelViewSet(viewsets.GenericViewSet,
                         viewsets.mixins.CreateModelMixin,
                         viewsets.mixins.RetrieveModelMixin,
                         viewsets.mixins.UpdateModelMixin,
                         viewsets.mixins.ListModelMixin):
    """
    客户管理视图集
    
    list: 获取客户列表
    retrieve: 获取客户详情
    create: 创建客户
    update: 更新客户信息
    follow: 跟进客户
    """
    queryset = Client.objects.all()
    serializer_class = ClientListSerializer
    permission_classes = [IsAuthenticated, IsBoss | IsManager]
    pagination_class = ClientPagination
    
    def get_queryset(self):
        """根据用户权限返回不同的查询集"""
        user = self.request.user
        request = self.request
        
        # 基于用户权限确定基础查询集
        if user.is_boss:
            # 老板可以查看所有客户
            queryset = Client.objects.all()
        else:
            # 普通员工只能查看自己的客户
            queryset = Client.objects.filter(staff=user)
        
        # 获取单个客户详情时不应用默认筛选规则
        if self.action == 'retrieve':
            return queryset
        
        # 处理筛选参数
        if request.query_params:
            # 按客户级别筛选
            level = request.query_params.get('level')
            if level and level.isdigit():
                level = int(level)
                queryset = queryset.filter(level=level)
            else:
                # 默认排除已成交(0)和已流失(5)的客户
                queryset = queryset.exclude(level__in=[0, 5])
            
            # 按客户名称筛选
            name = request.query_params.get('name')
            if name:
                queryset = queryset.filter(name__contains=name)
            
            # 按电话筛选
            telephone = request.query_params.get('telephone')
            if telephone:
                queryset = queryset.filter(telephone__contains=telephone)
        else:
            # 没有筛选参数时，默认排除已成交和已流失的客户
            queryset = queryset.exclude(level__in=[0, 5])
        
        # 按客户级别和最后跟进时间排序（最久未跟进的排在前面）
        return queryset.order_by('level', 'last_follow_time')
    
    def get_serializer_class(self):
        """根据不同的操作返回不同的序列化器"""
        if self.action == 'retrieve':
            return ClientDetailSerializer
        elif self.action == 'create':
            return ClientCreateSerializer
        elif self.action == 'follow':
            return FollowUpCreateSerializer
        return ClientListSerializer
    
    def create(self, request, *args, **kwargs):
        """创建客户"""
        # 如果不是老板，则只能创建自己负责的客户
        if not request.user.is_boss:
            request.data['staff'] = request.user.uid
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """更新客户信息"""
        instance = self.get_object()
        
        # 如果不是老板，不能修改客户的所属员工
        if not request.user.is_boss and 'staff' in request.data:
            return Response({"detail": "您没有权限修改客户的所属员工"}, status=status.HTTP_403_FORBIDDEN)
        
        # 使用ClientDetailSerializer序列化更新数据
        serializer = ClientDetailSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def follow(self, request, *args, **kwargs):
        """跟进客户"""
        client = self.get_object()
        
        # 确保只有负责的员工或老板可以跟进客户
        if not request.user.is_boss and client.staff != request.user:
            return Response({"detail": "您没有权限跟进此客户"}, status=status.HTTP_403_FORBIDDEN)
        
        # 添加客户和员工信息到请求数据
        data = request.data.copy()
        data['client'] = client.uid
        data['staff'] = request.user.uid
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 返回更新后的客户详情
        client_serializer = ClientDetailSerializer(client)
        return Response(client_serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """获取已过期需要跟进的客户列表"""
        # 获取基本的查询集，这里会应用上面的筛选逻辑
        queryset = self.get_queryset()
        
        # 如果没有明确的级别筛选，确保排除不需要跟进的客户级别
        level = request.query_params.get('level')
        if not level or not level.isdigit():
            queryset = queryset.filter(~Q(level=0) & ~Q(level=4) & ~Q(level=5))
        
        # 在Python层面过滤过期客户，因为is_overdue是计算属性
        overdue_clients = [client for client in queryset if client.is_overdue]
        
        # 排序：先按客户级别，再按最后跟进时间的升序排序（最久未跟进的排前面）
        overdue_clients.sort(key=lambda x: (x.level, x.last_follow_time or timezone.now().replace(year=2000)))
        
        # 不进行分页，直接返回所有需要跟进的客户
        serializer = self.get_serializer(overdue_clients, many=True)
        return Response(serializer.data)

class AllClientViewSet(viewsets.GenericViewSet,
                      viewsets.mixins.ListModelMixin):
    """
    获取所有客户
    """
    queryset = Client.objects.all()
    serializer_class = ClientListSerializer
    permission_classes = [IsAuthenticated, IsBoss | IsManager]

