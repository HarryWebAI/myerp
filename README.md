# 简介

- myerp 是一款个人门店仓库管理工具, 他包括`库存管理`, `客户管理`, `订单管理`四大功能.

1. 在库存管理方面,具有以下功能:
   - 针对`品牌`的增改查
   - 针对`类别`的增改查
   - 针对`商品`的增改查
   - `发货`功能
   - `收货`功能
   - 配合订单管理的`出库`功能

# 开发日志 D01

### 创建后端项目

- 使用 pycharm 创建 django 项目
  - 项目名称 `myerp_backend`
  - python 解释器版本: `3.12.8`
  - django 版本`5.1.6`
- 安装 rest_framework:`pip install djangorestframework`(3.15.2)
- 安装 mysql_client:`pip install mysqlclient`(2.2.7)

### 后端:整理项目

1. 建数据库, 登录 mysql, `create database myerp charst utf8mb4`
2. 安装`pip install django-environ`用于配置环境, 新建`~/.env`环境配置文件

```conf
# 前端地址
FRONTEND_URL=

# 数据库
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# celery
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=

# redis缓存
CACHE_URL=
```

3. 新建`~/.gitignore`声明不追踪`~/.env`
4. 编辑`settings.py`

```python
from pathlib import Path
import os
import environ

# ...

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ...

INSTALLED_APPS = [
    # 注释掉不需要的app
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',

    # 加载drf
    'rest_framework'
    # 项目app
]

MIDDLEWARE = [
    # 注释掉不需要的中间件
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ...

WSGI_APPLICATION = 'myerp_backend.wsgi.application'

# 数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        "NAME": env.str('DB_NAME'),
        "USER": env.str('DB_USER'),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str('DB_HOST', 'localhost'),
        "PORT": env.str('DB_PORT', '3306'),
    }
}

# 配置时区
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = False


STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

5. git 托管, 略

### 后端staff模块: 重写user
1. 新建staff模块: `python manage.py startapp staff`
2. 移动`~/staff`统一管理到`~/apps/`下
3. 下载django用的shortuuid包: `pip install django-shortuuidfield`
4. 重写user模型: `~/apps/staff/models.py`
```python
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from shortuuidfield import ShortUUIDField


class ERPUserManager(BaseUserManager):
    """
    重写 UserManager
    """
    use_in_migrations = True

    # 创建用户
    def _create_user(self, account, name, telephone, password, **extra_fields):
        if not account:
            raise ValueError("必须设置登录账号!")
        if not name:
            raise ValueError("必须填写姓名!")
        if not telephone:
            raise ValueError("必须填写电话!")
        user = self.model(account=account, name=name, telephone=telephone, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    # 普通用户
    def create_user(self, account=None, name=None, telephone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(account, name, telephone, password, **extra_fields)

    # 超级用户
    def create_superuser(self, account=None, name=None, telephone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_boss", True)
        extra_fields.setdefault("is_manager", True)
        extra_fields.setdefault("is_storekeeper", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置is_staff = True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置is_superuser = True")
        if extra_fields.get("is_boss") is not True:
            raise ValueError("超级用户必须设置is_boss = True")
        if extra_fields.get("is_manager") is not True:
            raise ValueError("超级用户必须设置is_manager = True")
        if extra_fields.get("is_storekeeper") is not True:
            raise ValueError("超级用户必须设置is_storekeeper = True")

        return self._create_user(account, name, telephone, password, **extra_fields)


class ERPUser(AbstractBaseUser, PermissionsMixin):
    """
    重写 User
    """

    uid = ShortUUIDField(primary_key=True)  # uuid
    account = models.CharField(max_length=20, unique=True, blank=False)  # 登录账号
    name = models.CharField(max_length=10)  # 姓名
    telephone = models.CharField(max_length=11)  # 联系电话

    is_active = models.BooleanField(default=True)  # django自带, 是否激活, 默认为是
    is_staff = models.BooleanField(default=True)  # django自带, 是否是员工, 默认为是
    is_boss = models.BooleanField(default=False)  # 新建时默认不是老板
    is_manager = models.BooleanField(default=False)  # 新建时默认不是经理
    is_storekeeper = models.BooleanField(default=False)  # 新建时默认不是仓库管理员

    objects = ERPUserManager()

    # USERNAME_FIELD 是用来做鉴权的, 作为 authenticate() 中的username参数
    USERNAME_FIELD = "account"  # 重写的User模型中, 我们用account字段作为登录账号
    # REQUIRED_FIELDS 指定哪些字段是必须要传入的, 但是不能重复包含EMAIL_FIELD和USERNAME_FIELD已经设置过的值
    REQUIRED_FIELDS = ['name', 'telephone', 'password']
```
5. 创建和执行迁移, 实现建库`python manage.py makemigration`, `python manage.py migrate`(需先确保数据库连接无误)
6. 新建manage命令, 实现初始化超级用户新建路径和文件并编辑: `~/apps/staff/management/commands/initsuperuser.py`
```python
from django.core.management.base import BaseCommand
from apps.staff.models import ERPUser

class Command(BaseCommand):
    def handle(self, *args, **options):
        account = ERPUser.objects.create_superuser(account='liuhaoyu', name='刘浩宇', telephone='13006462272',
                                                   password='111111')

        self.stdout.write('超级用户创建成功! 初始密码[6个1]! 请迅速登录并修改密码以确保系统安全!')
```
> 复习: 该文件的名称对应 `python manage.py <执行的动作>`
> 该文件必须这么写(类名必须叫Command, 继承的类必须是BaseCommand, 定义的函数必须叫handle)

7. 执行命令创建初始化角色`python manage.py initsuperuser`

### 后端staff模块: 登录接口
1. 安装jwt包: `pip install PyJWT`
2. 创建认证器并编辑: `~/apps/staff/authentications.py`
```python
import jwt
import time
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from jwt.exceptions import ExpiredSignatureError
from .models import ERPUser


# 生成 jwt_token
def generate_jwt(user):

    # 过期时间
    expire_time = time.time() + 60 * 60 * 24 * 7
    return jwt.encode({"userid": user.pk, "exp": expire_time}, key=settings.SECRET_KEY)


class UserTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 这里的request：是rest_framework.request.Request对象
        return request._request.user, request._request.auth


class JWTAuthentication(BaseAuthentication):
    keyword = 'JWT'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = "不可用的JWT请求头!"
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = '不可用的JWT请求头!JWT Token中间不应该有空格!'
            raise exceptions.AuthenticationFailed(msg)

        try:
            jwt_token = auth[1]
            jwt_info = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms='HS256')
            userid = jwt_info.get('userid')
            try:
                # 绑定当前user到request对象上
                user = ERPUser.objects.get(pk=userid)
                setattr(request, 'user', user)
                return user, jwt_token
            except:
                msg = '用户不存在!'
                raise exceptions.AuthenticationFailed(msg)
        except ExpiredSignatureError:
            msg = "JWT Token已过期!"
            raise exceptions.AuthenticationFailed(msg)
```
3. 创建序列化器并编辑`~/apps/staff/serializers.py`
```python
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
```
4. 实现接口`LoginView`, 编辑`~/apps/staff/views.py`:
```python
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentications import generate_jwt
from .serializers import LoginSerializer, StaffSerializer


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
            # 序列化器抛出的异常可以通过这样的方式取得具体值
            detail = list(serializer.errors.values())[0][0]
            # 并将其交给data.detail传给前端, 同时返回401未认证状态码
            return Response(data={'detail': detail}, status=status.HTTP_401_UNAUTHORIZED)
```
5. 配置路由新建`~/apps/staff/urls.py` 以及主路由 `~/myerp_backend/urls.py`
```python
# 子路由
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login')
]

# 主路由
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login')
]
```
7. 使用postman测试接口, 新建集合`myerp`, 新建请求`myerp/登录接口`, 分别输入正确和错误的账号密码
    - 正确则返回JSON: 带token和User信息的
    - 错误则返回序列化器最先抛出的异常以及401状态码