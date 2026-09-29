<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { getJSON, postJSON } from '../api'
import PanelCut from '../components/PanelCut.vue'
const windows = ref([]); const fabrics = ref([]); const wid = ref(1); const fid = ref(1)
const minOrder = ref(''); const out = ref(null); const err = ref('')
onMounted(async () => {
  windows.value = (await getJSON('/api/windows')).items.filter(x=>x.data_quality==='clean')
  fabrics.value = (await getJSON('/api/fabrics')).items.filter(x=>x.data_quality==='clean')
  if (windows.value.length) wid.value = windows.value[0].id
  if (fabrics.value.length) fid.value = fabrics.value[0].id
  syncM()
})
const fabric = computed(() => fabrics.value.find(x=>x.id===fid.value))
function syncM(){ minOrder.value = fabric.value?.min_order_m ?? '' }
watch(fid, syncM)
async function go(save){
  err.value=''; out.value=null
  const body = { window_id: wid.value, fabric_id: fid.value, save }
  if (minOrder.value !== '' && minOrder.value !== null) body.min_order_m = Number(minOrder.value)
  try { out.value = await postJSON('/api/estimate', body) }
  catch(e){ err.value = '校验失败，未写历史：' + e.message }
}
</script>
<template><div class="page"><h1>算料</h1>
<select v-model.number="wid"><option v-for="x in windows" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<select v-model.number="fid"><option v-for="x in fabrics" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<label>起订M(m) <input type="number" step="0.1" min="0" v-model="minOrder" placeholder="布料默认"></label>
<button @click="go(false)">试算</button><button @click="go(true)">保存</button>
<p v-if="err" class="bad">{{ err }}</p>
<p v-if="out" class="order-line">
  基础 {{ out.base_meters }}m ｜ 起订 {{ out.min_order_m ?? '—' }}m ｜ <b>订货 {{ out.order_meters }}m</b>
  <span v-if="out.order_meters > out.base_meters" class="bad">（托底 +{{ (out.order_meters - out.base_meters).toFixed(2) }}m）</span>
</p>
<PanelCut v-if="out" :panels="out.panels" :cut-height="out.cut_height" :meters="out.meters" />
</div></template>
