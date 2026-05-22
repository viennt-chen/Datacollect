import { ref } from 'vue'

export function useSelection({ isSelectable } = {}) {
  const selectedIds = ref([])

  function isAllSelected(list) {
    const selectable = isSelectable ? list.filter(isSelectable) : list
    return selectable.length > 0 && selectable.every(item => selectedIds.value.includes(item.id))
  }

  function toggleSelectAll(list) {
    if (isAllSelected(list)) {
      selectedIds.value = []
    } else {
      const selectable = isSelectable ? list.filter(isSelectable) : list
      selectedIds.value = selectable.map(item => item.id)
    }
  }

  function toggleSelect(id) {
    const idx = selectedIds.value.indexOf(id)
    if (idx === -1) {
      selectedIds.value = [...selectedIds.value, id]
    } else {
      selectedIds.value = selectedIds.value.filter(x => x !== id)
    }
  }

  function clearSelection() {
    selectedIds.value = []
  }

  return {
    selectedIds,
    isAllSelected,
    toggleSelectAll,
    toggleSelect,
    clearSelection
  }
}
