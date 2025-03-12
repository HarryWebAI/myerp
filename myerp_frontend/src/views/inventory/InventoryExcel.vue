<script setup>
import MainBox from '@/components/MainBox.vue';
import { ElMessage } from 'element-plus'
import inventoryHttp from '@/api/inventoryHttp'
import timeFormatter from '@/utils/timeFormatter'

const downloadInventory = () => {
  inventoryHttp.downloadInventoryData().then(result => {
    if (result.status === 200) {
      let a = document.createElement('a')
      let href = URL.createObjectURL(result.data)
      a.href = href
      // 获取日期, 并用timeFormatter格式化 yyyy-mm-dd
      let date = new Date()

      a.setAttribute('download', `库存列表_${timeFormatter.stringFromDate(date)}.xlsx`)
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(href)
    } else {
      ElMessage.error('下载失败')
    }
  })
}
</script>

<template>
  <MainBox title="库存备份">
    <el-button type="primary" @click="downloadInventory">下载库存</el-button>
  </MainBox>
</template>