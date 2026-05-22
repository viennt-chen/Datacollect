export function cleanParams(params) {
  const result = {}
  for (const [key, value] of Object.entries(params)) {
    if (value !== '' && value !== null && value !== undefined) {
      result[key] = value
    }
  }
  return result
}
