<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const items = ref([]); const runs = ref([]); const msg = ref({})
onMounted(async () => {
  items.value = (await getJSON('/api/fabrics')).items
  runs.value = (await getJSON('/api/runs')).items
})
function lastOrder(fid){
  const r = runs.value.find(x => x.fabric_id === fid) // runs 按 id 倒序，首个即最近一单
  if (!r) return '—'
  const m = r.result?.order_meters ?? r.result?.meters
  return `${m}m (#${r.id})`
}
async function saveM(f){
  msg.value = { ...msg.value, [f.id]: '' }
  try {
    const v = (f.min_order_m === '' || f.min_order_m === null || f.min_order_m === undefined) ? null : Number(f.min_order_m)
    const updated = await putJSON(`/api/fabrics/${f.id}/min-order`, { min_order_m: v })
    f.min_order_m = updated.min_order_m
    msg.value = { ...msg.value, [f.id]: '已保存（不影响历史单）' }
  } catch(e){ msg.value = { ...msg.value, [f.id]: '失败：' + e.message } }
}
</script>
<template><div class="page"><h1>面料</h1>
<table class="fab-table">
  <thead><tr><th>名称</th><th>门幅</th><th>上/下折边</th><th>起订M(m)</th><th></th><th>最近订货</th></tr></thead>
  <tbody>
    <tr v-for="f in items" :key="f.id">
      <td>{{ f.name }}</td>
      <td>{{ f.fabric_width }}m</td>
      <td>{{ f.hem_top }}/{{ f.hem_bottom }}m</td>
      <td><input type="number" step="0.1" min="0" v-model="f.min_order_m" placeholder="无"></td>
      <td><button @click="saveM(f)">保存</button> <span class="muted">{{ msg[f.id] }}</span></td>
      <td>{{ lastOrder(f.id) }}</td>
    </tr>
  </tbody>
</table>
</div></template>
