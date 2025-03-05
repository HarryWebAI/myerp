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

3. 新建`@/views/MainView.vue` (页面可复用)

```vue
<script setup>
import { ref } from "vue";
/**侧边栏 */
let isCollapse = ref(false);

const toggleAside = () => {
  isCollapse.value = !isCollapse.value;
};
</script>

<template>
  <el-container>
    <!-- 导航部分 -->
    <el-menu
      class="side-bar"
      text-color="#fff"
      active-text-color="#ffd04b"
      background-color="#1276af"
      default-active="1"
      :collapse="isCollapse"
    >
      <!-- logo -->
      <el-menu-item index="1" class="brand">
        <router-link to="/" class="brand-logo">
          <el-icon><HomeFilled /></el-icon>
          <span v-show="!isCollapse">myerp</span>
        </router-link>
      </el-menu-item>

      <!-- 菜单 -->
      <el-sub-menu index="2">
        <template #title>
          <el-icon><location /></el-icon>
          <span>导航占位1</span>
        </template>
        <el-menu-item index="2-1">1-1</el-menu-item>
        <el-menu-item index="2-2">1-2</el-menu-item>
      </el-sub-menu>
    </el-menu>

    <!-- 主体部分 -->
    <el-container>
      <!-- 页面头部 -->
      <el-header class="header">
        <div>
          <el-button @click="toggleAside" v-show="!isCollapse">
            <el-icon><Fold /></el-icon>
          </el-button>
          <el-button @click="toggleAside" v-show="isCollapse">
            <el-icon><Expand /></el-icon>
          </el-button>
        </div>

        <div>
          <p>用户信息相关</p>
        </div>
      </el-header>
      <!-- 页面主体 -->
      <el-main class="main">我是主体</el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.side-bar {
  height: 100vh;
}
.brand {
  height: 100px;
  background-color: #034855;
}
.brand-logo {
  text-decoration: none;
  font-size: 25px;
  font-weight: bold;
  color: #fff;
}
.header {
  background-color: red;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100px;
}
</style>
```

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
CORS_ALLOW_ALL_ORIGINS = False  # 默认情况下，禁用所有跨域请求
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

   - `@components/MainBox.vue`: 内容主体容器(所需参数:`title`)
   - `@components/BoxHeader.vue`: 作为 MainBox 的子组件渲染主体头部(返回按键和页面标题)
   - `@FormDialog.vue`: 表单对话框(所需参数:`v-model`=>表单开关属性 ref, `title`="对话框标题", `@submit`="绑定提交函数")
   - `@PaginationView.vue`: 分页器(所需参数:`:page_size`=>每页多少条数据, `:total`=>一共多少条数据, `v-model`=>当前页数 )

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
