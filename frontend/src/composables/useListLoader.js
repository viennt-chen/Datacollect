import { ref } from 'vue'
import { cleanParams } from '@/utils/params'

export function useListLoader(apiFn, {
  onSuccess,
  onError,
  dataPath = 'data.items',
  totalPath = 'data.total'
} = {}) {
  const loading = ref(false)
  const list = ref([])

  function getNestedValue(obj, path) {
    return path.split('.').reduce((acc, key) => acc?.[key], obj)
  }

  async function load(params = {}) {
    loading.value = true
    try {
      const cleaned = cleanParams(params)
      const response = await apiFn(cleaned)
      list.value = getNestedValue(response, dataPath) || []
      const totalCount = getNestedValue(response, totalPath) || 0
      onSuccess?.(response, totalCount)
      return { items: list.value, total: totalCount }
    } catch (error) {
      console.error('加载数据失败:', error)
      onError?.(error)
      return { items: [], total: 0 }
    } finally {
      loading.value = false
    }
  }

  return { loading, list, load }
}
