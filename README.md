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

### 后端 staff 模块: 重写 user

1. 新建 staff 模块: `python manage.py startapp staff`
2. 移动`~/staff`统一管理到`~/apps/`下
3. 下载 django 用的 shortuuid 包: `pip install django-shortuuidfield`
4. 重写 user 模型: `~/apps/staff/models.py`

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
6. 新建 manage 命令, 实现初始化超级用户新建路径和文件并编辑: `~/apps/staff/management/commands/initsuperuser.py`

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
> 该文件必须这么写(类名必须叫 Command, 继承的类必须是 BaseCommand, 定义的函数必须叫 handle)

7. 执行命令创建初始化角色`python manage.py initsuperuser`

### 后端 staff 模块: 登录接口

1. 安装 jwt 包: `pip install PyJWT`
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

7. 使用 postman 测试接口, 新建集合`myerp`, 新建请求`myerp/登录接口`, 分别输入正确和错误的账号密码 - 正确则返回 JSON: 带 token 和 User 信息的 - 错误则返回序列化器最先抛出的异常以及 401 状态码
   > 接下来的开发日志将不会粘贴全部的代码作为笔记, 仅提供思路, 否则日志太冗余了.

### 创建前端项目:

- 在`myerp/`路径下执行命令`npm create vue@latest`: 创建 vue 项目(3.5.13)
  - 名称`myerp_frontend`
  - 勾选`Pinia`(3.0.1)
  - 勾选`Router`(4.5.0)
- 进入`myerp_fronted/`执行命令
  - `npm install`: 根据依赖声明安装所需的 node 包
  - `npm run format`: 格式化代码
  - `npm run dev`: 启动项目

### 前端: 整理项目

> `@` = `~/src`

1. 删除`@/assets/`, `@/components/`和`@/views/`下的所有东西
2. 编辑`@/App.vue`入口文件, 仅保留路由出口, 并在样式声明: 全局样式(无 scoped)无内外边距

```vue
<script setup></script>

<template>
  <router-view></router-view>
</template>

<style>
* {
  margin: 0;
  padding: 0;
}
</style>
```

3. 新建`~/.env.development`和`.env.production`: 环境配置文件

```conf
# 开发环境
VITE_BASE_URL = 'http://localhost:8000/api'
# 生产环境
VITE_BASE_URL = '/api'
```

### 前端:导入 Element-plus 并实现框架

1. `npm install element-plus --save`: 安装 Element-plus
2. `npm install @element-plus/icons-vue --save`: 安装图标
3. 编辑整理`@/main.js`中, 顺便声明使用 Element-plus 和 el-icon 图标

```js
import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

// 导入 Element-plus, 样式表, 图标库
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";

const app = createApp(App);

app.use(createPinia());
app.use(router);

// 声明使用Element-plus
app.use(ElementPlus);
// 遍历图标库使其作为组件加入vue中
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

app.mount("#app");
```

3. 新建`@/views/MainView.vue`, 略

4. 整理路由文件`@/router/index.js`:

```js
import { createRouter, createWebHistory } from "vue-router";
import MainView from "@/views/MainView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // 主页对应框架页面
      path: "/",
      name: "main",
      component: MainView,
    },
  ],
});

export default router;
```

### 前端: 实现登录页面

1. 新建`@/views/LoginView.vue`(页面可复用)

```vue
<script setup>
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";

const formLabelWidth = 80;
let loginForm = ref();
let loginFormData = reactive({
  account: "",
  password: "",
});
const loginFormRules = reactive({
  account: [
    { required: true, message: "必须填写登录账号!", trigger: "blur" },
    { min: 4, max: 20, message: "登录账号应该在4~20位之间!", trigger: "blur" },
  ],
  password: [
    { required: true, message: "必须填写登录密码!", trigger: "blur" },
    { min: 6, max: 30, message: "登录密码位数不对!", trigger: "blur" },
  ],
});

const onLogin = () => {
  loginForm.value.validate((valid, fields) => {
    if (valid) {
      ElMessage.success("验证通过正在登录!");
      console.log(loginFormData);
    } else {
      for (let key in fields) {
        ElMessage.error(fields[key][0]["message"]);
      }
    }
  });
};
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h3 class="title">MyERP</h3>
      <el-form ref="loginForm" :model="loginFormData" :rules="loginFormRules">
        <el-form-item
          label="登录账号"
          prop="account"
          :label-width="formLabelWidth"
        >
          <el-input type="text" v-model="loginFormData.account" />
        </el-form-item>
        <el-form-item
          label="登录密码"
          prop="password"
          :label-width="formLabelWidth"
        >
          <el-input type="password" v-model="loginFormData.password" />
        </el-form-item>
        <br />
        <button type="button" class="login-btn" @click="onLogin">
          点击登录
        </button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #a5acf1, #2b369c);
}

.login-box {
  background: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 400px;
}

.title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #6e7dff;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.login-btn:hover {
  background: #5a6bd8;
}
</style>
```

2. 编辑`@/routes/index.js`, 添加路由

```js
// ...
import LoginView from "@/views/LoginView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ...

    // 添加路由
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
  ],
});

export default router;
```

3. 安装 axios: `npm install axios --save`
4. 新建`@/api/http.js`用于封装像后台接口发送 http 请求的代码

```js
import axios from "axios";
// import { useAuthStore } from '@/stores/auth'

class Http {
  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_BASE_URL,
      timeout: 10000,
    });

    // this.instance.interceptors.request.use((config) => {
    //   const authStore = useAuthStore()
    //   const token = authStore.token
    //   if (token) {
    //     config.headers.Authorization = 'JWT' + ' ' + authStore.token
    //   }
    //   return config
    // })
  }

  post = (path, data) => {
    return (
      this.instance
        // 请求接口
        .post(path, data)
        // 如果成功(200)
        .then((response) => {
          return {
            status: response.status,
            data: response.data,
          };
        })
        // 如果失败(非200)
        .catch((error) => {
          return {
            status: error.response.status,
            data: error.response.data,
          };
        })
    );
  };
}

export default Http;
```

> 注释的部分在完成`@/stores/auth.js`以后再取消注释: 注释部分是配置请求头, 给请求头添加上认证令牌信息用的

5. 新建`@/api/loginHttp.js`调取 post 请求

```js
import Http from "./http";

const http = new Http();

const login = (data) => {
  // 定义路由
  const path = "/staff/login/";
  // 调取http,请求接口
  return http.post(path, data);
};

export default { login };
```

6. pinia 存储用户数据, 新建`@/stores/auth.js`

```js
import { computed } from "vue";
import { defineStore } from "pinia";

// 配置常量名称
const USER_KEY = "JWT_TOKEN_FROM_MYERP_USER_INFO";
const TOKEN_KEY = "JWT_TOKEN_FROM_MYERP_TOKEN";

// 创建store对象
export const useAuthStore = defineStore("auth", () => {
  // 登录成功时调取: 在localStore中写入用户信息和认证令牌
  const setToken = (data) => {
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    localStorage.setItem(TOKEN_KEY, data.token);
  };

  // 退出登录时调取: 移除用户信息和认证令牌
  const clearToken = () => {
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(TOKEN_KEY);
  };

  // 定义计算属性 user: 尝试从本地存储中获取, 如果没有则为false
  let user = computed(() => {
    return localStorage.getItem(USER_KEY)
      ? JSON.parse(localStorage.getItem(USER_KEY))
      : false;
  });

  // 定义计算属性 token
  let token = computed(() => {
    return localStorage.getItem(TOKEN_KEY)
      ? localStorage.getItem(TOKEN_KEY)
      : false;
  });

  // 登录状态判定函数
  let isLogined = computed(() => {
    if (localStorage.getItem(USER_KEY) && localStorage.getItem(TOKEN_KEY)) {
      return true;
    }

    return false;
  });

  return { setToken, clearToken, user, token, isLogined };
});
```

7. 完成登录功能`@/views/LoginView.vue`

```js
// ...

// 表单label宽度
const formLabelWidth = 80;

// 老三样: 表单的ref, 表单项, 表单的验证规则
let loginForm = ref();
let loginFormData = reactive({
  account: "",
  password: "",
});
const loginFormRules = reactive({
  account: [
    { required: true, message: "必须填写登录账号!", trigger: "blur" },
    { min: 4, max: 20, message: "登录账号应该在4~20位之间!", trigger: "blur" },
  ],
  password: [
    { required: true, message: "必须填写登录密码!", trigger: "blur" },
    { min: 6, max: 30, message: "登录密码位数不对!", trigger: "blur" },
  ],
});

// 登录功能
const onLogin = () => {
  // 先用表单的ref.value.validate方法验证是表单项是否符合表单验证规则
  loginForm.value.validate((valid, fields) => {
    // 如果前端验证合规
    if (valid) {
      // 开始请求后端(从http.js返回到loginHttp.js再到这里, 它们return回来的都是一个Promise对象)
      loginHttp.login(loginFormData).then((result) => {
        // 该对象有两个值: 一个是http状态码(status), 一个是返回的数据(data)
        if (result.status == 200) {
          console.log(result.data);
          // 将用户信息写入浏览器存储
          authStore.setToken(result.data);
          // 跳转到首页
          router.push({ name: "main" });
        } else {
          // 读取错误信息
          ElMessage.error(result.data.detail);
        }
      });
    } else {
      // 如果前端验证不合规, 弹出验证错误信息
      for (let key in fields) {
        ElMessage.error(fields[key][0]["message"]);
      }
    }
  });
};
```

8. 取消`http.js`中关于请求头配置的注释

### 后端: 补充!跨域请求限制处理

> 测试时发现忘记处理跨域请求, 这一步应该在后端项目构建之初就进行处理

- 后端项目执行命令: `pip install django-cors-headers` 安装 cors-headers
- 编辑`settings.py`

```python
# ...加载app
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'corsheaders',  # 加载corshearders
]

# ...加载中间件, 注意应该放在
MIDDLEWARE = [
    # ...
    # corsheaders 务必放在 CommonMiddleware 前
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]

# ...简单配置
# cors配置
CORS_ALLOW_ALL_ORIGINS = True  # 开发阶段暂时允许所有域名跨域请求


'''
# 实际投入使用时应该配置:
CORS_ALLOW_ALL_ORIGINS = False  # 默认情况下,禁用所有跨域请求
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # 前端vue默认的的URL
]

# 允许请求的方法
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'PATCH',
]

# 允许的请求头
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]

# 如果需要携带 Cookie 或认证信息
CORS_ALLOW_CREDENTIALS = True
'''
```

### 前端: 增加路由守卫

- 编辑 `@/routes/index.js`, 给路由增加全局守卫

```js
import { useAuthStore } from "@/stores/auth";
import { ElMessage } from "element-plus";

// 在执行任何动作前
router.beforeEach((to) => {
  // 获取当前用户信息
  const authStore = useAuthStore();
  // 如果没有, 且不是访问 'login' 路由(登录页面)的话
  if (!authStore.isLogined && to.name != "login") {
    // 弹出错误
    ElMessage.error("请先登录!");
    // 跳转到登录页面
    return { name: "login" };
  }
});
```

### 前端: 完善框架页面

1. 组件化: 将重复的代码封装为组件, 通过传入不同的参数实现渲染不同的内容, 分别有:

   - `@/components/MainBox.vue`: 内容主体容器(所需参数:`title`)
   - `.../BoxHeader.vue`: 作为 MainBox 的子组件渲染主体头部(返回按键和页面标题)
   - `.../FormDialog.vue`: 表单对话框(所需参数:`v-model`=>表单开关属性 ref, `title`="对话框标题", `@submit`="绑定提交函数")
   - `.../PaginationView.vue`: 分页器(所需参数:`:page_size`=>每页多少条数据, `:total`=>一共多少条数据, `v-model`=>当前页数 )

   > 这些代码来自上一个项目`myoa`, 具有很好的复用性

2. 主页修改配色, 头部渲染当前用户, 提供下拉菜单(退出登录和重置密码功能), 并导入`MainBox`放在主体部分,略
3. 退出登录功能:

- 给退出登录绑定点击事件`@click="logout"`

```js
/**退出登录 */
const logout = () => {
  ElMessageBox.confirm("即将退出登录,确认?", "退出登录?", {
    confirmButtonText: "确认",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      ElMessage.success("成功退出!");
      authStore.clearToken();
      router.push({ name: "login" });
    })
    .catch(() => {
      ElMessage.info("取消退出!");
    });
};
```

4. 重置密码表单: (代码可复用)之后的各种对话框表单只需要复制下面的代码修改即可

```html
<FormDialog v-model="dialogVisible" title="修改密码" @submit="resetPassword">
  <el-form
    :model="resetPasswordFormData"
    :rules="resetPasswordFormRules"
    ref="resetPasswordForm"
    :label-width="80"
  >
    <el-form-item label="旧密码" prop="old_password">
      <el-input type="password" v-model="resetPasswordFormData.old_password" />
    </el-form-item>
    <el-form-item label="新的密码" prop="new_password">
      <el-input type="password" v-model="resetPasswordFormData.new_password" />
    </el-form-item>
    <el-form-item label="再输一次" prop="check_new_password">
      <el-input
        type="password"
        v-model="resetPasswordFormData.check_new_password"
      />
    </el-form-item>
  </el-form>
</FormDialog>
```

5. 重置密码功能

```js
/**表单开关 */
let dialogVisible = ref(false);
const toggleResetPasswordForm = () => {
  dialogVisible.value = true;
};

/**修改密码 */
let resetPasswordForm = ref();
let resetPasswordFormData = reactive({
  user: authStore.user,
  old_password: "",
  new_password: "",
  check_new_password: "",
});
const resetPasswordFormRules = reactive({
  old_password: [
    { required: true, message: "必须填写旧密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度必须在6~30位之间", trigger: "blur" },
  ],

  new_password: [
    { required: true, message: "必须填写旧密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度必须在6~30位之间", trigger: "blur" },
  ],

  check_new_password: [
    { required: true, message: "必须填写旧密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度必须在6~30位之间", trigger: "blur" },
  ],
});

const resetPassword = () => {
  // 还没完成
  console.log(resetPasswordFormData);
};
```

### 后端: staff 模块完成修改密码接口

1. 序列化器: 用户需要传入 3 个字段: 旧密码,新密码,确认新密码, 而我需要在序列化器里实现:

   - 验证新旧密码是否不同
   - 验证新密码和"再输一遍"的新密码是否相同
   - 根据当前登录的用户, 验证旧密码是否正确

   > 重点在于如何在序列化器里获取当前登录的用户?

   - 使用`user = self.context['request'].user`获取当前用户

   > 如何传入`context`?

2. 接口: 继承 `APIView`, 定义`put`函数
   - 函数内部我需要实例化序列化器, 并且通过 context 将带用户信息的请求对象交给序列化器
   - `serializer = ResetPasswordSerializer(data=request.data, context={'request': request})`
   - 验证通过, 更新用户信息(request.user.set_password(), save())
   - 验证失败, 返回错误信息
3. 路由, 略
4. postman 测试, 请求头加上认证令牌`Authorization = JWT + 登录接口获取的Token`, 略

### 前端: 修改密码功能

1. 表单验证:配置好验证规则后, 表单 ref 对象调用 validate 函数: `loginForm.value.validate((valid, fields)=>{})`
   - `{}`内如果验证通过`valid`为真, 提交请求
   - valid 说明前端验证失败, 遍历错误信息
2. 提交请求:`http.js`封装 `put()` 函数, 然后`loginHttp.js`完成`resetPassword()`函数:

   - 配置地址, 请求接口
   - 这里因为接口路由没有指定为`../<uid>`, 所以直接访问`'/staff/reset/'`即可(put 请求按理来说应该传入要修改数据的主键)
   - 但是, 我们要修改的信息直接存储在`request.user`中

3. 提交成功后, 后端写的是`return Response(data={'messsage':'修改密码成功'})`, 所以应该`ElMessage.success(result.data.message)`, 如果失败则是`ElMessage.error(result.data.detail)`

### 后端: brand 品牌模块

1. 创建 app: `python manage.py startapp brand`, 放进`~/apps/`中
2. 注册 app: `settings.py`
3. 编写模型`models.py`, 执行迁移建表, 略
4. 命令初始化数据
   - 新建和编辑`~/apps/brand/management/commands/initbrands.py`
   - 然后`python manage.py initbrands`
5. 编写序列化器, 继承`ModelSerializer`子类 `Meta` 声明`model`和`fields`
6. 编写接口(模型视图集): 继承`ModelViewSet`, 声明`queryset`和`serializer_class`
7. 注册模块路由

```python
# 导入路由
from rest_framework.routers import DefaultRouter
# 导入视图
from .views import BrandModelViewSet

# 配置应用名称
app_name = 'brand'

# 实例化路由并注册
router = DefaultRouter()
router.register('brand',BrandModelViewSet,basename='brand')

# 拼接在传统路由中
urlpatterns = [] + router.urls
```

8. 主路由导入,前缀只有`api/`, 使用`include()`导进来, 略
9. postman 测试, 略
   - `GET ./api/brand/` => 获取列表
   - `GET ./api/brand/<pk>/` => 获取指定行详情
   - `POST ./api/brand` => 增加一行数据
   - `PUT ./api/brand/<pk>` => 修改指定行数据
   - `DELETE ./api/brand/<pk>` => 删除指定行数据

### 后端: category 产品种类模块

- 跟上面一样, 略

### 后端: 忘记权限认证

- 在 brand 模块和 category 模块的模型视图集接口上,都要求必须登录才可以操作
  - 导入: `from rest_framework.permissions import IsAuthenticated`
  - 声明: `permission_classes = [IsAuthenticated]`

> 今天到此为止, 我重写 User 类, 实现了登录, 登出, 以及修改密码功能, 实现了品牌和种类两个视图集接口.

### 前端:处理布局问题

- 正确的前端框架页面布局应该是:

```html
<template>
  <!-- 最外层一个 container 包所有元素, 设置高度为视窗100% 设置整体背景颜色 -->
  <el-container style="height: 100vh; background-color: #???;">
    <el-menu>
      <!-- 侧边导航条...el-menu -->
    </el-menu>

    <!-- 主体 -->
    <el-container>
      <!-- 头部 -->
      <el-header></el-header>
      <!-- 内容 -->
      <el-main>
        <!-- 内容通常是一个路由出口 -->
      </el-main>
    </el-container>
  </el-container>
</template>
```

- 之前我只把侧边导航条高度设置为`100vh`, 发现当内容部分超过浏览器高度时, 导航条并未占满整体视窗高度.
- 然后增加一个内容为(`<h1>首页</h1>`)的视图`@/views/home/HomeView.vue`
- 将其路由在`@/router/index.js`中声明为`{path:'', name:'home', component: 导入的视图组件}`
- 这样访问首页至少知道在首页了

### 前端: 品牌和种类管理

> 这些代码复用性很强,值得收藏避免反复写

1. 完整的接口请求封装类: `@/api/http.js`

```js
// 导入axios和Pinia.auth
import axios from "axios";
import { useAuthStore } from "@/stores/auth";

// 定义Http类
class Http {
  // 构造函数
  constructor() {
    // 实例构造时成为一个axios实体
    this.instance = axios.create({
      // 请求基础地址位于 `~/.env` 文件中, 会根据不同的环境访问同名变量 [VITE_BASE_URL]
      baseURL: import.meta.env.VITE_BASE_URL,
      // 请求超时时间为10s
      timeout: 10000,
    });

    // 在发起任何请求前先拦截一下, 我们还得给请求做额外配置
    this.instance.interceptors.request.use((config) => {
      // 先尝试获取浏览器存储的认证令牌数据
      const authStore = useAuthStore();
      const token = authStore.token;
      // 如果令牌存在
      if (token) {
        // 给请求头配置字段 Authorization = JWT + 认证令牌
        config.headers.Authorization = "JWT" + " " + authStore.token;
      }
      return config;
    });
  }

  // http.post函数, 需要传入参数(请求路由, 表单数据)
  post = async (path, data) => {
    try {
      // 使用axios.post发起请求
      const response = await this.instance.post(path, data);
      // 成功则返回 {状态码, 新创建的数据}
      return {
        status: response.status,
        data: response.data,
      };
    } catch (error) {
      // 失败则返回 {状态码, drf.Response返回的data}
      return {
        status: error.response.status,
        data: error.response.data, // 本项目约定, 服务器端发生错误时, 返回的错误详情用 detail 表示 (data.detail)
      };
    }
  };

  // put请求, 同样需要传入参数(路由, 数据)
  // 在调用put前, 请务必拼接正确的path: (.../<pk>)
  put = async (path, data) => {
    try {
      const response = await this.instance.put(path, data);
      return {
        status: response.status,
        data: response.data,
      };
    } catch (error) {
      return {
        status: error.response.status,
        data: error.response.data,
      };
    }
  };

  // get请求, param参数可选
  get = async (path, param) => {
    try {
      // 注意param外面加上{} 将其转为对象, 这样路由地址就是 (.../?param.key=param.value&p.k=p.v&...)
      const response = await this.instance.get(path, { param });
      return {
        status: response.status,
        data: response.data,
      };
    } catch (error) {
      return {
        status: error.response.status,
        data: error.response.data,
      };
    }
  };

  // delete请求, 调用时需要配置正确的path: (.../<pk>)
  delete = async (path) => {
    try {
      const response = await this.instance.delete(path);
      return {
        status: response.status,
        data: response.data,
      };
    } catch (error) {
      return {
        status: error.response.status,
        data: error.response.data,
      };
    }
  };
}

export default Http;
```

2. 完整的品牌和种类管理请求封装`@/api/brandAndCategoryHttp.js`

```js
// 导入Http
import Http from "./http";

// 实例化http
const http = new Http();

// 定义可以操作的模型列表
const models = ["brand", "category"];

// 请求: 获得所有品牌数据
const requesetBrandData = () => {
  // 配置接口路由
  const path = `/brand/`;

  // 调取 http.get() 请求接口路由
  return http.get(path);
};

// 请求: 获得所有种类数据
const requesetCategoryData = () => {
  const path = `/category/`;

  return http.get(path);
};

// 编辑
const editData = (model, data) => {
  // 先用一个外部变量存放path
  let path = "";
  // 如果传入的model在可操作的模型列表中
  if (models.includes(model)) {
    // 拼接路由
    path = `/${model}/${data.id}/`;
    // 并请求接口
    return http.put(path, data);
  }

  // 否则禁止操作
  console.error("错误的请求!");
  return false;
};

// 删除同样的逻辑, 不过这里直接传入id即可, 不需要通过传入整行数据, 再用data.id读取
const deleteData = (model, id) => {
  let path = "";
  if (models.includes(model)) {
    path = `${model}/${id}/`;
    return http.delete(path);
  }

  console.error("错误的请求!");
  return false;
};

const createData = (model, data) => {
  let path = "";
  if (models.includes(model)) {
    path = `/${model}/`;
    return http.post(path, data);
  }

  console.error("错误的请求!");
  return false;
};

export default {
  requesetBrandData,
  requesetCategoryData,
  editData,
  deleteData,
  createData,
};
```

3. 创建视图`@/brandAndCategory/BrandAndCategoryView.vue`

```vue
<script setup>
// 导入组件
import MainBox from "@/components/MainBox.vue";
import FormDialog from "@/components/FormDialog.vue";
// 导入api请求函数封建文件
import brandAndCategoryHttp from "@/api/brandAndCategoryHttp";
// 导入响应式变量定义函数和生命周期函数
import { ref, onMounted, reactive } from "vue";
// 导入element-plus提供的组件
import { ElMessage, ElMessageBox } from "element-plus";

/**获取数据 */
// 先定义两个空的响应式数组
let brands = ref([]);
let categories = ref([]);

// 在生命周期-挂载后自动执行
onMounted(() => {
  // 请求后端接口, 分别获取品牌, 种类数据, 用 _result存储响应结果(这时 _result 是一个 Promise 对象)
  let brands_result = brandAndCategoryHttp.requesetBrandData();
  let categories_result = brandAndCategoryHttp.requesetCategoryData();
  // 如果有响应, 判断返回的状态码
  brands_result.then((result) => {
    // 如果是状态码是200, 说明响应成功
    if (result.status == 200) {
      // 将数据交给先前定义好的空数组
      brands.value = result.data;
    } else {
      // 如果状态码不是200, 说明服务器收到请求, 但服务器没有正确响应
      // console.log(result) // 可以通过打印result查看状态码和错误详情
      // 但投入使用后, 不应该给客户端暴露过多的服务器返回的信息, 万一客户端发出的请求就是恶意的,带攻击性质的呢?
      // 所以直接返回错误提示
      ElMessage.error("请求数据失败!");
    }
  });
  // Promise对象如果请求没有成功(服务器那边压根没收到), 可以用 .catch() 获取客户端这边的错误信息, 我这里没有写, 因为一般不会出现这样的问题

  // 种类同理
  categories_result.then((result) => {
    if (result.status == 200) {
      categories.value = result.data;
    } else {
      ElMessage.error("请求数据失败!");
    }
  });
});

/**品牌表单 */
// 表单5件套: let 表单开关, let 表单数据, const 表单ref, const表单验证规则,  const表单提交函数
//开关
let brandFormVisable = ref(false);
//数据
let brandFormData = reactive({
  id: 0,
  name: "",
  intro: "",
});
//ref
const brandForm = ref();
//验证规则
const brandFormRules = reactive({
  name: [
    { required: true, message: "必须填写品牌名称!", trigger: "blue" },
    { min: 2, max: 10, message: "品牌名称必须2~10个字!", trigger: "blur" },
  ],
  intro: [
    { required: true, message: "必须填写品牌简介!", trigger: "blue" },
    { min: 2, max: 100, message: "品牌简介必须2~100个字!", trigger: "blur" },
  ],
});
// 提交函数
const editBrand = () => {
  // 先用 ref.value.validate 验证表单数据是否符合表单验证规则, 回调的(valid是布尔值验证通过则为真, fields是错误字段)
  brandForm.value.validate((valid, fields) => {
    // 如果验证成功
    if (valid) {
      // 开始请求服务器
      brandAndCategoryHttp.editData("brand", brandFormData).then((result) => {
        // 如果返回的状态码是200, 说明修改成功
        if (result.status == 200) {
          // 通过修改成功后返回的数据的主键id,找到该id位于数组中的未知
          let index = brands.value.findIndex(
            (brand) => brand.id === result.data.id
          );
          // 使用 splice 函数,替换该位置为新数据
          brands.value.splice(index, 1, result.data);
          // 关闭表单
          brandFormVisable.value = false;
          // 提示修改成功
          ElMessage.success("品牌修改成功!");
        } else {
          // 如果状态码不是200, 则说明修改失败
          ElMessage.error("修改失败!");
        }
      });
    } else {
      // 如果表单前端验证没有通过, 则遍历fields, 展示错误信息
      for (let key in fields) {
        ElMessage.error(fields[key][0]["message"]);
      }
      return;
    }
  });
};

/**种类表单 */
// 同理
let categoryFormVisable = ref(false);
let categoryFormData = reactive({
  id: 0,
  name: "",
});
const categoryForm = ref();
const categoryFormRules = reactive({
  name: [
    { required: true, message: "必须填写商品种类!", trigger: "blue" },
    { min: 2, max: 10, message: "种类名称只能2~10个字!", trigger: "blur" },
  ],
});

const editCategory = () => {
  categoryForm.value.validate((valid, fields) => {
    if (valid) {
      brandAndCategoryHttp
        .editData("category", categoryFormData)
        .then((result) => {
          if (result.status == 200) {
            let index = categories.value.findIndex(
              (category) => category.id === result.data.id
            );
            categories.value.splice(index, 1, result.data);
            categoryFormVisable.value = false;
            ElMessage.success("种类修改成功!");
          } else {
            ElMessage.error("修改失败!");
          }
        });
    } else {
      for (let key in fields) {
        ElMessage.error(fields[key][0]["message"]);
      }
      return;
    }
  });
};

/**编辑表单开关 */
// 表单开关进行了简单的封装, 多一个参数form, 也就是要打开的表单名称
const openForm = (form, data) => {
  // 如果要打开brand表单
  if (form == "brand") {
    // 通过 Object.assign 匹配两个对象的共有属性, 将后者的对应值赋给前者
    Object.assign(brandFormData, data);
    // 显示表单
    brandFormVisable.value = true;
  } else if (form == "category") {
    // 如果要打开category表单...
    Object.assign(categoryFormData, data);
    categoryFormVisable.value = true;
  } else {
    // 如果没有传入正确的参数
    ElMessage.error("错误!没有找到对应行为!");
  }
};

/**删除功能 */
// 同样进行简单的封装, 删除指定模型下指定id的数据
const onDelete = (model, id) => {
  // 采用Element-plus.ElmessageBox.confirm组件实现
  // "提示内容", "提示信息"
  ElMessageBox.confirm("确认删除该条数据?", "确认删除?", {
    // 确认按键文本
    confirmButtonText: "确认",
    // 取消按键文本
    cancelButtonText: "取消",
    // 提示类型
    type: "warning",
  })
    .then(() => {
      // 如果点击确认,则会回调.then()函数
      // 调用封装好的函数接口(指定要删除的模型, 指定要删除的主键)
      brandAndCategoryHttp.deleteData(model, id).then((result) => {
        // 注意: 删除成功将返回204而不是200
        if (result.status == 204) {
          ElMessage.success("成功删除!");
          // 0.5秒后刷新窗口(给提示信息展示时间)
          setTimeout(() => {
            window.location.reload();
          }, 500);
        } else {
          // 如果不是204, 说明删除失败
          ElMessage.error("删除失败!");
        }
      });
    })
    .catch(() => {
      // 如果用户点击取消
      ElMessage.info("取消删除!");
    });
};

/**新增功能_品牌 */
// 表单老五样
let addBrandFormVisable = ref(false);
let addBrandFormData = reactive({
  name: "",
  intro: "",
});
const addBrandForm = ref();
// 这里的规则直接采用上面定义好的
const createBrand = () => {
  // 逻辑和编辑差不多
  brandAndCategoryHttp.createData("brand", addBrandFormData).then((result) => {
    if (result.status == 201) {
      // 通过 array.push() 给数组末尾添加元素
      // 也可以 .unshift 添加在最前面
      brands.value.push(result.data);
      addBrandFormVisable.value = false;
      ElMessage.success("新增品牌成功!");
    } else {
      ElMessage.error("错误!");
    }
  });
};

/**新增功能_种类 */
// 同理
let addCategoryFormVisable = ref(false);
let addCategoryFormData = reactive({
  name: "",
});
const addCategoryForm = ref();
const createCategory = () => {
  brandAndCategoryHttp
    .createData("category", addCategoryFormData)
    .then((result) => {
      if (result.status == 201) {
        categories.value.push(result.data);
        addCategoryFormVisable.value = false;
        ElMessage.success("新增种类成功!");
      } else {
        ElMessage.error("错误!");
      }
    });
};

/**新增表单开关 */
// 简单封装, 需要指定打开的表单
const openAddform = (form) => {
  if (form == "brand") {
    // 打开后清空数据
    addBrandFormData.name = "";
    addBrandFormData.intro = "";
    addBrandFormVisable.value = true;
  } else if (form == "category") {
    addCategoryFormData.name = "";
    addCategoryFormVisable.value = true;
  } else {
    ElMessage.error("错误!没有找到对应行为!");
  }
};
</script>

<template>
  <!-- 使用组件需要先导入 -->
  <MainBox title="品牌和种类管理">
    <!-- 定义一个css类,为了使用flex布局使两组 el-card 分列左右布局 -->
    <div class="main-body">
      <el-card class="body-card">
        <template #header>
          <!-- 同理, 该css类也为了两个块级元素h3(标题)和div(包裹新增按钮的容器)实现flex布局 -->
          <div class="card-header">
            <h3>品牌</h3>
            <div>
              <!-- 绑定点击事件, 打开brand新增表 -->
              <el-button type="success" @click="openAddform('brand')">
                <el-icon><Plus /></el-icon>
                <span>新增品牌</span>
              </el-button>
            </div>
          </div>
        </template>
        <!-- el-table, :data=数组,可以自动遍历数组展示诗句 -->
        <el-table :data="brands">
          <!-- el-table-column, prop="数组里面单条数据的某个属性" label="相当于设置表头thead" -->
          <el-table-column prop="name" label="名称" />
          <!-- min-width="设置最小宽度<int>" align="设置内容的位置(left, center, right)" -->
          <el-table-column
            prop="intro"
            label="简介"
            min-width="140"
            align="center"
          />
          <!-- width="设置绝对宽度" fixed="设置始终显示,如果设置fixed不指定right, 那么默认值是left" -->
          <el-table-column
            label="操作"
            width="120"
            align="center"
            fixed="right"
          >
            <!-- 当需要获取这一行的某些数据时, 可以不在 -column 上指定prop -->
            <!-- 而是使用默认插槽 -->
            <template #default="scope">
              <div class="table-btn-group">
                <div>
                  <el-tooltip content="编辑" placement="top" effect="light">
                    <!-- 通过 scope.row 就可以获取当前行的所有属性(完整的对象) -->
                    <el-button
                      type="primary"
                      @click="openForm('brand', scope.row)"
                    >
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
                <div>
                  <el-tooltip content="删除" placement="top" effect="light">
                    <!-- 还可以获取当前行数据的指定属性: scope.row.id -->
                    <el-button
                      type="danger"
                      @click="onDelete('brand', scope.row.id)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 和上面同理 -->
      <el-card class="body-card">
        <template #header>
          <div class="card-header">
            <h3>品牌</h3>
            <div>
              <el-button type="success" @click="openAddform('category')">
                <el-icon><Plus /></el-icon>
                <span>新增种类</span>
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="categories">
          <el-table-column prop="name" label="名称" />
          <el-table-column
            label="操作"
            width="120"
            align="center"
            fixed="right"
          >
            <template #default="scope">
              <div class="table-btn-group">
                <div>
                  <el-tooltip content="编辑" placement="top" effect="light">
                    <el-button
                      type="primary"
                      @click="openForm('category', scope.row)"
                    >
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
                <div>
                  <el-tooltip content="删除" placement="top" effect="light">
                    <el-button
                      type="danger"
                      @click="onDelete('category', scope.row.id)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </MainBox>

  <!-- 品牌编辑表单 -->
  <!-- 详情见组件(@/components/FormDialog.vue)v-model=表单开关属性, @submit="表单提交函数" -->
  <FormDialog
    v-model="brandFormVisable"
    title="修改品牌信息"
    @submit="editBrand"
  >
    <!-- el-form ref="表单ref" :model="表单数据" :rules="表单验证规则" -->
    <el-form ref="brandForm" :model="brandFormData" :rules="brandFormRules">
      <!-- prop="验证规则里定义的属性名称, 应与表单数据.属性对应" -->
      <el-form-item label="品牌名称" prop="name">
        <!-- v-model="表单数据.具体数据" -->
        <el-input type="text" v-model="brandFormData.name" />
      </el-form-item>
      <el-form-item label="品牌简介" prop="intro">
        <el-input type="text" v-model="brandFormData.intro" />
      </el-form-item>
    </el-form>
  </FormDialog>

  <!-- 种类编辑表单,同上 -->
  <FormDialog
    v-model="categoryFormVisable"
    title="编辑商品种类"
    @submit="editCategory"
  >
    <el-form
      ref="categoryForm"
      :model="categoryFormData"
      :rules="categoryFormRules"
    >
      <el-form-item label="种类名称" prop="name">
        <el-input type="text" v-model="categoryFormData.name" />
      </el-form-item>
    </el-form>
  </FormDialog>

  <!-- 新增品牌表单 -->
  <FormDialog
    v-model="addBrandFormVisable"
    title="新增品牌"
    @submit="createBrand"
  >
    <el-form
      ref="addBrandForm"
      :model="addBrandFormData"
      :rules="brandFormRules"
    >
      <el-form-item label="品牌名称" prop="name">
        <el-input type="text" v-model="addBrandFormData.name" />
      </el-form-item>
      <el-form-item label="品牌简介" prop="intro">
        <el-input type="text" v-model="addBrandFormData.intro" />
      </el-form-item>
    </el-form>
  </FormDialog>
  <!-- 新增种类表单 -->
  <FormDialog
    v-model="addCategoryFormVisable"
    title="新增种类"
    @submit="createCategory"
  >
    <el-form
      ref="addCategoryForm"
      :model="addCategoryFormData"
      :rules="categoryFormRules"
    >
      <el-form-item label="种类名称" prop="name">
        <el-input type="text" v-model="addCategoryFormData.name" />
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
.main-body,
.card-header,
.table-btn-group {
  /* 块级元素内部子元素同行左右对齐: flex布局实现 */
  display: flex;
  justify-content: space-between;
}
.body-card {
  /* 给两个card设置宽度和最小高度 */
  width: 49.5%;
  min-height: 888px;
}
</style>
```

4. 指定路由, 并且在框架页面绑定

```html
<!-- 首先要给侧边菜单栏指定 :router="true" 表示其具有路由导航的能力 -->
<el-menu :router="true">
  <!-- 然后告诉指定路由 :route="{name:'路由配置里写的路由名称'}" -->
  <el-menu-item index="1" class="brand" :route="{ name: 'home' }">
    <!-- ... -->
  </el-menu-item>

  <!-- 对于有下拉子菜单的路由 -->
  <el-sub-menu index="2">
    <template #title>
      <!-- 父菜单文本 -->
    </template>
    <!-- 也是在 el-menu-item 上指定 -->
    <el-menu-item index="2-1" :route="{ name: 'brandandcategory' }">
      <!-- 子菜单文本 -->
    </el-menu-item>
  </el-sub-menu>
</el-menu>
```

5. 顺带把菜单栏完善了(商品库存,订单管理等模块在侧边栏上先把导航按钮画出来), 略
