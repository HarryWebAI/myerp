<script setup name="OAMain">
import BoxHeader from './BoxHeader.vue'

let props = defineProps({
  // eslint-disable-next-line vue/require-prop-type-constructor
  title: '',
})
</script>

<template>
  <el-space style="width: 100%" direction="vertical" :fill="true" :size="15">
    <BoxHeader :content="props.title"></BoxHeader>

    <!-- 待填充的默认插槽 -->
    <slot></slot>
  </el-space>
</template>

<style scoped></style>
