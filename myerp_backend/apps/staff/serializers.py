from rest_framework import serializers

from .models import ERPUser
import re


class LoginSerializer(serializers.Serializer):
    """
    登录序列化
    """
    account = serializers.CharField(required=True)
    password = serializers.CharField(required=True, max_length=30, min_length=6)

    # 校验传入的数据
    def validate(self, attrs):
        account = attrs.get('account')
        password = attrs.get('password')

        if account and password:
            user = ERPUser.objects.filter(account=account).first()

            if not user:
                raise serializers.ValidationError('请输入正确的账号!')
            if not user.check_password(password):
                raise serializers.ValidationError('请输入正确的密码!')

            if user.is_active == False:
                raise serializers.ValidationError('用户被锁定!如有疑问请联系管理员!')

        else:
            raise serializers.ValidationError('请输入账号密码!')

        attrs['user'] = user

        return attrs


class StaffSerializer(serializers.ModelSerializer):
    """
    员工序列化器
    """
    class Meta:
        model = ERPUser
        fields = ['uid', 'account', 'name', 'telephone', 'is_active', 'is_manager', 'is_storekeeper']
        read_only_fields = ['uid']

    def validate_account(self, value):
        """验证账号唯一性和格式"""
        if len(value) < 4 or len(value) > 20:
            raise serializers.ValidationError("账号长度必须在4-20个字符之间")
        
        # 检查账号是否已存在
        if ERPUser.objects.filter(account=value).exists():
            raise serializers.ValidationError("该账号已存在")
        
        return value
    
    def validate_telephone(self, value):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("请输入正确的手机号格式")
        return value
    
    def validate_name(self, value):
        """验证姓名格式"""
        if len(value) < 2 or len(value) > 10:
            raise serializers.ValidationError("姓名长度必须在2-10个字符之间")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    重置密码序列化
    """

    old_password = serializers.CharField(min_length=6, max_length=30)
    new_password = serializers.CharField(min_length=6, max_length=30)
    check_new_password = serializers.CharField(min_length=6, max_length=30)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        check_new_password = attrs.get('check_new_password')

        if new_password != check_new_password:
            raise serializers.ValidationError('两次密码输入不一致!')
        if new_password == old_password:
            raise serializers.ValidationError('新旧密码不能相同!')

        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError('旧密码不正确!')

        return attrs


class CreateStaffSerializer(StaffSerializer):
    """
    创建员工专用序列化器
    """
    password = serializers.CharField(write_only=True, required=False, help_text="密码，不传则使用默认密码111111")
    
    class Meta(StaffSerializer.Meta):
        fields = StaffSerializer.Meta.fields + ['password']
    
    def create(self, validated_data):
        """创建员工"""
        # 如果没有提供密码，则使用默认密码111111
        password = validated_data.pop('password', '111111')
        
        # 创建用户基本信息
        user = ERPUser(
            account=validated_data['account'],
            name=validated_data['name'],
            telephone=validated_data['telephone'],
            is_manager=validated_data.get('is_manager', False),
            is_storekeeper=validated_data.get('is_storekeeper', False)
        )
        
        # 安全地设置密码
        user.set_password(password)
        user.save()
        
        return user


class StaffUpdateSerializer(serializers.ModelSerializer):
    """
    员工信息更新序列化器
    """
    class Meta:
        model = ERPUser
        fields = ['name', 'telephone', 'is_active', 'is_manager', 'is_storekeeper']
    
    def validate_telephone(self, value):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("请输入正确的手机号格式")
        return value
    
    def validate_name(self, value):
        """验证姓名格式"""
        if len(value) < 2 or len(value) > 10:
            raise serializers.ValidationError("姓名长度必须在2-10个字符之间")
        return value
    
    def update(self, instance, validated_data):
        """更新员工信息"""
        instance.name = validated_data.get('name', instance.name)
        instance.telephone = validated_data.get('telephone', instance.telephone)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_manager = validated_data.get('is_manager', instance.is_manager)
        instance.is_storekeeper = validated_data.get('is_storekeeper', instance.is_storekeeper)
        
        instance.save()
        return instance
