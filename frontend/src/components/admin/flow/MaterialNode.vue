<template>
  <div class="material-node" :class="{ selected: selected }">
    <div class="node-header">
      <v-icon icon="mdi-package-variant" size="16" color="white" />
      <span class="node-title">{{ data.label || '物料' }}</span>
    </div>
    <div class="node-body">
      <div v-if="data.material_code" class="node-info">
        <v-icon icon="mdi-barcode" size="12" />
        {{ data.material_code }}
      </div>
      <div v-if="data.part_number" class="node-info">
        <v-icon icon="mdi-pound" size="12" />
        {{ data.part_number }}
      </div>
      <div v-if="data.quantity" class="node-info">
        <v-icon icon="mdi-counter" size="12" />
        {{ data.quantity }}
      </div>
    </div>
    <Handle type="target" :position="Position.Left" />
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script setup>
import { Handle, Position } from '@vue-flow/core'

defineProps({
  data: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})
</script>

<style scoped>
.material-node {
  background: #e3f2fd;
  border: 2px solid #2196f3;
  border-radius: 8px;
  min-width: 140px;
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s;
}
.material-node:hover,
.material-node.selected {
  box-shadow: 0 4px 16px rgba(33, 150, 243, 0.3);
}
.node-header {
  background: #2196f3;
  color: white;
  padding: 4px 8px;
  border-radius: 6px 6px 0 0;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: bold;
  font-size: 12px;
}
.node-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}
.node-body {
  padding: 6px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.node-info {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 11px;
}
</style>
