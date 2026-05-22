<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      color="#0a1628"
      theme="dark"
      height="100vh"
      style="position: fixed;"
    >
      <v-list-item
        prepend-icon="mdi-cog"
        title="管理后台"
        nav
      >
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
          v-for="module in adminModules"
          :key="module.id"
          :to="{ name: module.routeName }"
          :prepend-icon="module.icon"
          :title="module.name"
          :active="currentModule === module.id"
          active-color="primary"
          rounded="lg"
        />
      </v-list>

      <template v-slot:append>
        <v-divider />
        <v-list nav density="comfortable">
          <v-list-item
            :to="{ name: 'Dashboard' }"
            prepend-icon="mdi-chart-line"
            title="生产看板"
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

    <v-app-bar color="white" elevation="1">
      <v-app-bar-nav-icon @click="rail = !rail" />
      <v-app-bar-title>{{ pageTitle }}</v-app-bar-title>
      <v-spacer />
      <v-chip prepend-icon="mdi-account-circle" variant="text">
        管理员
      </v-chip>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const drawer = ref(true)
const rail = ref(false)

const adminModules = [
  { id: 'processparams', name: '工艺参数追溯', icon: 'mdi-clipboard-text-search', routeName: 'AdminProcessParams' },
  { id: 'processingevents', name: '产品加工信息追溯', icon: 'mdi-calendar-check', routeName: 'AdminProcessingEvents' },
  { id: 'materials', name: '物料管理', icon: 'mdi-package-variant-closed', routeName: 'AdminMaterials' },
  { id: 'datacollector', name: '数据采集管理', icon: 'mdi-wifi', routeName: 'AdminDataCollector' },
  { id: 'devices', name: '设备管理', icon: 'mdi-cpu-64-bit', routeName: 'AdminDevices' },
  { id: 'alarms', name: '报警管理', icon: 'mdi-bell', routeName: 'AdminAlarms' },
  { id: 'quality', name: '质量管理', icon: 'mdi-clipboard-check', routeName: 'AdminQuality' },
  { id: 'workshops', name: '车间管理', icon: 'mdi-factory', routeName: 'AdminWorkshops' },
  { id: 'projects', name: '项目管理', icon: 'mdi-folder-open', routeName: 'AdminProjects' },
  { id: 'bom', name: 'BOM 管理', icon: 'mdi-file-tree', routeName: 'AdminBOM' },
  { id: 'productionflows', name: '生产流程管理', icon: 'mdi-sitemap', routeName: 'AdminProductionFlows' },
  { id: 'process-definitions', name: '工艺管理', icon: 'mdi-cog-transfer', routeName: 'AdminProcessDefinitions' },
]

const currentModule = computed(() => route.meta.module || 'processparams')

const pageTitle = computed(() => {
  const m = adminModules.find(m => m.id === currentModule.value)
  return m ? m.name : '管理后台'
})
</script>
