export function formatDateTime(value, fallback = '-') {
  if (!value && value !== 0) return fallback
  try {
    const date = new Date(value)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return String(value)
  }
}

export function formatDate(value, fallback = '-') {
  if (!value) return fallback
  try {
    const date = new Date(value)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch {
    return String(value)
  }
}
