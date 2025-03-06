<script setup>
// 定义v-model: 是否展示对话框, 由外面决定所以要用 v-model进行绑定
let dialogVisible = defineModel({ required: true })

// 定义props: 由外面传入参数
let props = defineProps({
  title: {
    type: String,
    default: '',
  },
  width: {
    type: String,
    default: '500',
  },
})

// 定义事件
const emits = defineEmits(['cancel', 'submit'])

// 定义内部函数
const onCancel = () => {
  // 当调用内部的 onCancel() 函数时候, 先将对话框隐藏
  dialogVisible.value = false
  // 再执行外部通过 @cancel="指定函数" 指定的函数
  emits('cancel')
}

const onSubmit = () => {
  // @submit="调用父组件指定的函数"
  emits('submit')
}
</script>

<template>
  <el-dialog v-model="dialogVisible" :title="props.title" :width="props.width">
    <slot></slot>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="onCancel"> 返回 </el-button>
        <el-button type="primary" @click="onSubmit"> 确认 </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped></style>
