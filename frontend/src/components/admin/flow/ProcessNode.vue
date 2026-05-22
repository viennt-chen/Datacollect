<template>
  <div class="process-node" :class="{ selected: selected }">
    <div class="node-header">
      <v-icon icon="mdi-cog" size="16" color="white" />
      <span class="node-title">{{ data.label || '工序' }}</span>
    </div>
    <div class="node-body">
      <div v-if="data.device_type" class="node-info">
        <v-icon icon="mdi-cpu-64-bit" size="12" />
        {{ data.device_type }}
      </div>
      <div v-if="data.expected_duration_min" class="node-info">
        <v-icon icon="mdi-clock-outline" size="12" />
        {{ data.expected_duration_min }}分钟
      </div>
      <div v-if="data.process_code" class="node-info">
        <v-icon icon="mdi-pound" size="12" />
        {{ data.process_code }}
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
.process-node {
  background: #fff3e0;
  border: 2px solid #ff9800;
  border-radius: 8px;
  min-width: 140px;
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s;
}
.process-node:hover,
.process-node.selected {
  box-shadow: 0 4px 16px rgba(255, 152, 0, 0.3);
}
.node-header {
  background: #ff9800;
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
