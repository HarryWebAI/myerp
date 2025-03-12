<script setup>
import MainBox from '@/components/MainBox.vue';
import FormDialog from '@/components/FormDialog.vue';
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import orderHttp from '@/api/orderHttp';
import clientHttp from '@/api/clientHttp';
import staffHttp from '@/api/staffHttp';
import brandAndCategoryHttp from '@/api/brandAndCategoryHttp';
import inventoryHttp from '@/api/inventoryHttp';

const router = useRouter();

// 表单数据
const orderForm = reactive({
  order_number: '',
  client_id: '',
  staff_id: '',
  brand_id: 0,
  total_amount: 0,
  down_payment: 0,
  pending_balance: 0,
  total_cost: 0,
  gross_profit: 0,
  address: '',
  details: []
});

// 表单验证规则
const orderFormRules = reactive({
  order_number: [
    { required: true, message: '订单编号不能为空', trigger: 'blur' },
    { min: 2, max: 30, message: '订单编号长度在2到30个字符之间', trigger: 'blur' }
  ],
  client_id: [
    { required: true, message: '请选择客户', trigger: 'change' }
  ],
  staff_id: [
    { required: true, message: '请选择签单人员', trigger: 'change' }
  ],
  brand_id: [
    { required: true, message: '请选择品牌', trigger: 'change' }
  ],
  total_amount: [
    { required: true, message: '订单总额不能为空', trigger: 'blur' },
    { type: 'number', min: 0, message: '订单总额必须大于等于0', trigger: 'blur' }
  ],
  down_payment: [
    { required: true, message: '首付定金不能为空', trigger: 'blur' },
    { type: 'number', min: 0, message: '首付定金必须大于等于0', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '安装地址不能为空', trigger: 'blur' },
    { max: 200, message: '安装地址不能超过200个字符', trigger: 'blur' }
  ]
});

// 获取数据
const clients = ref([]);
const staffs = ref([]);
const brands = ref([]);
const inventories = ref([]);
const categories = ref([]);

// 加载所有数据
onMounted(() => {
// 获取所有客户
  clientHttp.getAllClients().then(result => {
    if (result.status === 200) {
      console.log(result.data)
      clients.value = result.data;
    } else {
      ElMessage.error('获取客户数据失败！');
    }
  });

// 获取所有员工
  staffHttp.getStaffList().then(result => {
    if (result.status === 200) {
      staffs.value = result.data;
    } else {
      ElMessage.error('获取员工数据失败！');
    }
  });

  // 获取所有品牌
  brandAndCategoryHttp.requesetBrandData().then(result => {
    if (result.status === 200) {
      brands.value = result.data;
    } else {
      ElMessage.error('获取品牌数据失败！');
    }
  });

  // 获取所有商品分类
  brandAndCategoryHttp.requesetCategoryData().then(result => {
    if (result.status === 200) {
      categories.value = result.data;
    } else {
      ElMessage.error('获取商品分类失败！');
    }
  });
});

// 加载品牌相关商品
const loadInventories = () => {
  if (!orderForm.brand_id) {
    ElMessage.warning('请先选择品牌');
    return;
  }

  inventoryHttp.requestAllInventoryData(orderForm.brand_id).then(result => {
    if (result.status === 200) {
      inventories.value = result.data;
      ElMessage.success('商品数据加载成功！');
    } else {
      ElMessage.error('获取商品数据失败！');
    }
  });
};

// 添加订单详情行
const addOrderDetail = () => {
  orderForm.details.push({
    inventory_id: 0,
    quantity: 1
  });
};

// 删除订单详情行
const deleteOrderDetail = (index) => {
  orderForm.details.splice(index, 1);
  calculateTotals();
};

// 选中商品时的处理（防止重复选择同一商品）
const selectedInventoryMap = ref(new Map());

// 获取已选商品ID集合
const getSelectedIds = () => {
  const ids = new Set();
  for (const id of selectedInventoryMap.value.values()) {
    if (id !== 0) {
      ids.add(id);
    }
  }
  return ids;
};

// 商品选择事件处理
const handleSelectChange = (row, rowIndex, value) => {
  selectedInventoryMap.value.set(rowIndex, value);
  calculateTotals();
};

// 生成禁用状态
const getDisabledStatus = (inventoryId, rowIndex) => {
  if (selectedInventoryMap.value.get(rowIndex) === inventoryId) {
    return false;
  }
  const selectedIds = getSelectedIds();
  return selectedIds.has(inventoryId);
};

// 计算所有总额
const calculateTotals = () => {
  // 计算成本总价
  let autoCalculatedCost = 0;
  for (const detail of orderForm.details) {
    if (detail.inventory_id && detail.quantity) {
      const inventory = inventories.value.find(inv => inv.id === detail.inventory_id);
      if (inventory) {
        autoCalculatedCost += inventory.cost * detail.quantity;
      }
    }
  }

  // 只有在用户尚未手动修改成本总价的情况下才自动设置
  if (!userModifiedCost.value) {
    orderForm.total_cost = autoCalculatedCost;
  }

  // 计算待收尾款 = 订单总额 - 首付定金
  orderForm.pending_balance = orderForm.total_amount - orderForm.down_payment;

  // 计算毛利润 = 订单总额 - 成本总价
  orderForm.gross_profit = orderForm.total_amount - orderForm.total_cost;
};

// 用户是否手动修改过成本总价的标志
const userModifiedCost = ref(false);

// 手动修改成本总价时的处理
const handleCostChange = () => {
  userModifiedCost.value = true;

  // 重新计算毛利润
  orderForm.gross_profit = orderForm.total_amount - orderForm.total_cost;
};

// 确认订单表单
const confirmDialogVisible = ref(false);
const orderFormRef = ref(null);

// 提交前的验证
const validateOrder = () => {
  if (!orderForm.order_number) {
    ElMessage.error('请输入订单编号！');
    return false;
  }

  if (!orderForm.client_id) {
    ElMessage.error('请选择客户！');
    return false;
  }

  if (!orderForm.staff_id) {
    ElMessage.error('请选择签单人员！');
    return false;
  }

  if (!orderForm.brand_id) {
    ElMessage.error('请选择品牌！');
    return false;
  }

  if (orderForm.total_amount <= 0) {
    ElMessage.error('订单总额必须大于0！');
    return false;
  }

  if (orderForm.down_payment < 0) {
    ElMessage.error('首付定金不能为负数！');
    return false;
  }

  if (orderForm.details.length === 0) {
    ElMessage.error('请添加订单详情！');
    return false;
  }

  // 检查订单详情
  const inventoryIds = new Set();
  const duplicateItems = [];

  for (const detail of orderForm.details) {
    if (!detail.inventory_id) {
      ElMessage.error('请选择商品！');
      return false;
    }

    if (detail.quantity <= 0) {
      ElMessage.error('商品数量必须大于0！');
      return false;
    }

    // 检查重复商品
    if (inventoryIds.has(detail.inventory_id)) {
      const itemName = inventories.value.find(inv => inv.id === detail.inventory_id)?.full_name || '未知商品';
      duplicateItems.push(itemName);
    } else {
      inventoryIds.add(detail.inventory_id);
    }
  }

  if (duplicateItems.length > 0) {
    ElMessage.error(`禁止重复添加商品：${duplicateItems.join('、')}`);
    return false;
  }

  return true;
};

// 提交订单前预览
const previewOrder = () => {
  if (!validateOrder()) {
    return;
  }

  calculateTotals();
  confirmDialogVisible.value = true;
};

// 预览详情数据
const orderPreviewDetails = computed(() => {
  return orderForm.details.map(detail => {
    const inventory = inventories.value.find(inv => inv.id === detail.inventory_id);
    if (inventory) {
      return {
        ...inventory,
        quantity: detail.quantity,
        subtotal: inventory.cost * detail.quantity
      };
    }
    return null;
  }).filter(item => item !== null);
});

// 提交订单
const submitOrder = () => {
  // 验证所有订购的商品品牌与当前锚定的品牌一致
  const mismatchedItems = [];

  // 检查每个订单详情项
  for (const detail of orderForm.details) {
    const inventory = inventories.value.find(inv => inv.id === detail.inventory_id);

    // 如果找到商品但品牌不匹配，记录下来
    if (inventory && Number(inventory.brand.id) !== Number(orderForm.brand_id)) {
      mismatchedItems.push({
        name: inventory.full_name || '未知商品',
        actual_brand: brands.value.find(b => b.id === inventory.brand_id)?.name || '未知品牌',
        expected_brand: brands.value.find(b => b.id === orderForm.brand_id)?.name || '未知品牌'
      });
    }
  }

  // 验证代收尾款不能为负数
  if (orderForm.pending_balance < 0) {
    ElMessage.error('请检查订单总额与首付定金是否正确！待收尾款不能为负数！ ');
    return;
  }

  // 如果有不匹配的商品，显示详细错误信息并中止提交
  if (mismatchedItems.length > 0) {
    const errorMessage = mismatchedItems.map(item =>
      `${item.name}(${item.actual_brand}) 与签单品牌(${item.expected_brand})不一致`
    ).join('\n');

    ElMessage({
      message: `订单中存在品牌不一致的商品:\n${errorMessage}`,
      type: 'error',
      duration: 5000,
      showClose: true
    });
    return;
  }

  // 准备提交数据
  const orderData = {
    order_number: orderForm.order_number,
    brand_id: orderForm.brand_id,
    client_id: orderForm.client_id,
    staff_id: orderForm.staff_id,
    total_amount: orderForm.total_amount,
    down_payment: orderForm.down_payment,
    total_cost: orderForm.total_cost,
    gross_profit: orderForm.gross_profit,
    address: orderForm.address,
    remark: orderForm.remark,
    details: orderForm.details
  };

  orderHttp.createOrder(orderData).then(result => {
    if (result.status === 201) {
      ElMessage.success('订单创建成功！');
      // 跳转至订单列表页面
      router.push({ name: 'order_list' });
    } else {
      // 检查是否有详细错误信息
      if (result.data && result.data.detail) {
        // 检查是否是重复订单号错误
        if (result.data.detail.includes('Duplicate entry') && result.data.detail.includes('order_number')) {
          ElMessage.error('订单创建失败！订单编号已存在，请使用不同的订单编号。');
        } else {
          // 显示服务器返回的具体错误
          ElMessage.error(`订单创建失败！${result.data.detail}`);
        }
      } else {
        ElMessage.error('订单创建失败！');
      }
    }
  }).catch(error => {
    console.error('订单创建错误:', error);
    // 检查响应中是否包含详细错误信息
    if (error.response && error.response.data && error.response.data.detail) {
      const errorDetail = error.response.data.detail;
      // 检查是否是重复订单号错误
      if (errorDetail.includes('Duplicate entry') && errorDetail.includes('order_number')) {
        ElMessage.error('订单创建失败！订单编号已存在，请使用不同的订单编号。');
      } else {
        // 显示服务器返回的具体错误
        ElMessage.error(`订单创建失败！${errorDetail}`);
      }
    } else {
      ElMessage.error('订单创建发生错误！请检查网络连接或联系管理员。');
    }
  });
};

// 数量变化时重新计算
const handleQuantityChange = () => {
  calculateTotals();
};

// 金额变化时重新计算
const handleAmountChange = () => {
  calculateTotals();
};

// 新增商品相关功能
const createInventoryFormVisible = ref(false);
const createInventoryFormData = reactive({
  name: '',
  brand_id: 0,
  category_id: 0,
  size: '原版',
  color: '原色',
  cost: 0
});
const createInventoryForm = ref();

// 打开新增商品表单
const openCreateInventoryForm = (rowIndex) => {
  // 记录当前行索引，用于后续添加商品后更新
  currentEditingRowIndex.value = rowIndex;

  // 设置品牌为当前选择的品牌
  createInventoryFormData.brand_id = orderForm.brand_id;
  createInventoryFormData.category_id = 0;
  createInventoryFormData.name = '';
  createInventoryFormData.size = '原版';
  createInventoryFormData.color = '原色';
  createInventoryFormData.cost = 0;

  createInventoryFormVisible.value = true;
};

// 记录当前正在编辑的行索引
const currentEditingRowIndex = ref(-1);

// 新增商品表单验证规则
const inventoryFormRules = reactive({
  name: [
    { required: true, message: '必须填写商品名称', trigger: 'blur' },
    { min: 2, max: 30, message: '商品名称必须在2~30个字之间', trigger: 'blur' }
  ],
  brand_id: [{ required: true, message: '必须选择所属品牌', trigger: 'change' }],
  category_id: [{ required: true, message: '必须选择商品分类', trigger: 'change' }],
  size: [{ min: 2, max: 15, message: '规格必须在2~15个字之间', trigger: 'blur' }],
  color: [{ min: 2, max: 15, message: '颜色必须在2~15个字之间', trigger: 'blur' }],
  cost: [
    { required: true, message: '必须填写单个进价', trigger: 'blur' },
    { type: 'number', message: '进价必须为数值', trigger: ['blur', 'change'] },
    { pattern: /^\d+(\.\d{1,2})?$/, message: '进价最多保留两位小数', trigger: 'blur' }
  ]
});

// 创建新商品
const createInventory = () => {
  if (createInventoryFormData.brand_id < 1) {
    ElMessage.error('必须选择所属品牌！');
    return;
  }

  if (createInventoryFormData.category_id < 1) {
    ElMessage.error('必须选择商品分类！');
    return;
  }

  if (createInventoryFormData.cost < 0) {
    ElMessage.error('进价不可以为负数！');
    return;
  }

  createInventoryForm.value.validate((valid, fields) => {
    if (valid) {
      // 转换商品名称为大写
      createInventoryFormData.name = createInventoryFormData.name.toUpperCase();

      // 提交创建请求
      inventoryHttp.createInventoryData(createInventoryFormData).then(result => {
        if (result.status === 201) {
          // 将新商品添加到商品列表
          inventories.value.unshift(result.data);
          ElMessage.success('创建商品成功！');

          // 如果有指定行，则设置该行选中新创建的商品
          if (currentEditingRowIndex.value >= 0 && currentEditingRowIndex.value < orderForm.details.length) {
            orderForm.details[currentEditingRowIndex.value].inventory_id = result.data.id;
            // 更新选中商品映射
            handleSelectChange(orderForm.details[currentEditingRowIndex.value], currentEditingRowIndex.value, result.data.id);
          }

          // 关闭表单
          createInventoryFormVisible.value = false;
        } else {
          ElMessage.error('创建商品失败！');
        }
      }).catch(error => {
        console.error('创建商品错误:', error);
        ElMessage.error('创建商品发生错误！');
      });
    } else {
      // 显示表单验证错误
      for (let key in fields) {
        ElMessage.error(fields[key][0].message);
      }
    }
  });
};

// 客户选择变化时的处理
const handleClientChange = () => {
  // 根据客户ID获取客户地址
  if (orderForm.client_id) {
    const selectedClient = clients.value.find(c => c.uid === orderForm.client_id);
    if (selectedClient && selectedClient.address) {
      orderForm.address = selectedClient.address;
    } else {
      orderForm.address = '';
    }
  } else {
    orderForm.address = '';
  }
};
</script>

<template>
  <MainBox title="创建订单">
    <!-- 订单表单 -->
    <el-form
      ref="orderFormRef"
      :model="orderForm"
      :rules="orderFormRules"
      label-width="120px"
      class="order-form"
    >
      <!-- 基本信息 -->
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="订单编号" prop="order_number">
            <el-input v-model="orderForm.order_number" placeholder="请输入订单编号"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="签单品牌" prop="brand_id">
            <el-select
              v-model="orderForm.brand_id"
              placeholder="请选择品牌"
              @change="loadInventories"
              style="width: 100%"
            >
              <el-option :value="0" label="请选择品牌..."></el-option>
              <el-option
                v-for="brand in brands"
                :key="brand.id"
                :value="brand.id"
                :label="brand.name"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="签单客户" prop="client_id">
            <el-select
              v-model="orderForm.client_id"
              placeholder="请选择客户"
              filterable
              style="width: 100%"
              @change="handleClientChange"
            >
              <el-option
                v-for="client in clients"
                :key="client.uid"
                :value="client.uid"
                :label="client.name + ' - ' + client.telephone"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="签单人员" prop="staff_id">
            <el-select
              v-model="orderForm.staff_id"
              placeholder="请选择签单人员"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="staff in staffs"
                :key="staff.uid"
                :value="staff.uid"
                :label="staff.name"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="订单总额" prop="total_amount">
            <el-input-number
              v-model="orderForm.total_amount"
              :precision="2"
              :step="100"
              :min="0"
              style="width: 100%"
              @change="handleAmountChange"
            ></el-input-number>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="首付定金" prop="down_payment">
            <el-input-number
              v-model="orderForm.down_payment"
              :precision="2"
              :step="100"
              :min="0"
              style="width: 100%"
              @change="handleAmountChange"
            ></el-input-number>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="16">
          <el-form-item label="送货地址" prop="address">
            <el-input
              v-model="orderForm.address"
              placeholder="选择客户后将自动填入客户地址, 如有不同请更正!"
              type="text"
            ></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="! 待收尾款">
            <el-input-number
              v-model="orderForm.pending_balance"
              :precision="2"
              disabled
              style="width: 100%"
            ></el-input-number>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 订单详情 -->
      <div class="order-details-header">
        <h3>订单详情</h3>
        <el-button
          type="primary"
          @click="addOrderDetail"
          :disabled="!orderForm.brand_id"
        >
          添加商品
        </el-button>
      </div>

      <el-table :data="orderForm.details" border style="width: 100%; margin-bottom: 20px;">
        <el-table-column label="序号" type="index" width="60" align="center" />

        <el-table-column label="订购商品" width="400">
          <template #default="{ row, $index }">
            <el-select
              v-model="row.inventory_id"
              filterable
              placeholder="请选择商品"
              style="width: 100%"
              @change="(val) => { handleSelectChange(row, $index, val); handleQuantityChange(); }"
            >
              <el-option :value="0" label="请选择商品" class="option-container">
                <div class="option-container">
                  <el-button
                    type="success"
                    @click.stop="openCreateInventoryForm($index)"
                    size="small"
                  >首次销售？点击新增 +
                  </el-button>
                </div>
              </el-option>
              <el-option
                v-for="inventory in inventories"
                :key="inventory.id"
                :value="inventory.id"
                :label="inventory.category.name + ' - ' + inventory.full_name + ' (¥' + inventory.cost + ')'"
                :disabled="getDisabledStatus(inventory.id, $index)"
              />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column label="订购数量">
          <template #default="{ row }">
            <el-input-number
              v-model="row.quantity"
              :min="1"
              @change="handleQuantityChange"
              style="width: 100%"
            />
          </template>
        </el-table-column>

        <el-table-column label="小计" width="150">
          <template #default="{ row }">
            <span v-if="row.inventory_id">
              ¥{{
                (inventories.find(i => i.id === row.inventory_id)?.cost || 0) * row.quantity
              }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" align="center">
          <template #default="{ $index }">
            <el-button
              type="danger"
              @click="deleteOrderDetail($index)"
              circle
              size="small"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 成本和毛利润计算区域 -->
      <el-row :gutter="20" class="cost-profit-section">
        <el-col :span="12">
            <el-form-item label="成本总价">
              <el-tooltip content="选择客户订购的商品后, 系统将自动计算成本总价! 如有出入, 请手动修改!" placement="top" effect="light">
              <el-input-number
                v-model="orderForm.total_cost"
                :precision="2"
                :step="100"
                :min="0"
                style="width: 100%"
                @change="handleCostChange"
              ></el-input-number>
            </el-tooltip>
          </el-form-item>

          <el-form-item label="初步毛利">
            <el-input-number
              v-model="orderForm.gross_profit"
              :precision="2"
              disabled
              style="width: 100%"
            ></el-input-number>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="备注">
            <el-input type="textarea" v-model="orderForm.remark" placeholder="请输入备注, 没有可以不输" resize="none" :rows="3" style="width: 100%;"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 提交按钮 -->
      <div class="form-footer">
        <el-button @click="$router.go(-1)">取消</el-button>
        <el-button type="primary" @click="previewOrder">提交订单</el-button>
      </div>
    </el-form>
  </MainBox>

  <!-- 确认窗口 -->
  <FormDialog
    title="确认订单信息"
    v-model="confirmDialogVisible"
    @submit="submitOrder"
    width="800px"
  >
    <el-descriptions title="订单信息" :column="3" border>
      <el-descriptions-item label="订单编号">{{ orderForm.order_number }}</el-descriptions-item>
      <el-descriptions-item label="签单品牌">
        {{ brands.find(b => b.id === orderForm.brand_id)?.name || '' }}
      </el-descriptions-item>
      <el-descriptions-item label="订购客户">
        {{ clients.find(c => c.uid === orderForm.client_id)?.name || '' }}
      </el-descriptions-item>
      <el-descriptions-item label="签单人员">
        {{ staffs.find(s => s.uid === orderForm.staff_id)?.name || '' }}
      </el-descriptions-item>
      <el-descriptions-item label="订单总额">¥{{ orderForm.total_amount }}</el-descriptions-item>
      <el-descriptions-item label="首付定金">¥{{ orderForm.down_payment }}</el-descriptions-item>
      <el-descriptions-item label="成本总价">¥{{ orderForm.total_cost }}</el-descriptions-item>
      <el-descriptions-item label="初步毛利">
        <el-tag
          :type="
            orderForm.gross_profit < 0 ? 'danger' :
            orderForm.gross_profit < 1000 ? 'warning' :
            orderForm.gross_profit < 3000 ? 'primary' : 'success'
          "
          effect="dark"
        >
          ¥{{ Number(orderForm.gross_profit).toFixed(2) }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="待收尾款">
        <span
          :class="{
            'text-danger': orderForm.pending_balance > 3000,
            'text-strikethrough': orderForm.pending_balance < 0
          }"
        >
          ¥{{ orderForm.pending_balance }}
        </span>
      </el-descriptions-item>
      <el-descriptions-item label="安装地址" :span="3">{{ orderForm.address }}</el-descriptions-item>
      <el-descriptions-item label="备注" :span="6">{{ orderForm.remark }}</el-descriptions-item>
    </el-descriptions>

    <div class="warning-info">
      <h3>注意!</h3>
      <p><small>请仔细核对订单信息,[确认]后可以修改但会产生操作记录!</small></p>
    </div>

    <h4>订单商品详情</h4>
    <el-table :data="orderPreviewDetails" border>
      <el-table-column prop="full_name" label="商品名称" />
      <el-table-column label="商品分类" width="100" align="center">
        <template #default="scope">
          {{ scope.row.category.name }}
        </template>
      </el-table-column>
      <el-table-column label="单价" width="100" align="right">
        <template #default="scope">
          ¥{{ scope.row.cost }}
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="80" align="center" />
      <el-table-column label="小计" width="120" align="right">
        <template #default="scope">
          ¥{{ scope.row.subtotal }}
        </template>
      </el-table-column>
    </el-table>
  </FormDialog>

  <!-- 新增商品表单 -->
  <FormDialog
    title="新增商品"
    v-model="createInventoryFormVisible"
    @submit="createInventory"
  >
    <el-form
      ref="createInventoryForm"
      :model="createInventoryFormData"
      :rules="inventoryFormRules"
      :label-width="80"
    >
      <el-form-item label="所属品牌" prop="brand_id">
        <el-select v-model="createInventoryFormData.brand_id" disabled>
          <el-option label="请选择所属品牌" :value="0"></el-option>
          <el-option
            v-for="brand in brands"
            :label="brand.name"
            :value="brand.id"
            :key="brand.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="商品分类" prop="category_id">
        <el-select v-model="createInventoryFormData.category_id">
          <el-option label="请选择商品分类" :value="0"></el-option>
          <el-option
            v-for="category in categories"
            :label="category.name"
            :value="category.id"
            :key="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="商品名称" prop="name">
        <el-input type="text" v-model="createInventoryFormData.name" />
      </el-form-item>
      <el-form-item label="商品尺寸" prop="size">
        <el-input type="text" v-model="createInventoryFormData.size" />
      </el-form-item>
      <el-form-item label="商品颜色" prop="color">
        <el-input type="text" v-model="createInventoryFormData.color" />
      </el-form-item>
      <el-form-item label="￥ 进价" prop="cost">
        <el-input type="number" v-model.number="createInventoryFormData.cost" />
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
.order-form {
  margin-top: 20px;
}

.order-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
}

.warning-info {
  width: 100%;
  text-align: center;
  color: red;
  font-weight: bold;
  margin: 15px 0;
}

.option-container {
  text-align: center;
}

.cost-profit-section {
  margin: 10px 0;
  padding: 10px 0;
  border-top: 1px dashed #eee;
}

/* 新增文本样式 */
.text-danger {
  color: #f56c6c;
  font-weight: bold;
}

.text-strikethrough {
  text-decoration: line-through;
  color: #f56c6c;
}
</style>
