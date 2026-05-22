import { ref, computed } from 'vue'

export function usePagination({ defaultPageSize = 20, pageSizes = [20, 50, 100] } = {}) {
  const page = ref(1)
  const pageSize = ref(defaultPageSize)
  const total = ref(0)

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)
  const pageStart = computed(() => total.value === 0 ? 0 : (page.value - 1) * pageSize.value + 1)
  const pageEnd = computed(() => Math.min(page.value * pageSize.value, total.value))

  const visiblePages = computed(() => {
    const pages = []
    const tp = totalPages.value
    const cp = page.value
    let start = Math.max(1, cp - 2)
    let end = Math.min(tp, cp + 2)
    if (end - start < 4) {
      if (start === 1) end = Math.min(tp, start + 4)
      else start = Math.max(1, end - 4)
    }
    for (let i = start; i <= end; i++) pages.push(i)
    return pages
  })

  function setPage(newPage) {
    if (newPage < 1 || newPage > totalPages.value) return
    page.value = newPage
  }

  function setPageSize(newSize) {
    pageSize.value = newSize
    page.value = 1
  }

  function setTotal(newTotal) {
    total.value = newTotal
  }

  function reset() {
    page.value = 1
  }

  return {
    page, pageSize, total,
    totalPages, pageStart, pageEnd, visiblePages,
    pageSizes,
    setPage, setPageSize, setTotal, reset
  }
}
