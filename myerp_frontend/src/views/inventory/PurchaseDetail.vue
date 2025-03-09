<script setup>
import MainBox from '@/components/MainBox.vue'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import inventoryHttp from '@/api/inventoryHttp'
import { ElMessage } from 'element-plus'

const route = useRoute()
const purchases_id = route.params.id
let details = ref([])

onMounted(() => {
  inventoryHttp.requestPurchaseDetails(purchases_id).then((result) => {
    if (result.status == 200) {
      details.value = result.data
    } else {
      ElMessage.error('数据请求失败!')
    }
  })
})
</script>

<template>
  <MainBox title="发货详情">
    <el-card>
      <el-table :data="details">
        <el-table-column prop="inventory.full_name" label="名称"></el-table-column>
        <el-table-column prop="quantity" label="数量"></el-table-column>
        <el-table-column prop="inventory.cost" label="价格"></el-table-column>
        <el-table-column label="总价">
          <template #default="scope">
            {{ scope.row.quantity * scope.row.inventory.cost }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </MainBox>
</template>

<style scoped></style>
