<template>
  <div v-if="material">
    <v-list density="compact">
      <v-list-item prepend-icon="mdi-package-variant" :title="material.product_name" :subtitle="'U9 编码: ' + material.u9_material_code" />
      <v-list-item v-if="material.part_number" prepend-icon="mdi-barcode" title="零件号" :subtitle="material.part_number" />
      <v-list-item v-if="material.specification" prepend-icon="mdi-ruler" title="规格" :subtitle="material.specification" />
      <v-list-item v-if="material.category" prepend-icon="mdi-shape" title="分类" :subtitle="material.category" />
      <v-list-item v-if="material.material_type" prepend-icon="mdi-tag" title="物料类型" :subtitle="material.material_type" />
    </v-list>
  </div>
  <div v-else class="text-center pa-8 text-medium-emphasis">
    <v-icon icon="mdi-package-variant-closed" size="48" />
    <p class="mt-2">未找到关联物料</p>
  </div>
</template>

<script setup>
defineProps({
  material: { type: Object, default: null }
})
</script>
