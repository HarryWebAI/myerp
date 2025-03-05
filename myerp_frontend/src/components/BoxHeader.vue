<script setup name="OAPageHeader">
import { useRouter } from 'vue-router'
import { defineProps } from 'vue'

let props = defineProps({
  // eslint-disable-next-line vue/require-prop-type-constructor
  content: '',
})

const router = useRouter()
const goBack = () => {
  router.go(-1)
}
</script>

<template>
  <el-page-header @back="goBack" title="上一页">
    <template #content>
      <span>当前: {{ props.content }} </span>
    </template>
  </el-page-header>
</template>

<style scoped></style>
