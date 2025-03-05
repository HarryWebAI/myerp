<script setup>
import { defineProps } from 'vue'

let props = defineProps({
  // eslint-disable-next-line vue/require-prop-type-constructor
  page_size: 0,
  // eslint-disable-next-line vue/require-prop-type-constructor
  total: 0,
})

let page = defineModel({
  required: true,
})
</script>

<template>
  <el-pagination
    background
    layout="prev, pager, next"
    :total="props.total"
    :page-size="props.page_size"
    v-model:current-page="page"
    style="justify-content: center"
  />
</template>

<style scoped></style>
