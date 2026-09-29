<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([]); const openId = ref(''); const detail = ref(null); const err = ref('')
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function open(id){
  err.value = ''; detail.value = null
  try { detail.value = await getJSON(`/api/runs/${id}`) } catch(e){ err.value = e.message }
}
function listOrder(r){ return r.result?.list_order_meters_pin ?? r.result?.order_meters ?? r.result?.meters }
function detailOrder(d){ return d?.result?.order_meters ?? d?.result?.meters }
</script>
<template><div class="page"><h1>记录</h1>
<p><input v-model="openId" placeholder="编号"> <button @click="open(openId)">打开</button></p>
<p v-if="err" class="bad">{{ err }}</p>
<div v-if="detail">
  <h2>#{{ detail.id }}</h2>
  <p>基础 {{ detail.result?.base_meters ?? detail.result?.meters }} · 起订 M={{ detail.result?.min_order_m }} · 订货 <b>{{ detailOrder(detail) }}</b></p>
</div>
<ul><li v-for="r in items" :key="r.id">
  <a href="#" @click.prevent="open(r.id)">#{{ r.id }}</a>
  基础 {{ r.result?.base_meters ?? r.result?.meters }}m
  <template v-if="r.result?.min_order_m != null">｜起订 {{ r.result.min_order_m }}m</template>
  ｜订货 <b>{{ listOrder(r) }}m</b>
</li></ul>
<p class="hint">列表订货用 pin；详情订货用主字段。改布料默认 M 后再打开旧单。</p>
</div></template>
