import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '上海新泉-ShanghaiXinQuan.Inc', requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '生产看板', requiresAuth: false },
    redirect: { name: 'DashboardOverview' },
    children: [
      {
        path: 'overview',
        name: 'DashboardOverview',
        component: () => import('@/components/dashboards/ProductionOverview.vue'),
        meta: { title: '生产总览', module: 'overview' }
      },
      {
        path: 'machine',
        name: 'DashboardMachine',
        component: () => import('@/components/dashboards/MachineMonitor.vue'),
        meta: { title: '设备监控', module: 'machine' }
      },
      {
        path: 'quality',
        name: 'DashboardQuality',
        component: () => import('@/components/dashboards/QualityAnalysis.vue'),
        meta: { title: '质量分析', module: 'quality' }
      },
      {
        path: 'realtime',
        name: 'DashboardRealtime',
        component: () => import('@/components/dashboards/RealtimeData.vue'),
        meta: { title: '实时数据', module: 'realtime' }
      }
    ]
  },
  {
    path: '/device-detail',
    name: 'DeviceDetail',
    component: () => import('@/components/dashboards/DeviceDetailDashboard.vue'),
    meta: { title: '设备详情', requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { title: '管理后台', requiresAuth: true },
    redirect: { name: 'AdminProcessParams' },
    children: [
      {
        path: 'processparams',
        name: 'AdminProcessParams',
        component: () => import('@/components/admin/ProcessParams.vue'),
        meta: { title: '工艺参数追溯', module: 'processparams' }
      },
      {
        path: 'processingevents',
        name: 'AdminProcessingEvents',
        component: () => import('@/components/admin/ProcessingEvents.vue'),
        meta: { title: '产品加工信息追溯', module: 'processingevents' }
      },
      {
        path: 'materials',
        name: 'AdminMaterials',
        component: () => import('@/components/admin/Materials.vue'),
        meta: { title: '物料管理', module: 'materials' }
      },
      {
        path: 'datacollector',
        name: 'AdminDataCollector',
        component: () => import('@/components/admin/DataCollector.vue'),
        meta: { title: '数据采集管理', module: 'datacollector' }
      },
      {
        path: 'devices',
        name: 'AdminDevices',
        component: () => import('@/components/admin/Devices.vue'),
        meta: { title: '设备管理', module: 'devices' }
      },
      {
        path: 'alarms',
        name: 'AdminAlarms',
        component: () => import('@/components/admin/Alarms.vue'),
        meta: { title: '报警管理', module: 'alarms' }
      },
      {
        path: 'quality',
        name: 'AdminQuality',
        component: () => import('@/components/admin/QualityManagement.vue'),
        meta: { title: '质量管理', module: 'quality' }
      },
      {
        path: 'datacollection',
        name: 'AdminDataCollection',
        component: () => import('@/components/admin/DeviceDataCollection.vue'),
        meta: { title: '数据采集', module: 'datacollection' }
      },
      {
        path: 'workshops',
        name: 'AdminWorkshops',
        component: () => import('@/components/admin/Workshops.vue'),
        meta: { title: '车间管理', module: 'workshops' }
      },
      {
        path: 'projects',
        name: 'AdminProjects',
        component: () => import('@/components/admin/Projects.vue'),
        meta: { title: '项目管理', module: 'projects' }
      },
      {
        path: 'bom',
        name: 'AdminBOM',
        component: () => import('@/components/admin/BOMManagement.vue'),
        meta: { title: 'BOM 管理', module: 'bom' }
      },
      {
        path: 'production-flows',
        name: 'AdminProductionFlows',
        component: () => import('@/components/admin/ProductionFlowManagement.vue'),
        meta: { title: '生产流程管理', module: 'productionflows' }
      },
      {
        path: 'process-definitions',
        name: 'AdminProcessDefinitions',
        component: () => import('@/components/admin/ProcessDefinitionManagement.vue'),
        meta: { title: '工艺管理', module: 'process-definitions' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 访问控制
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    if (to.path === '/') {
      document.title = to.meta.title
    } else if (to.path.startsWith('/dashboard/')) {
      document.title = `${to.meta.title} - 生产看板 - 生产数据管理`
    } else if (to.path.startsWith('/admin/')) {
      document.title = `${to.meta.title} - 管理后台 - 生产数据管理`
    } else {
      document.title = `${to.meta.title} - 生产数据管理`
    }
  }
  
  // 检查是否需要认证
  const requiresAuth = to.meta.requiresAuth !== false
  const token = localStorage.getItem('access_token')
  
  if (requiresAuth && !token) {
    // 需要认证但没有令牌，重定向到登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.path === '/login' && token) {
    // 已登录但访问登录页，重定向到首页
    next({ path: '/' })
  } else {
    next()
  }
})

export default router
