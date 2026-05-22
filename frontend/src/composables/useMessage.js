import { ref } from 'vue'

const snackbarState = ref({
  show: false,
  message: '',
  color: 'success',
  timeout: 3000
})

const dialogState = ref({
  show: false,
  title: '',
  message: '',
  type: 'warning',
  resolve: null
})

export function showSnackbar(message, color = 'success', timeout = 3000) {
  snackbarState.value = { show: true, message, color, timeout }
}

export function useMessage() {
  return {
    success: (msg) => showSnackbar(msg, 'success'),
    error: (msg) => showSnackbar(msg, 'error'),
    warning: (msg) => showSnackbar(msg, 'warning'),
    info: (msg) => showSnackbar(msg, 'info'),
  }
}

export function useConfirm() {
  return (message, title = '确认操作', type = 'warning') => {
    return new Promise((resolve) => {
      dialogState.value = { show: true, title, message, type, resolve }
    })
  }
}

export function handleConfirmOk() {
  if (dialogState.value.resolve) {
    dialogState.value.resolve(true)
  }
  dialogState.value.show = false
}

export function handleConfirmCancel() {
  if (dialogState.value.resolve) {
    dialogState.value.resolve(false)
  }
  dialogState.value.show = false
}

export { snackbarState, dialogState }
