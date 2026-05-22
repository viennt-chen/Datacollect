import { ref, reactive } from 'vue'

export function useCrudDialog({ createFn, updateFn, validateFn, onSuccess, onError, defaults = {} } = {}) {
  const showAddDialog = ref(false)
  const showEditDialog = ref(false)
  const showViewDialog = ref(false)
  const saving = ref(false)

  const formData = reactive({ ...defaults })
  const formErrors = reactive({})
  const viewData = ref({})

  function openAdd() {
    Object.assign(formData, { ...defaults })
    Object.keys(formErrors).forEach(k => formErrors[k] = '')
    showAddDialog.value = true
  }

  function openEdit(item) {
    Object.assign(formData, item)
    Object.keys(formErrors).forEach(k => formErrors[k] = '')
    showEditDialog.value = true
  }

  function openView(item) {
    viewData.value = { ...item }
    showViewDialog.value = true
  }

  function closeDialog() {
    showAddDialog.value = false
    showEditDialog.value = false
  }

  function resetForm() {
    Object.assign(formData, { ...defaults })
    Object.keys(formErrors).forEach(k => formErrors[k] = '')
  }

  async function save() {
    if (validateFn) {
      const { valid, errors } = validateFn(formData)
      Object.assign(formErrors, errors)
      if (!valid) return false
    }

    saving.value = true
    try {
      const data = { ...formData }
      delete data.id

      if (showEditDialog.value && formData.id && updateFn) {
        await updateFn(formData.id, data)
      } else if (createFn) {
        await createFn(data)
      }

      closeDialog()
      onSuccess?.()
      return true
    } catch (error) {
      const detail = error.response?.data?.detail || error.message
      onError?.(detail, error)
      return false
    } finally {
      saving.value = false
    }
  }

  return {
    showAddDialog, showEditDialog, showViewDialog,
    saving, formData, formErrors, viewData,
    openAdd, openEdit, openView, closeDialog, resetForm, save
  }
}
