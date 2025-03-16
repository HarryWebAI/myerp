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

    uid = ShortUUIDField(primary_key=True)
    account = models.CharField(max_length=20, unique=True, blank=False)
    name = models.CharField(max_length=10)
    telephone = models.CharField(max_length=11, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_boss = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_storekeeper = models.BooleanField(default=False)

    objects = ERPUserManager()

    USERNAME_FIELD = "account"
    REQUIRED_FIELDS = ['name', 'telephone', 'password']
