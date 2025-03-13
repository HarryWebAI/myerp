<script setup>
import MainBox from '@/components/MainBox.vue'
import PaginationView from '@/components/PaginationView.vue'
import inventoryHttp from '@/api/inventoryHttp'
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import timeFormatter from '@/utils/timeFormatter'
import { useRouter } from 'vue-router'

const router = useRouter()

/** 获取数据 */
let receives = ref([])
let pagination = reactive({
  page: 1,
  total: 0,
})
onMounted(() => {
  getReceives(1)
})

watch(
  () => pagination.page,
  () => {
    getReceives(pagination.page)
  },
)

const getReceives = (page) => {
  inventoryHttp.requestReceiveData(page).then((result) => {
    if (result.status == 200) {
      pagination.total = result.data.count
      receives.value = result.data.results
    } else {
      ElMessage.error('数据请求失败!')
    }
  })
}

const showDetail = (id) => {
  router.push({ name: 'inventory_receive_detail', params: { id: id } })
}
</script>

<template>
  <MainBox title="收货列表">
    <el-card>
      <template #header>
        <h3>最新收货记录</h3>
      </template>
      <el-table :data="receives">
        <el-table-column label="收货人员" width="120">
          <template #default="scope"> {{ scope.row.user_name }} </template>
        </el-table-column>
        <el-table-column label="收货品牌" width="120">
          <template #default="scope"> {{ scope.row.brand_name }} </template>
        </el-table-column>
        <el-table-column label="收货时间" align="center">
          <template #default="scope">
            <el-tooltip
              :content="'准确时间:' + timeFormatter.stringFromDateTime(scope.row.create_time)"
              placement="top"
              effect="light"
            >
              <el-tag>
                {{ timeFormatter.stringFromDate(scope.row.create_time) }}
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="scope">
            <el-button type="success" @click="showDetail(scope.row.id)">
              <span>查看详情</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <PaginationView
          v-model="pagination.page"
          :page_size="20"
          :total="pagination.total"
        ></PaginationView>
      </template>
    </el-card>
  </MainBox>
</template>

<style scoped></style>
