# myErp

### 项目简介

- myErp 是一款个体商户门店库存管理系统, 其开发背景是着眼于**单门店**,**多品牌**,**多分类**,的**大件商品**的门店辅助经营和库存管理.(比如品牌家具加盟经销商)

### 技术栈

- myErp**前端**采用**Vue3**作为框架, **Element-Plus**作为组件库, 同时集成封装**axios**对后端服务器实现异步请求获取数据, 首页使用**echarts**图表实现数据可视化. 具体如下:
  - Vue 3.5.13 => Vue3 框架
  - pinia 3.0.1 => Vue 状态管理库
  - vue-route 4.5.0 => Vue 路由
  - element-plus 2.9.5(以及其 icon 组件) => 组件库
  - axios 1.8.1 => 异步请求库
  - echarts 5.6.0 => 可视化图表插件
  - ... => 以上包需要的其他依赖
- myErp**后端**采用**django**作为框架, **rest_framework**编写 api, **JWT**作为登录认证, 同时在首页模块使用**redis**实现访问针对频率较高的接口(首页图表)进行页面缓存, 降低服务器压力.
  - django 5.1.6 => django 框架
  - django.rest_framework 3.15.2 => django WEB API 框架
  - PyJWT 2.10.1 => Json Web Token(登录认证)
  - pandas 2.2.3 => 著名 python 文件读写包
  - redis 5.2.1 => python 与 redis 通信用的包
  - mysqlclient 2.27 => python 操作 mysql 的包
  - ... => 以上包需要的其他依赖
- myErp**数据库**采用**mysql8 社区版**

> 感谢以上软件开源!

### 目录结构

- myerp_backend/ => 后端
  - apps/ => 我们开发的模块
    - brand/ => 品牌管理模块
    - category/ => 分类管理模块
    - client/ => 客户管理模块
    - home/ => 首页模块
    - inventory/ => 库存管理模块
    - order/ => 订单管理模块
    - staff/ => 员工管理模块
  - myerp_backend/ => 主 app 模块
- myerp_frontend/ => 前端
  - src/ => 我们开发的前端页面
    -api/ => 封装请求各模块接口所用函数
    - components/ => 各页面通用组件
    - routes/ => 路由(vue-router)
    - stores/ => 状态管理(Pinia)
    - utils/ => 封装的工具函数(包括字段验证用的正则表达式, 时间戳格式转换函数)
    - views/ => 视图

### 后端模块功能简介

- brand 品牌管理模块: 实现了对品牌的基础增改查
- category 分类管理模块: 实现了对分类的基础增改查
- client 客户管理模块: 实现了对客户的增改查, 列表筛选, 客户跟进, 以及跟进日志记录
- home 首页模块: 实现了响应返回: 员工业绩数据, 年度销量趋势, 品牌库存总价三个图表数据以配合 echarts 渲染首页的可视化图表
- inventory 库存管理模块: 实现了采购发货(Purchase), 收货入库(Receive), 库存列表, 列表筛选, 收发货详情, 收发货记录修正, 以及修正日志记录
- order 订单管理模块: 实现了创建订单 ,订单列表, 列表筛选, 尾款收取, 一键出库, 订单作废, 安装人员基础的增改查功能
- staff 员工管理模块: 实现了对员工的增改查, 登录功能, 认证功能, 权限分配和访问各接口鉴权

> 不足之处 1: 简单的品牌, 分类, 甚至人员管理(包括员工管理, 安装师傅管理)都应该作为一个基础模块 **base**或者**system**最佳.

> 不足之处 2: 或者本应独立为一个模块的安装人员管理整合到了订单管理模块中, 造成了该模块的冗余和代码可维护性的降低.

> 最终的项目有点 "前后端不整齐统一" 的感觉, 比如后端的 brand 和 category, 在前端只用一个页面 `BrandAndCategoryView.vue` 就实现了, 然后又把"品牌和分类管理" 以及 "安装师傅管理" 放在了一个后端并不存在的模块, 前端的 `system` 目录中.

> 总结: 主要原因是独立开发经验尚不足, 在开发前没有做到合理有效地项目架构规划, 比如安装师傅模块管理, 是因为觉得安装师傅只涉及和订单一键出库相关功能有关联, 所以将模型, 序列化器, 视图全部写在了 order 模块中, 而品牌, 分类这些简单的模块, 只有 1~2 个字段的模型, 却又单独给他们建立了 app 模块.

### 前端视图简介

- `@/MainView`: 作为所有页面的主体框架, 他包括鉴权后动态渲染的侧边栏, 固定展示登录用户的 header(提供修改密码和退出登录功能), 固定展示版权信息的 footer, 一个重置密码的对话框表单, 以及以主体作为渲染其他视图的路由出口
- `@/LoginView`: 作为登录视图, 当路由守卫判断用户没有登录时, 会强制跳转到本页面提示用户登录
- `@/views/client`: 客户列表(列表筛选, 新增客户, 展示需跟进的客户)和客户详情(修改客户信息, 跟进客户, 展示跟进记录日志)
- `@/views/home`: 数据可视化图表展示(通过请求后端 home 模块暴露的接口, 获取员工月度业绩, 年度销量趋势, 品牌总价值三个数据以柱状图, 折线图, 饼图的形式展示)
- `@/views/inventory/`:
  - `InventoryExcel`: 库存数据备份(下载 Excel 文件), 库存盘点(上传 Excel 文件更新库存表)两个功能
  - `InventoryList`: 库存列表, 库存筛选
  - `InventoryPurchase`: 采购发货, 采购时新增从未采购过的商品 (联动更新库存列表数据)
  - `InventoryReceive`: 收货入库 (联动更新库存列表数据)
  - `PurchaseList`: 发货记录列表展示
  - `PurchaseDeteail`: 发货记录详情展示, 修正收货总成本, 修正发货数量动态更新发货成本, 发货管理日志, 修正时保证联动更新库存列表数据
  - `ReceiveList`: 收货列表展示
  - `ReceiveDetail`: 收货记录详情展示, 修正收货数量, 收货管理日志, 修正时修正时保证联动更新库存列表数据
- `@/views/order/`:
  - `CreateOrder`: 实现新增订单, 新增订单时新增首次到店即成交的客户, 新增订单时新增从未销售过的商品, 根据订单总额, 首付定金, 动态计算待收尾款, 根据客户订购商品, 动态计算出算毛利 (联动更新库存列表数据)
  - `OrderList`: 订单列表展示, 列表筛选, 尾款收取功能
  - `OrderDetail`: 一键出库, 订单作废功能, 订单操作跟踪日志
- `@/views/system`: 系统基础管理:
  - `BrandAndCategoryView`: 品牌和分类管理, 包括列表展示, 新增, 修改
  - `InstallerView`: 安装师傅管理, 同上
  - `StaffView`: 员工管理, 员工编辑(身份授权)

### 基础功能实现思路

###### 登录认证

- 前端采用路由守卫, 未登录用户仅可访问 `LoginView`
- 后端采用 JWT 认证, 未登录用户仅可访问 `login/` 路由, 即 `staff/views/LoginView` 视图接口
- 前端通信后端时, 通过 `staff/authentications` 判断用户是否登录(请求头是否带 JWT 令牌), 在后端配置文件 `settings` 中指定

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['apps.staff.authentications.JWTAuthentication']
}
```

###### 权限鉴定

- 前端通过员工模型(重写 django.user 模型)中的`is_boss`(老板), `is_storekeeper`(库管), `is_manager`(经理) 三个字段属性判断员工的身份(在`@/store/auth.js`中实现判断, 在`@/router/index.js`中实现对页面添加访问权限, 并动态渲染`MainView`的侧边栏)
- 后端部分, 编写 `staff/permissions` 实现员工身份判断, 在视图接口中声明 `permission_class=[...]` 对接口进行保护

###### 发货功能

1. 锚定品牌获取该品牌下的所有商品
2. 选择现有库存商品或者新增商品
3. 填写好后请求发货接口 `inventory.PurchaseView`:

- 传入品牌, 总成本, 发货详情
- 开启数据库事务
  1. 新建发货单,
  2. 遍历发货详情, 找到每条详情记录对应的库存商品, 更新他们的`on_road`在途字段数量, 这里需要用**悲观锁**`select_for_update()`找到对应库存信息, 防止多条发货请求同一时间修改同一条库存数据, 导致库存数据不准确
  3. 用一个空列表存储明细, 最后用`PurchaseDetail.objects.bulk_create()`批量创建详情数据
  4. 写入针对本采购单的采购日志

###### 收货功能

1. 锚定品牌, 获取该品牌下所有在途商品, 在**前端**筛选出在途数量>0 的在途商品
2. 勾选收货商品
3. 确认后请求收货接口 `inventory.ReceiveView`:

- 同上, 创建收货单, 遍历收货详情, 减少`on_road`, 增加同数量的`in_stock` 在库, 批量创建收货详情, 创建本收货单的收货日志

###### 发货修正

- 修正某一条发货详情的数量, 会修改 `1发货详情`, `2所属库存在途数量`, `3发货单成本`, 创建 `4发货单日志`
- 也可以直接修改发货单的发货成本(单独接口)

###### 收货修正

- 修正某一条收货详情的数量, 会修改 `1所属库存在库数量`, `2所属库存在途数量`, 创建 `3收货单日志`

###### 下载(备份)和上传(盘点和系统初次投入使用时)库存数据

- 都采用`pandas`针对指定格式的 Excel 表格进行读写

> 为确保数据准确, 使用此功能需要用户将系统里的订单先全部确保送货交付到客户(订单全部出库), 再从开始盘点起暂停一切系统操作(包括发货,收货,新增订单)直到盘点结束(上传最后现实里准确的盘点结果汇总的 Excel 表). 使用时, 必须通过其他方式记录: 1, 当前采购发货但还没到库的记录, 2, 这一期间的所有订单. 因为盘点只针对`in_stock`这一字段进行盘点, 当盘点结束后, 用户再将盘点期间的这些记录写入系统中, 才会使系统的库存准确无误.

> 这一功能在前端通过醒目的提示告知了用户. 因为通常大件商品的经销商以季度甚至年度进行库存盘点, 作为个体商户, 盘点的工作量也不大, 最多一天时间就可以盘清所有库存, 所以在淡季或者过年前后进行盘点最为合理, 这一期间依常理来说不会发货, 也不会有客户生成新订单

###### 新增订单

- 新增一个订单, 会新增 `1一条订单数据`, 同时根据订单详情, 会修改 `2所属库存的被订购数量`, 会创建 `3订单所属日志`

###### 订单一键出库

- 出库一个订单, 会修改 `1订单的送货状态`, 同时根据订单详情, 会修改 `2所属库存的被订购数量减少(解锁)`, `3所属库存的库存数量减少(从库房出库)`, 商品被销售数量增加(统一畅销品)

###### 订单作废

- 作废一个订单, 会修改 `1订单的送货状态`和`2订单的结清状态`, 同时根据订单详情, 会修改 `2所属库存的被订购数量减少(解锁)`, `3所属库存的库存数量减少(从库房出库)`

###### 尾款收取

- 尾款首次计算通过订单模型的`订单总额`-`首付定金`形成, 当客户签单时, `首付定金=订单总额`, 说明客户一次性结清, 订单的结清状态应直接为`已结清`, 尾款为`0`
- 若客户有尾款, 我们通过订单所属订单收取表的`本次付款`字段累加求和计算出客户已付的尾款.

###### 列表筛选

- 无论是客户筛选, 库存筛选, 还是订单筛选, 都通过重写类视图的`get_queryset()`函数实现, 通过判断接口的 url 参数`.../?key=value&key=value&...`来进行列表数据的筛选过滤

###### 列表重写

- 库存列表需要重写, 因为我们还要给前端返回库存总价(而后端分页后想在前端实现累加的逻辑不对)
- 订单列表需要重写, 因为我们默认排除`已作废`的订单, 除非用户特意筛选`已作废`订单, 否则`全部订单`其实是不包含`已作废`的订单的
- 客户列表需要重写, 因为我们默认排除`已成交`和`已流失`的客户, 除非客户特意筛选`已成交`和`已流失`的客户, `全部客户`同样不包含`已成交`和`已流失`的客户

###### 其他细节

- 在任何提交和修改数据的接口, 我们都会在前端进行字段上合法性的判断, 后端用序列化器实行字段合法性的判断, 某些接口被请求前, 前端会针对的业务逻辑进行显性判断: 比如收货时不能超收(禁止在途 1 个收 2 个入库), 同时后端即使通过了序列化器的判断, 也会再视图层中通过业务逻辑进行再度审核, 确保系统的稳健和数据的安全

### 值得收藏复用的代码

###### 前端部分

1. 工具库 - 时间戳格式化

```js
/**
 * @param: 时间戳
 * @return: yyyy-mm-dd
 */
const stringFromDate = (date) => {
  if (typeof date === "string") {
    date = new Date(date);
  }
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");
  const formattedDate = `${year}-${month}-${day}`;
  return formattedDate;
};

/**
 * @param: 时间戳
 * @return: yyyy-mm-dd hh:mm:ss
 */
const stringFromDateTime = (date) => {
  if (typeof date === "string") {
    date = new Date(date);
  }
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");
  const hour = date.getHours().toString().padStart(2, "0");
  const minute = date.getMinutes().toString().padStart(2, "0");
  const second = date.getSeconds().toString().padStart(2, "0");
  const formattedDate = `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  return formattedDate;
};

export default {
  stringFromDate: stringFromDate,
  stringFromDateTime,
};
```

2. 工具库 - 正则表达式

```js
// 手机号码正则表达式
const telphoneRegExp = /^1[3-9]\d{9}$/;

// 电子邮箱正则表达式
const emailRegExp =
  /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

// 订单编号正则表达式
const orderIdRegExp = /^[A-Za-z0-9]{6,20}$/;

// 中文姓名正则表达式 (增强版-支持生僻字和少数民族姓名)
const chineseNameRegExp = /^[\u3400-\u9fa5·•]{2,15}$/;

// 身份证号码正则表达式
const idCardRegExp =
  /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;

// 银行卡号正则表达式
const bankCardRegExp = /^[1-9]\d{15,18}$/;

export {
  telphoneRegExp,
  idCardRegExp,
  bankCardRegExp,
  emailRegExp,
  orderIdRegExp,
  chineseNameRegExp,
};
```

3. 封装 axios

```js
// : npm install axios --save
import axios from "axios";
// 引用 Pinia 的用户状态管理
import { useAuthStore } from "@/stores/auth";

/**
 * 封装 Http 类
 */
class Http {
  // 构造函数: 实例化 axios 类
  constructor() {
    this.instance = axios.create({
      // 配置基础请求地址(url前面的部分)
      baseURL: import.meta.env.VITE_BASE_URL,
      // 设置超时时间
      timeout: 10000,
    });

    // 请求前的拦截器: 用于通配全部请求的请求头
    this.instance.interceptors.request.use((config) => {
      // 获取当前用户
      const authStore = useAuthStore();
      // 获取当前 jwt 令牌
      const token = authStore.token;
      if (token) {
        // 配置请求头, 任何请求都带上认证令牌
        config.headers.Authorization = "JWT" + " " + authStore.token;
      }
      return config;
    });
  }

  // 以下所有函数的返回值都是一个 Promise 对象
  // post请求
  post = async (path, data) => {
    try {
      const response = await this.instance.post(path, data);
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

  // put请求
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

  // get请求
  get = async (path, params) => {
    try {
      const response = await this.instance.get(path, { params });
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

  // delete请求
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

  // download请求(其实是大文件的post请求)
  download = async (path) => {
    try {
      const response = await this.instance.get(path, { responseType: "blob" });
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

/**
 * 在使用时, 需要先引用本文件后, 再
 * const http = new Http()
 * http.method(params...)
 */
```

4. Pinia 实现的用户状态管理

```js
// 引入计算属性
import { computed } from "vue";
// 引入pinia定义函数
import { defineStore } from "pinia";

// 配置存入浏览器本地存储的键名, 可根据项目自定义
const USER_KEY = "JWT_TOKEN_FROM_MYERP_USER_INFO";
const TOKEN_KEY = "JWT_TOKEN_FROM_MYERP_TOKEN";

// 开始构建Pinia数据
export const useAuthStore = defineStore("auth", () => {
  // 登录成功时调用, 写入数据到浏览器本地存储
  const setToken = (data) => {
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    localStorage.setItem(TOKEN_KEY, data.token);
  };

  // 退出登录时调用, 通过键名清理浏览器本地存储的数据
  const clearToken = () => {
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(TOKEN_KEY);
  };

  // 获取当前登录用户
  let user = computed(() => {
    return localStorage.getItem(USER_KEY)
      ? JSON.parse(localStorage.getItem(USER_KEY))
      : false;
  });

  // 获取当前登录用户的JWT令牌
  let token = computed(() => {
    return localStorage.getItem(TOKEN_KEY)
      ? localStorage.getItem(TOKEN_KEY)
      : false;
  });

  // 判断当前用户是否处于登录状态
  let isLogined = computed(() => {
    if (localStorage.getItem(USER_KEY) && localStorage.getItem(TOKEN_KEY)) {
      return true;
    }

    return false;
  });

  return {
    setToken,
    clearToken,
    user,
    token,
    isLogined,
  };
});

/**
 * 在使用时候, 需要先引用本文件后, 再
 * const authStore = new useAuthStore()
 * 通过 authStore.计算属性 获取需要的信息
 */
```

5. 其他的通用组件, 位于 `@/components/`

###### 后端部分
1. 登录认证
```python
########## models.py ##########
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
    telephone = models.CharField(max_length=11)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_boss = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_storekeeper = models.BooleanField(default=False)

    objects = ERPUserManager()

    # 设置登录账号用哪个字段?
    USERNAME_FIELD = "account"
    # 创建用户时必须填写哪些字段?
    REQUIRED_FIELDS = ['name', 'telephone', 'password']


########## authentications.py #########
import time
# pip install PyJWT
import jwt
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from .models import ERPUser

# 生成 JWT 令牌
def generate_jwt(user):
    # 设置过期时间
    expire_time = time.time() + 60 * 60 * 24 * 7
    # 返回加密的 jwt 令牌
    return jwt.encode({"userid": user.pk, "exp": expire_time}, key=settings.SECRET_KEY)


class UserTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return request._request.user, request._request.auth

# jwt 认证, 通过 settings.rest_framework 指定该类作为登录认证类
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
                user = ERPUser.objects.get(pk=userid)
                setattr(request, 'user', user)
                return user, jwt_token
            except:
                msg = '用户不存在!'
                raise exceptions.AuthenticationFailed(msg)
        except ExpiredSignatureError:
            msg = "JWT Token已过期!"
            raise exceptions.AuthenticationFailed(msg)


########## serializers.py ##########
class LoginSerializer(serializers.Serializer):
    """
    登录序列化
    """
    # 声明要传入的数据
    account = serializers.CharField(required=True)
    password = serializers.CharField(required=True, max_length=30, min_length=6)

    # 校验传入的数据
    def validate(self, attrs):
        account = attrs.get('account')
        password = attrs.get('password')

        if account and password:
            # 尝试找到用户(本项目通过 account 字段作为"登录账号")
            user = ERPUser.objects.filter(account=account).first()

            # 找不到用户
            if not user:
                raise serializers.ValidationError('请输入正确的账号!')
            # 找得到用户但密码不对
            if not user.check_password(password):
                raise serializers.ValidationError('请输入正确的密码!')

            # 找得到用户但状态属于未激活
            if user.is_active == False:
                raise serializers.ValidationError('用户被锁定!如有疑问请联系管理员!')

        else:
            # 没有输入账号或者密码
            raise serializers.ValidationError('请输入账号密码!')

        # 节约服务器资源的小技巧, 绑定到序列化器的'user'属性上, 防止在视图层再度获取
        attrs['user'] = user

        return attrs

########## views.py ##########
class LoginView(APIView):
    """
    登录接口
    """
    def post(self, request):
        # 调用序列化器验证字段是否合规, 用户是否存在, 用户名密码是否正确
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            # 验证成功
            user = serializer.validated_data.get('user')
            # 更新最近登录时间
            user.last_login = datetime.now()
            user.save()

            # 生成jwt
            token = generate_jwt(user)
            # 返回给前端, 作为 authStore.setToken() 的参数, 在用户登录成功后调用
            return Response({'token': token, 'user': serializers.StaffSerializer(user).data})

        else:

            detail = list(serializer.errors.values())[0][0]
            return Response(data={'detail': detail}, status=status.HTTP_401_UNAUTHORIZED)
```
2. 上传下载
```python
# pip install pandas
# pip install pandas openpyxl (pandas依赖openpyxl)
import pandas as pd
# 添加os模块用于文件扩展名验证
import os 
# 添加文件上传解析器
from rest_framework.parsers import MultiPartParser  

class InventoryDownloadView(APIView):
    """
    库存数据下载接口
    """
    permission_classes = [IsAuthenticated,IsBoss]
    def get(self, request):
        # 获取所有库存数据
        queryset = models.Inventory.objects.order_by('-brand__id', '-category__id', '-id').all()
        results = queryset.values('id', 'name', 'brand__name', 'category__name', 'size', 'color', 'cost', 'on_road', 'in_stock', 'been_order', 'sold')

        try: 
            # 如果没有数据，创建一个空的DataFrame但包含所有列
            if not results:
                inventory_df = pd.DataFrame(columns=[
                    'id', 'name', 'brand__name', 'category__name', 'size', 
                    'color', 'cost', 'on_road', 'in_stock', 'been_order', 'sold'
                ])
            else:
                inventory_df = pd.DataFrame(results)

            inventory_df = inventory_df.rename(columns={
                'name': '名称',
                'brand__name': '品牌',
                'category__name': '分类',
                'size': '规格',
                'color': '颜色',
                'cost': '成本',
                'on_road': '物流在途',
                'in_stock': '当前在库',
                'been_order': '已被订购',
                'sold': '已售出'
            })
            
            # 获取日期 yyyy-mm-dd
            date = datetime.now().strftime('%Y-%m-%d')
            response = HttpResponse(content_type='application/xlsx')
            response['Content-Disposition'] = f"attachment; filename=库存列表_{date}.xlsx"
            with pd.ExcelWriter(response) as writer:
                inventory_df.to_excel(writer, sheet_name='库存信息', index=False)
            
            return response
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InventoryUploadView(APIView):
    """
    库存数据上传接口
    """
    permission_classes = [IsAuthenticated,IsBoss]
    parser_classes = [MultiPartParser]  # 添加文件上传解析器
    
    def post(self, request):
        try:
            # 验证当前系统中是否存在未出库的订单
            from apps.order.models import Order
            undelivered_orders = Order.objects.filter(delivery_status=1)  # 1表示新订单
            if undelivered_orders.exists():
                return Response({
                    'detail': '系统中存在未出库的订单，请先完成所有订单出库操作再进行库存盘点',
                    'order_count': undelivered_orders.count(),
                    'order_numbers': list(undelivered_orders.values_list('order_number', flat=True))
                }, status=status.HTTP_400_BAD_REQUEST)

            # 1. 验证文件是否存在
            if 'file' not in request.FILES:
                return Response({'detail': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            
            # 2. 验证文件格式
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension not in ['.xlsx', '.xls']:
                return Response({'detail': '只支持.xlsx或.xls格式的文件'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. 读取Excel文件
            df = pd.read_excel(file)
            
            # 4. 验证必要的列是否存在
            required_columns = ['名称', '品牌', '分类', '规格', '颜色', '成本']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'detail': f'缺少必要的列: {", ".join(missing_columns)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 5. 创建空列表用于存储要创建的库存对象
            inventory_objects = []
            
            # 获取所有品牌和分类的集合，用于验证
            existing_brands = set(models.Brand.objects.values_list('name', flat=True))
            existing_categories = set(models.Category.objects.values_list('name', flat=True))
            
            # 获取Excel中的所有品牌和分类
            excel_brands = set(df['品牌'].astype(str).unique())
            excel_categories = set(df['分类'].astype(str).unique())
            
            # 检查是否有不存在的品牌
            invalid_brands = excel_brands - existing_brands
            if invalid_brands:
                return Response({
                    'detail': f'发现未经授权的品牌: {", ".join(invalid_brands)}，请先在系统中创建这些品牌。'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查是否有不存在的分类
            invalid_categories = excel_categories - existing_categories
            if invalid_categories:
                return Response({
                    'detail': f'发现未经授权的分类: {", ".join(invalid_categories)}，请先在系统中创建这些分类。'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 预先获取所有需要用到的品牌和分类对象
            brands_dict = {brand.name: brand for brand in models.Brand.objects.filter(name__in=excel_brands)}
            categories_dict = {category.name: category for category in models.Category.objects.filter(name__in=excel_categories)}
            
            # 6. 开启事务处理
            with transaction.atomic():
                # 首先清空所有库存记录
                models.Inventory.objects.all().delete()
                
                # 遍历Excel的每一行
                for index, row in df.iterrows():
                    # 从预加载的字典中获取品牌和分类对象
                    brand = brands_dict[str(row['品牌'])]
                    category = categories_dict[str(row['分类'])]
                    
                    # 确保数值字段为正确的类型，处理空值和NaN
                    try:
                        # 处理成本字段
                        cost = row['成本']
                        if pd.isna(cost) or cost == '':
                            return Response({
                                'detail': f'第{index + 1}行成本不能为空'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        cost = float(cost)
                        
                        # 处理其他数值字段，空值或NaN都转为0
                        def safe_convert_to_int(value):
                            if pd.isna(value) or value == '':
                                return 0
                            return int(float(value))
                        
                        # 只统计in_stock库存数量，其他数量都设为0
                        in_stock = safe_convert_to_int(row.get('当前在库', 0))
                        
                        # 验证数值是否为负数
                        if cost < 0 or in_stock < 0:
                            return Response({
                                'detail': f'第{index + 1}行存在负数，所有数值必须大于等于0'
                            }, status=status.HTTP_400_BAD_REQUEST)
                            
                    except (ValueError, TypeError) as e:
                        return Response({
                            'detail': f'第{index + 1}行数据格式错误：{str(e)}，请确保数值字段格式正确'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # 创建库存对象（但不保存到数据库）
                    inventory = models.Inventory(
                        name=str(row['名称']).upper(),  # 将名称中的英文字母转为大写
                        brand=brand,
                        category=category,
                        size=str(row['规格']),
                        color=str(row['颜色']),
                        cost=cost,
                        on_road=0,  # 物流在途设为0
                        in_stock=in_stock,  # 只保留当前在库数量
                        been_order=0,  # 已被订购设为0
                        sold=0  # 已售出设为0
                    )
                    inventory_objects.append(inventory)
                
                # 7. 批量创建库存记录
                models.Inventory.objects.bulk_create(inventory_objects)

                # 8. 创建库存日志
                log_content = f"{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}进行了库存盘点\n"
                log_content += f"成功导入{len(inventory_objects)}条库存记录"
                models.InventoryLog.objects.create(
                    content=log_content,
                    operator=request.user
                )

                # 获取当前时间作为盘点时间点
                current_time = datetime.now()
                inventory_check_message = f"{current_time.strftime('%Y-%m-%d %H:%M:%S')}进行了库存盘点，此次盘点之前的所有数据已失效!"
                
                # 为所有采购记录添加盘点日志
                purchases = models.Purchase.objects.filter(create_time__lt=current_time)
                for purchase in purchases:
                    models.PurchaseLog.objects.create(
                        purchase=purchase,
                        content=inventory_check_message,
                        operator=request.user
                    )
                
                # 为所有收货记录添加盘点日志
                receives = models.Receive.objects.filter(create_time__lt=current_time)
                for receive in receives:
                    models.ReceiveLog.objects.create(
                        receive=receive,
                        content=inventory_check_message,
                        operator=request.user
                    )
                
                # 为订单添加操作日志
                from apps.order.models import Order
                orders = Order.objects.filter(sign_time__lt=current_time)
                for order in orders:
                    OperationLog.objects.create(
                        order=order,
                        description=inventory_check_message,
                        operator=request.user
                    )
                
            return Response({
                'detail': f'成功导入{len(inventory_objects)}条库存记录，所有库存仅保留当前在库数量，其他数量已重置为0',
                'count': len(inventory_objects)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'detail': f'导入失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
```