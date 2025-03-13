<script setup>
import MainBox from '@/components/MainBox.vue';
import { ElMessage } from 'element-plus'
import inventoryHttp from '@/api/inventoryHttp'
import timeFormatter from '@/utils/timeFormatter'
import { useAuthStore } from '@/stores/auth'
import { Download, Upload, Warning, Document, InfoFilled } from '@element-plus/icons-vue'
import inventoryLog from '@/api/inventoryHttp'
import { ref, onMounted } from 'vue'
const authStore = useAuthStore()
const baseAction = import.meta.env.VITE_BASE_URL
const logs = ref([])

// 上传前的验证
const beforeUpload = (file) => {
  // 检查文件类型
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
    file.type === 'application/vnd.ms-excel'
  if (!isExcel) {
    ElMessage.error('只能上传 Excel 文件!')
    return false
  }

  // 检查文件大小（限制为 5MB）
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('文件大小不能超过 5MB!')
    return false
  }

  return true
}

// 上传成功的回调
const handleSuccess = (response) => {
  if (response.detail) {
    ElMessage.success(response.detail)
    setTimeout(() => {
      window.location.reload()
    }, 1000);
  }
}

// 上传失败的回调
const handleError = (error) => {
  const errorMsg = error.response?.data?.detail || '上传失败'
  ElMessage.error(errorMsg)
}

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

onMounted(() => {
  inventoryLog.requestInventoryLog().then(result => {
    if (result.status === 200) {
      logs.value = result.data
    } else {
      ElMessage.error('获取库存日志失败')
    }
  })
})

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return '';
  const date = new Date(timeString);
  return timeFormatter.stringFromDateTime(date);
}

// 获取日志类型（用于时间线图标颜色）
const getLogType = () => {
  // 可以根据日志内容判断不同类型，这里简单返回primary
  return 'primary';
}
</script>

<template>
  <MainBox title="盘点备份">
    <div class="excel-page-container">
      <!-- 提示区域 -->
      <div class="section prep-section">
        <div class="section-header">
          <el-icon class="header-icon"><InfoFilled /></el-icon>
          <h3>第一步：准备工作</h3>
        </div>
        <div class="section-content">
          <div class="prep-steps">
            <div class="prep-step danger-warning">
              <div class="step-number"><el-icon><Warning /></el-icon></div>
              <div class="step-content">
                <h4>谨慎使用该功能!</h4>
                <p>该功能主要用于[系统初次投入使用],以及[年度盘库盘点],要求系统在盘点期间停用,并且提交后会对现存记录造成不可逆地修改!</p>
              </div>
            </div>

            <div class="prep-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>确保订单全部出库</h4>
                <p>盘点前，请确保系统内现存订单都已完成出库操作!</p>
              </div>
            </div>

            <div class="prep-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>暂停系统一切操作</h4>
                <p>在盘点期间，请暂停在系统内新增发货, 收货, 订单记录, 确保库存数据稳定!</p>
              </div>
            </div>

            <div class="prep-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>明确记录盘点时间</h4>
                <p>明确记录盘点开始的具体时间，作为数据核对的时间节点, 期间的记录考虑可以用手写笔记记录!</p>
              </div>
            </div>

            <div class="prep-step">
              <div class="step-number">4</div>
              <div class="step-content">
                <h4>盘点后再补充记录</h4>
                <p>请在库存盘点结束后，再在系统中补录盘点期间的发货、收货和订单记录!</p>
              </div>
            </div>


          </div>

          <div class="prep-notice">
            <el-icon><Warning /></el-icon>
            <span>请严格按照以上步骤操作，确保盘点数据的准确性</span>
          </div>
        </div>
      </div>

      <!-- 下载区域 -->
      <div class="section download-section">
        <div class="section-header">
          <el-icon class="header-icon"><Download /></el-icon>
          <h3>第二步：下载当前库存备份</h3>
        </div>
        <div class="section-content">
          <div class="warning-box">
            <el-icon><Warning /></el-icon>
            <span>建议：在进行上传操作前，先下载当前库存数据作为备份！</span>
          </div>
          <el-button type="primary" @click="downloadInventory" class="action-button">
            <el-icon><Download /></el-icon>
            下载库存数据
          </el-button>
        </div>
      </div>

      <!-- 上传区域 -->
      <div class="section upload-section">
        <div class="section-header">
          <el-icon class="header-icon"><Upload /></el-icon>
          <h3>第三步：上传新的库存数据</h3>
        </div>
        <div class="section-content">
          <div class="warning-box danger">
            <el-icon><Warning /></el-icon>
            <span>警告：上传新文件将会清空现有库存数据，请确保数据准确无误！</span>
          </div>

          <el-upload
            class="upload-excel"
            :action="baseAction + '/upload/'"
            :headers="{ Authorization: 'JWT ' + authStore.token }"
            :before-upload="beforeUpload"
            :on-success="handleSuccess"
            :on-error="handleError"
            :show-file-list="true"
            :limit="1"
            accept=".xlsx,.xls"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .xlsx, .xls 格式的 Excel 文件，大小不超过 5MB
              </div>
            </template>
          </el-upload>
        </div>
      </div>

      <!-- 库存盘点日志 -->
      <div class="section log-section">
        <div class="section-header">
          <el-icon class="header-icon"><Document /></el-icon>
          <h3>库存盘点日志</h3>
          <div class="header-extra">共 {{ logs.length }} 条记录</div>
        </div>
        <div class="section-content">
          <el-empty v-if="logs.length === 0" description="暂无盘点记录" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="log in logs"
              :key="log.id"
              :timestamp="formatTime(log.create_time)"
              placement="top"
              :type="getLogType()"
            >
              <el-card class="log-card">
                <div class="log-header">
                  <span class="log-title">盘点操作</span>
                  <el-tag size="small">{{ log.operator_name }}</el-tag>
                </div>
                <div class="log-content">{{ log.content }}</div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </MainBox>
</template>

<style scoped>
.excel-page-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 24px;
  transition: all 0.3s ease;
}

.section:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 16px;
  position: relative;
}

.header-icon {
  font-size: 24px;
  margin-right: 12px;
  color: var(--el-color-primary);
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.section-content {
  padding: 0 12px;
}

.warning-box {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #fdf6ec;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #faecd8;
}

.warning-box.danger {
  background: #fef0f0;
  border-color: #fde2e2;
}

.warning-box .el-icon {
  font-size: 16px;
  color: #e6a23c;
  margin-right: 8px;
}

.warning-box.danger .el-icon {
  color: #f56c6c;
}

.warning-box span {
  color: #666;
  font-size: 14px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
}

.upload-excel {
  width: 100%;
}

.upload-excel :deep(.el-upload) {
  width: 100%;
}

.upload-excel :deep(.el-upload-dragger) {
  width: 100%;
  padding: 30px 20px;
  background: #fafafa;
  border: 2px dashed #dcdfe6;
  transition: all 0.3s;
}

.upload-excel :deep(.el-upload-dragger:hover) {
  border-color: var(--el-color-primary);
  background: #f5f7fa;
}

.upload-excel :deep(.el-icon--upload) {
  font-size: 48px;
  color: #909399;
  margin-bottom: 16px;
}

.upload-excel :deep(.el-upload__text) {
  color: #606266;
  font-size: 16px;
}

.upload-excel :deep(.el-upload__text em) {
  color: var(--el-color-primary);
  font-style: normal;
  cursor: pointer;
}

.el-upload__tip {
  color: #909399;
  font-size: 14px;
  margin-top: 12px;
  text-align: center;
}

/* 添加响应式设计 */
@media screen and (max-width: 768px) {
  .excel-page-container {
    padding: 12px;
    gap: 20px;
  }

  .section {
    padding: 16px;
  }

  .section-header {
    padding-bottom: 12px;
    margin-bottom: 16px;
  }

  .header-icon {
    font-size: 20px;
  }

  .section-header h3 {
    font-size: 16px;
  }
}

.log-section {
  /* margin-top已由容器的gap属性控制 */
}

.header-extra {
  margin-left: auto;
  color: #909399;
  font-size: 14px;
}

.log-card {
  --el-card-padding: 16px;
  margin-bottom: 5px;
  transition: all 0.3s;
}

.log-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.log-title {
  font-weight: 500;
  color: #303133;
}

.log-content {
  color: #606266;
  line-height: 1.6;
}

.log-content :deep(strong) {
  font-weight: 600;
}

:deep(.el-timeline-item__node--primary) {
  background-color: var(--el-color-primary);
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  margin-bottom: 8px;
}

/* 调整时间线间距 */
:deep(.el-timeline-item) {
  padding-bottom: 20px;
}
:deep(.el-timeline-item:last-child) {
  padding-bottom: 0;
}

/* 准备工作部分样式 */
.prep-section .section-content {
  padding: 5px 15px 15px;
}

.prep-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.prep-step {
  display: flex;
  align-items: flex-start;
  background-color: var(--el-color-primary-light-9);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.prep-step:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  background-color: var(--el-color-primary-light-8);
}

.step-number {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
  color: white;
  font-weight: bold;
  margin-right: 16px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h4 {
  margin: 0 0 8px 0;
  color: var(--el-color-primary-dark-2);
  font-size: 16px;
}

.step-content p {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}

.prep-notice {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: #fdf6ec;
  border-radius: 4px;
  border: 1px solid #faecd8;
}

.prep-notice .el-icon {
  color: #e6a23c;
  font-size: 18px;
  margin-right: 10px;
}

.prep-notice span {
  color: #666;
  font-size: 14px;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .prep-step {
    padding: 12px;
  }

  .step-number {
    width: 28px;
    height: 28px;
    margin-right: 12px;
  }

  .step-content h4 {
    font-size: 15px;
  }
}

/* 危险警告样式 */
.danger-warning {
  background-color: var(--el-color-danger-light-9);
  border: 1px solid var(--el-color-danger);
  animation: pulse 2s infinite;
}

.danger-warning:hover {
  background-color: var(--el-color-danger-light-8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.2);
}

.danger-warning .step-number {
  background-color: var(--el-color-danger);
  width: 34px;
  height: 34px;
}

.danger-warning .step-number .el-icon {
  font-size: 18px;
}

.danger-warning h4 {
  color: var(--el-color-danger) !important;
  font-weight: 700;
  font-size: 17px !important;
}

.danger-warning p {
  color: #f56c6c !important;
  font-weight: 500;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(245, 108, 108, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}
</style>
