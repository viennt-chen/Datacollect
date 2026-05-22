<template>
  <v-app :class="{ 'fullscreen-mode': isFullscreen }">
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      color="#0f172a"
      theme="dark"
      height="100vh"
      style="position: fixed;"
      :class="{ 'd-none': isFullscreen }"
    >
      <v-list-item prepend-icon="mdi-speedometer" title="数据监控" nav>
        <template v-slot:append>
          <v-btn
            variant="text"
            :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
            @click="rail = !rail"
            size="small"
          />
        </template>
      </v-list-item>

      <v-divider />

      <v-list nav density="comfortable" style="overflow-y: auto; max-height: calc(100vh - 180px);">
        <v-list-item
          v-for="module in dashboardModules"
          :key="module.id"
          :to="{ name: module.routeName }"
          :prepend-icon="module.icon"
          :title="module.name"
          :active="currentModule === module.id"
          active-color="info"
          rounded="lg"
        />
      </v-list>

      <template v-slot:append>
        <v-divider />
        <v-list nav density="comfortable">
          <v-list-item
            v-for="link in externalLinks"
            :key="link.label"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            :prepend-icon="link.icon"
            :title="link.label"
            rounded="lg"
          />
          <v-list-item
            :to="{ name: 'Admin' }"
            prepend-icon="mdi-cog"
            title="管理后台"
            rounded="lg"
          />
          <v-list-item
            :to="{ name: 'Home' }"
            prepend-icon="mdi-home"
            title="返回首页"
            rounded="lg"
          />
        </v-list>
      </template>
    </v-navigation-drawer>

    <v-app-bar
      color="white"
      elevation="1"
      :class="{ 'd-none': isFullscreen }"
    >
      <v-app-bar-nav-icon @click="rail = !rail" />
      <v-app-bar-title>
        <v-icon icon="mdi-speedometer" color="info" class="mr-2" />
        {{ currentModuleInfo.name }}
      </v-app-bar-title>
      <v-spacer />
      <v-chip prepend-icon="mdi-account-circle" variant="text">访客</v-chip>
      <v-btn
        :prepend-icon="isFullscreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'"
        variant="tonal"
        color="info"
        @click="toggleFullscreen"
        class="ml-2"
      >
        {{ isFullscreen ? '退出全屏' : '全屏' }}
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view
          :time-range="timeRange"
          :limit="realtimeLimit"
          :is-fullscreen="isFullscreen"
          @update:lastUpdate="handleUpdate"
        />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const drawer = ref(true)
const rail = ref(false)
const timeRange = ref('7')
const realtimeLimit = ref('20')
const isFullscreen = ref(false)

const dashboardModules = [
  { id: 'machine', name: '设备监控', icon: 'mdi-cog', routeName: 'DashboardMachine' },
  { id: 'realtime', name: '实时数据', icon: 'mdi-broadcast', routeName: 'DashboardRealtime' },
]

const externalLinks = [
  { label: '出风口', url: 'http://10.10.180.241:9002/', icon: 'mdi-link' },
  { label: '悬挂链大数据看板', url: 'http://10.10.180.241:9004/page', icon: 'mdi-link' },
  { label: 'KP1', url: 'http://10.10.180.241:9000/#/Screen', icon: 'mdi-link' },
]

const currentModule = computed(() => route.meta.module || 'machine')

const currentModuleInfo = computed(() => {
  return dashboardModules.find(m => m.id === currentModule.value) || dashboardModules[0]
})

const handleUpdate = () => {}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().then(() => {
      isFullscreen.value = true
    }).catch(() => {})
  } else {
    document.exitFullscreen().then(() => {
      isFullscreen.value = false
    }).catch(() => {})
  }
}

const handleFullscreenChange = () => {
  if (!document.fullscreenElement) {
    isFullscreen.value = false
  }
}

onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  if (document.fullscreenElement) {
    document.exitFullscreen()
  }
})
</script>

<style scoped>
.fullscreen-mode {
  background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 50%, #0a1628 100%);
}
</style>
