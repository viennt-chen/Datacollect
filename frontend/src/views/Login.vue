<template>
  <v-app>
    <v-main>
      <div class="login-container">
        <!-- Background decorations -->
        <div class="login-background">
          <div class="bg-circle bg-circle-1"></div>
          <div class="bg-circle bg-circle-2"></div>
          <div class="bg-circle bg-circle-3"></div>
        </div>

        <!-- Login card -->
        <v-card class="login-card mx-auto" max-width="450" rounded="xl" elevation="12">
          <!-- Header -->
          <div class="login-header pa-8 text-center">
            <v-avatar size="80" color="rgba(255,255,255,0.2)" class="mb-4">
              <v-icon icon="mdi-shield-lock" size="40" color="white" />
            </v-avatar>
          </div>

          <!-- Form -->
          <v-card-text class="pa-8">
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="formData.username"
                label="用户名 / 邮箱"
                prepend-inner-icon="mdi-account"
                :error-messages="errors.username"
                @blur="validateUsername"
                autocomplete="username"
                variant="outlined"
                class="mb-2"
              />

              <v-text-field
                v-model="formData.password"
                label="密码"
                prepend-inner-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                :error-messages="errors.password"
                @blur="validatePassword"
                autocomplete="current-password"
                variant="outlined"
                class="mb-1"
              />

              <!-- Password strength indicator -->
              <div v-if="formData.password" class="d-flex align-center ga-2 mb-2">
                <div class="d-flex ga-1 flex-grow-1">
                  <v-progress-linear
                    v-for="(level, index) in 4"
                    :key="index"
                    :model-value="index < passwordStrength ? 100 : 0"
                    :color="getStrengthColor()"
                    height="4"
                    rounded
                  />
                </div>
                <span class="text-caption" :class="getStrengthTextClass()">
                  {{ passwordStrengthText }}
                </span>
              </div>

              <div class="d-flex justify-space-between align-center mb-4">
                <v-checkbox
                  v-model="formData.rememberMe"
                  label="记住我（7 天内自动登录）"
                  density="compact"
                  hide-details
                  color="primary"
                />
                <a href="#" class="text-primary text-body-2" @click.prevent="handleForgotPassword">
                  忘记密码？
                </a>
              </div>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="isLoading"
                prepend-icon="mdi-login"
                class="mb-4"
              >
                登录
              </v-btn>

              <v-alert
                v-if="loginError"
                type="error"
                variant="tonal"
                closable
                @click:close="loginError = ''"
              >
                {{ loginError }}
              </v-alert>
            </v-form>
          </v-card-text>

          <v-divider />
          <v-card-actions class="justify-center pa-4">
            <span class="text-caption text-medium-emphasis">&copy; 2026 All rights reserved.</span>
          </v-card-actions>
        </v-card>
      </div>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi } from '@/api'

const router = useRouter()
const route = useRoute()

const formData = ref({
  username: '',
  password: '',
  rememberMe: false
})

const showPassword = ref(false)
const isLoading = ref(false)
const loginError = ref('')
const errors = ref({})

const passwordStrength = computed(() => {
  const password = formData.value.password
  if (!password) return 0
  let strength = 0
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++
  return Math.min(strength, 4)
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return '请输入密码'
  if (strength <= 2) return '弱'
  if (strength === 3) return '中等'
  return '强'
})

const getStrengthColor = () => {
  const s = passwordStrength.value
  if (s <= 2) return 'error'
  if (s === 3) return 'warning'
  return 'success'
}

const getStrengthTextClass = () => {
  const strength = passwordStrength.value
  if (strength <= 2) return 'text-error'
  if (strength === 3) return 'text-warning'
  return 'text-success'
}

const validateUsername = () => {
  errors.value.username = ''
  const username = formData.value.username.trim()
  if (!username) {
    errors.value.username = '请输入用户名或邮箱'
    return false
  }
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  const usernamePattern = /^[a-zA-Z0-9_]{3,50}$/
  if (!emailPattern.test(username) && !usernamePattern.test(username)) {
    errors.value.username = '请输入有效的用户名或邮箱格式'
    return false
  }
  return true
}

const validatePassword = () => {
  errors.value.password = ''
  const password = formData.value.password
  if (!password) {
    errors.value.password = '请输入密码'
    return false
  }
  if (password.length < 8) {
    errors.value.password = '密码长度至少为 8 位'
    return false
  }
  const hasUpper = /[A-Z]/.test(password)
  const hasLower = /[a-z]/.test(password)
  const hasDigit = /\d/.test(password)
  const hasSpecial = /[^a-zA-Z0-9]/.test(password)
  const passedChecks = [hasUpper, hasLower, hasDigit, hasSpecial].filter(Boolean).length
  if (passedChecks < 3) {
    errors.value.password = '密码需包含大小写字母、数字和特殊字符中的至少三种'
    return false
  }
  return true
}

const validateForm = () => {
  const usernameValid = validateUsername()
  const passwordValid = validatePassword()
  return usernameValid && passwordValid
}

const handleLogin = async () => {
  loginError.value = ''
  if (!validateForm()) return
  isLoading.value = true
  try {
    const response = await authApi.login({
      username: formData.value.username.trim(),
      password: formData.value.password,
      remember_me: formData.value.rememberMe
    })
    localStorage.setItem('access_token', response.data.access_token)
    if (response.data.refresh_token) {
      localStorage.setItem('refresh_token', response.data.refresh_token)
    }
    localStorage.setItem('user_info', JSON.stringify(response.data.user_info))
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    if (error.response) {
      loginError.value = error.response.data.detail || '登录失败，请检查用户名和密码'
    } else if (error.request) {
      loginError.value = '网络连接失败，请检查网络'
    } else {
      loginError.value = '登录失败，请稍后重试'
    }
  } finally {
    isLoading.value = false
  }
}

const handleForgotPassword = () => {
  alert('请联系系统管理员重置密码')
}

onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (token) {
    // already logged in
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.bg-circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
}

.bg-circle-2 {
  width: 400px;
  height: 400px;
  bottom: -150px;
  right: -150px;
  animation-delay: 5s;
}

.bg-circle-3 {
  width: 250px;
  height: 250px;
  top: 50%;
  left: 50%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(50px, -50px) scale(1.1); }
  66% { transform: translate(-50px, 50px) scale(0.9); }
}

.login-card {
  position: relative;
  z-index: 1;
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
