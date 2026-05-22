<template>
  <div class="bom-node" :class="{ 'bom-node--root': !data.bom_item_id }">
    <Handle type="target" :position="Position.Top" />
    <v-card
      :color="data.bom_item_id ? 'white' : 'primary'"
      :variant="data.bom_item_id ? 'outlined' : 'tonal'"
      :class="{ 'elevation-4': selected }"
      class="bom-node-card"
      @contextmenu.prevent="onContextMenu"
    >
      <v-card-text class="pa-3">
        <div class="d-flex align-center ga-2 mb-1">
          <v-icon
            :icon="data.has_bom ? 'mdi-file-tree' : 'mdi-package-variant-closed'"
            :color="data.bom_item_id ? (data.has_bom ? 'primary' : 'grey') : 'white'"
            size="18"
          />
          <span class="font-weight-bold text-truncate" style="max-width: 160px">
            {{ data.product_name }}
          </span>
        </div>
        <div class="text-caption text-medium-emphasis mb-2">
          {{ data.product_code || data.part_number || '-' }}
        </div>
        <div v-if="data.specification" class="text-caption text-medium-emphasis mb-2 text-truncate" style="max-width: 200px">
          {{ data.specification }}
        </div>
        <div class="d-flex align-center ga-1 flex-wrap">
          <v-chip size="x-small" color="info" variant="tonal">x{{ formatQty(data.quantity) }}</v-chip>
          <span v-if="data.unit" class="text-caption text-medium-emphasis">{{ data.unit }}</span>
          <v-chip v-if="data.reference_designator" size="x-small" color="secondary" variant="outlined">
            {{ data.reference_designator }}
          </v-chip>
        </div>
      </v-card-text>
      <v-divider />
      <v-card-actions class="pa-1">
        <v-btn icon size="x-small" variant="text" @click.stop="$emit('edit-quantity', data)">
          <v-icon icon="mdi-pencil" size="14" />
          <v-tooltip activator="parent" location="top">编辑用量</v-tooltip>
        </v-btn>
        <v-btn icon size="x-small" variant="text" @click.stop="$emit('add-child', data)">
          <v-icon icon="mdi-plus" size="14" />
          <v-tooltip activator="parent" location="top">添加子项</v-tooltip>
        </v-btn>
        <v-spacer />
        <v-btn
          v-if="data.bom_item_id"
          icon size="x-small" variant="text" color="error"
          @click.stop="$emit('delete-item', data)"
        >
          <v-icon icon="mdi-delete" size="14" />
          <v-tooltip activator="parent" location="top">删除</v-tooltip>
        </v-btn>
      </v-card-actions>
    </v-card>
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>

<script setup>
import { Handle, Position } from '@vue-flow/core'

defineProps({
  data: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})

defineEmits(['edit-quantity', 'add-child', 'delete-item'])

function formatQty(qty) {
  const n = parseFloat(qty)
  if (isNaN(n)) return '0'
  return n % 1 === 0 ? n.toString() : n.toFixed(2)
}

function onContextMenu(e) {
  // Parent handles via vue-flow event
}
</script>

<style scoped>
.bom-node {
  min-width: 220px;
  max-width: 260px;
}
.bom-node-card {
  border-radius: 8px;
  transition: box-shadow 0.2s;
}
.bom-node-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
