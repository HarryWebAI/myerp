# 简介
- myerp是一款个人门店仓库管理工具, 他包括`库存管理`, `客户管理`, `订单管理`四大功能.
1. 在库存管理方面,具有以下功能:
    - 针对`品牌`的增改查
    - 针对`类别`的增改查
    - 针对`商品`的增改查
    - `发货`功能
    - `收货`功能
    - 配合订单管理的`出库`功能

# 开发日志D01
### 创建后端项目
- 使用pycharm创建django项目
    - 项目名称 `myerp_backend`
    - python解释器版本: `3.12.8`
    - django版本`5.1.6`
- 安装rest_framework:`pip install djangorestframework`(3.15.2)
- 安装mysql_client:`pip install mysqlclient`(2.2.7)
### 整理项目
1. 建数据库, 登录mysql, `create database myerp charst utf8mb4`
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

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-)ad(j6oy4_(t^t5_p429+1l=5#pi!_2s$@%14#^@*qsn+g8txm'

DEBUG = True
ALLOWED_HOSTS = []

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

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
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myerp_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myerp_backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        "NAME": env.str('DB_NAME', "myerp"),
        "USER": env.str('DB_USER', "root"),
        "PASSWORD": env.str("DB_PASSWORD", "123456"),
        "HOST": env.str('DB_HOST', 'localhost'),
        "PORT": env.str('DB_PORT', '3306'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 配置时区
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = False


STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```
5. git托管, 略

