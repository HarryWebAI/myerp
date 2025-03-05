from rest_framework import serializers

from .models import ERPUser


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
    员工_模型序列化
    """

    class Meta:
        model = ERPUser
        exclude = ['password', 'groups', 'user_permissions']


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
