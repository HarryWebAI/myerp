from rest_framework import serializers
from .models import Client, FollowUpRecord
from apps.staff.serializers import StaffSerializer
from apps.staff.models import ERPUser
from django.utils import timezone


class FollowUpRecordSerializer(serializers.ModelSerializer):
    """跟进记录序列化器"""
    staff_name = serializers.CharField(source='staff.name', read_only=True)
    
    class Meta:
        model = FollowUpRecord
        fields = ['uid', 'client', 'staff', 'staff_name', 'content', 'created_at']
        read_only_fields = ['uid', 'created_at']


class ClientListSerializer(serializers.ModelSerializer):
    """客户列表序列化器"""
    staff_name = serializers.CharField(source='staff.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    latest_follow_time = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Client
        fields = ['uid', 'name', 'telephone', 'level', 'level_display', 
                  'last_follow_time', 'latest_follow_time', 'is_overdue', 
                  'staff', 'staff_name', 'created_at']
        read_only_fields = ['uid', 'created_at', 'last_follow_time']


class ClientDetailSerializer(serializers.ModelSerializer):
    """客户详情序列化器"""
    staff_name = serializers.CharField(source='staff.name', read_only=True)
    staff = serializers.PrimaryKeyRelatedField(queryset=ERPUser.objects.all())
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    latest_follow_time = serializers.DateTimeField(read_only=True)
    follow_records = FollowUpRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Client
        fields = ['uid', 'name', 'telephone', 'address', 'remark', 
                  'level', 'level_display', 'last_follow_time', 'latest_follow_time', 
                  'is_overdue', 'staff', 'staff_name', 'follow_records', 
                  'created_at', 'updated_at']
        read_only_fields = ['uid', 'created_at', 'updated_at', 'last_follow_time']


class ClientCreateSerializer(serializers.ModelSerializer):
    """客户创建序列化器"""
    class Meta:
        model = Client
        fields = ['name', 'telephone', 'address', 'remark', 'level', 'staff']
    
    def create(self, validated_data):
        # 创建客户时，设置最后跟进时间为当前时间
        validated_data['last_follow_time'] = timezone.now()
        return super().create(validated_data)


class FollowUpCreateSerializer(serializers.ModelSerializer):
    """跟进记录创建序列化器"""
    client_level = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FollowUpRecord
        fields = ['client', 'staff', 'content', 'client_level']
    
    def create(self, validated_data):
        # 从验证数据中取出客户分级
        client_level = validated_data.pop('client_level')
        # 创建跟进记录
        follow_record = super().create(validated_data)
        # 更新客户分级
        client = follow_record.client
        client.level = client_level
        client.save(update_fields=['level'])
        return follow_record 