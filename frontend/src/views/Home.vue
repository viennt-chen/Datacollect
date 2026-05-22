<template>
  <div class="home-layout" :class="[`theme-${theme}`, `lang-${lang}`]">

    <!-- ────── 顶部导航 ────── -->
    <header class="home-header" :class="{ 'header-scrolled': isScrolled }">
      <div class="header-inner">
        <div class="logo" @click="goToHome" tabindex="0" @keyup.enter="goToHome" role="button" aria-label="返回首页">
          <div class="logo-icon-wrap">
            <i class="mdi-factory"></i>
          </div>
          <span class="logo-text">{{ t('companyName') }}</span>
        </div>

        <!-- 桌面端导航 -->
        <nav class="header-nav desktop-nav" aria-label="主导航">
          <router-link :to="{ name: 'Dashboard' }" class="nav-link" :class="{ active: $route.path.startsWith('/dashboard') }">
            <i class="mdi-speedometer"></i>
            <span>{{ t('dashboard') }}</span>
          </router-link>
          <router-link :to="{ name: 'Admin' }" class="nav-link" v-if="isLoggedIn" :class="{ active: $route.path.startsWith('/admin') }">
            <i class="mdi-view-dashboard"></i>
            <span>{{ t('admin') }}</span>
          </router-link>

          <div class="nav-divider"></div>

          <div class="header-controls">
            <button class="control-btn" @click="toggleLang" :title="t('switchLang')" aria-label="切换语言">
              <span class="lang-badge">{{ lang === 'zh' ? 'CN' : 'EN' }}</span>
            </button>
            <button class="control-btn theme-btn" @click="toggleTheme" :title="t('switchTheme')" aria-label="切换主题">
              <i class="bi" :class="theme === 'dark' ? 'mdi-white-balance-sunny' : 'mdi-weather-night'"></i>
            </button>
          </div>

          <button class="auth-btn login-btn" v-if="!isLoggedIn" @click="debouncedGoToLogin" type="button">
            <i class="mdi-login"></i>
            <span>{{ t('login') }}</span>
          </button>
          <button class="auth-btn logout-btn" v-else @click="debouncedHandleLogout" type="button">
            <span class="user-avatar">
              <i class="mdi-account"></i>
            </span>
            <span>{{ t('logout') }}</span>
          </button>
        </nav>

        <!-- 移动端右侧 -->
        <div class="mobile-actions">
          <button class="control-btn" @click="toggleLang" aria-label="切换语言">
            <span class="lang-badge">{{ lang === 'zh' ? 'CN' : 'EN' }}</span>
          </button>
          <button class="control-btn theme-btn" @click="toggleTheme" aria-label="切换主题">
            <i class="bi" :class="theme === 'dark' ? 'mdi-white-balance-sunny' : 'mdi-weather-night'"></i>
          </button>
          <button class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen" :aria-expanded="mobileMenuOpen" aria-label="菜单">
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>

      <!-- 移动端菜单 -->
      <Transition name="mobile-menu">
        <div class="mobile-menu" v-if="mobileMenuOpen" @click.self="mobileMenuOpen = false">
          <router-link :to="{ name: 'Dashboard' }" class="mobile-nav-link" @click="mobileMenuOpen = false">
            <i class="mdi-speedometer"></i> {{ t('dashboard') }}
          </router-link>
          <router-link :to="{ name: 'Admin' }" class="mobile-nav-link" v-if="isLoggedIn" @click="mobileMenuOpen = false">
            <i class="mdi-view-dashboard"></i> {{ t('admin') }}
          </router-link>
          <button class="mobile-auth-btn" v-if="!isLoggedIn" @click="() => { debouncedGoToLogin(); mobileMenuOpen = false }" type="button">
            <i class="mdi-login"></i> {{ t('login') }}
          </button>
          <button class="mobile-auth-btn mobile-auth-btn--logout" v-else @click="() => { debouncedHandleLogout(); mobileMenuOpen = false }" type="button">
            <i class="mdi-logout"></i> {{ t('logout') }}
          </button>
        </div>
      </Transition>
    </header>

    <!-- ────── Hero 区 ────── -->
    <section class="hero-section" aria-labelledby="hero-title">
      <div class="hero-mesh"></div>
      
      <!-- ✨ 动效模块1: 粒子流场背景 -->
      <canvas ref="particleCanvasRef" class="hero-particle-canvas" aria-hidden="true"></canvas>
      
      <div class="hero-orb hero-orb--1"></div>
      <div class="hero-orb hero-orb--2"></div>

      <div class="hero-content">
        <div class="hero-eyebrow">
          <span class="eyebrow-dot"></span>
          <span>{{ t('eyebrow') }}</span>
          <span class="eyebrow-line"></span>
        </div>

        <h1 class="hero-title" id="hero-title">
          <span class="hero-title-main">{{ t('heroTitle1') }}</span>
          <span class="hero-title-accent">{{ t('heroTitle2') }}</span>
        </h1>

        <p class="hero-subtitle">{{ t('subtitle') }}</p>

        <div class="hero-cta">
          <router-link :to="{ name: 'Dashboard' }" class="cta-primary" @click="trackClick('dashboard')">
            <i class="mdi-speedometer"></i>
            <span>{{ t('dashboard') }}</span>
            <i class="mdi-arrow-right cta-arrow"></i>
          </router-link>

          <router-link :to="{ name: 'Admin' }" class="cta-secondary" v-if="isLoggedIn" @click="trackClick('admin')">
            <i class="mdi-view-dashboard"></i>
            <span>{{ t('admin') }}</span>
          </router-link>
          <button class="cta-secondary" v-else @click="debouncedGoToLogin" type="button">
            <i class="mdi-login"></i>
            <span>{{ t('enterSystem') }}</span>
          </button>
        </div>

        <!-- 实时数据条 -->
        <div class="hero-stats-bar" aria-label="实时数据概览">
          <template v-if="statsLoaded">
            <div class="hstat">
              <i class="mdi-cpu-64-bit"></i>
              <span class="hstat-num" data-count="stats.devices">{{ stats.devices }}</span>
              <span class="hstat-label">{{ t('stats.devices') }}</span>
            </div>
            <div class="hstat-sep"></div>
            <div class="hstat">
              <i class="mdi-package-variant-closed"></i>
              <span class="hstat-num" data-count="stats.todayProduction">{{ stats.todayProduction.toLocaleString() }}</span>
              <span class="hstat-label">{{ t('stats.todayProduction') }}</span>
            </div>
            <div class="hstat-sep"></div>
            <div class="hstat">
              <i class="mdi-check-circle"></i>
              <span class="hstat-num" data-count="stats.qualityRate">{{ stats.qualityRate }}%</span>
              <span class="hstat-label">{{ t('stats.qualityRate') }}</span>
            </div>
            <div class="hstat-sep"></div>
            <div class="hstat">
              <i class="mdi-bell hstat-alarm"></i>
              <span class="hstat-num" data-count="stats.alarms">{{ stats.alarms }}</span>
              <span class="hstat-label">{{ t('stats.alarms') }}</span>
            </div>
          </template>
          <template v-else>
            <div v-for="i in 4" :key="i" class="hstat-skeleton"></div>
          </template>
        </div>
      </div>

      <!-- ✨ 动效模块4+2+5: 节点网络可视化面板 (替换原浮动卡片) -->
      <div class="hero-visual" aria-hidden="true">
        <!-- 节点网络主面板 -->
        <div class="vis-card vis-card--main">
          <div class="vis-card-header">
            <span class="vis-dot green"></span>
            <span class="vis-dot yellow"></span>
            <span class="vis-dot red"></span>
            <span class="vis-title">{{ t('features.realtime') }}</span>
          </div>
          <!-- ✨ 动效模块2: Canvas 波形图 (替换原柱状图) -->
          <div class="vis-chart vis-chart--wave">
            <canvas ref="waveCanvasRef" class="wave-canvas"></canvas>
          </div>
          <div class="vis-footer">
            <span class="vis-status-dot"></span>
            <span>Live · {{ liveDataPoints }} pts</span>
          </div>
        </div>

        <!-- 浮动网络芯片 -->
        <div class="floating-chip chip-1 chip--network">
          <div class="chip-dot chip-dot--blue"></div>
          <div>
            <div style="font-size:11px;font-weight:700;color:var(--c-text-1)">12</div>
            <div style="font-size:10px;color:var(--c-text-3)">{{ t('stats.devices') }}</div>
          </div>
        </div>
        <div class="floating-chip chip-2">
          <i class="mdi-clipboard-text"></i>
          <span>{{ t('features.quality') }}</span>
        </div>
        <!-- ✨ 动效模块5: 迷你雷达扫描 -->
        <div class="floating-chip chip-3 chip--radar">
          <canvas ref="radarMiniRef" class="radar-mini"></canvas>
          <span>{{ t('features.realtime') }}</span>
        </div>
      </div>
    </section>

    <!-- ✨ 动效模块3: 生产线传送带条幅 (插入在 features 之前) -->
    <div class="pipeline-strip" aria-label="生产线动态展示" aria-hidden="true">
      <canvas ref="pipelineCanvasRef" class="pipeline-canvas"></canvas>
      <div class="pipeline-label">
        <span class="pipeline-live-dot"></span>
        <span>{{ t('features.machine') }} · Real-time</span>
      </div>
    </div>

    <!-- ────── 功能卡片区 ────── -->
    <section class="features-section" aria-labelledby="features-heading">
      <div class="section-header">
        <p class="section-label">{{ t('featuresLabel') }}</p>
        <h2 class="section-title" id="features-heading">{{ t('featuresTitle') }}</h2>
      </div>

      <div class="features-grid" v-if="featuresLoaded">
        <div
          v-for="feature in features"
          :key="feature.id"
          class="feature-card reveal"
          :class="`feature-card--${feature.color}`"
          @click="handleFeatureClick(feature)"
          tabindex="0"
          @keyup.enter="handleFeatureClick(feature)"
          role="button"
          :aria-label="`进入${t('features.' + feature.id)}`"
        >
          <div class="fc-top">
            <div class="fc-icon">
              <i :class="feature.icon"></i>
            </div>
            <span class="fc-badge" v-if="feature.new">NEW</span>
          </div>
          <h3 class="fc-title">{{ t(`features.${feature.id}`) }}</h3>
          <p class="fc-desc">{{ t(`featureDesc.${feature.id}`) }}</p>
          <div class="fc-action">
            <span>{{ feature.type === 'dashboard' ? t('viewDashboard') : t('enterAdmin') }}</span>
            <i class="mdi-arrow-right"></i>
          </div>
          <div class="fc-glow"></div>
        </div>
      </div>

      <div class="features-grid" v-else aria-busy="true" aria-label="加载中">
        <div v-for="i in 6" :key="i" class="feature-card feature-card--skeleton">
          <div class="sk-icon"></div>
          <div class="sk-line sk-line--title"></div>
          <div class="sk-line sk-line--desc"></div>
          <div class="sk-line sk-line--action"></div>
        </div>
      </div>
    </section>

    <!-- ────── 数据统计区 ────── -->
    <section class="stats-section" aria-labelledby="stats-heading">
      <div class="stats-inner">
        <div class="section-header section-header--center">
          <p class="section-label">{{ t('statsLabel') }}</p>
          <h2 class="section-title" id="stats-heading">{{ t('statsTitle') }}</h2>
        </div>

        <div class="stats-grid">
          <div v-for="(stat, key) in stats" :key="key" class="stat-card reveal">
            <div class="stat-icon-wrap" :class="`stat-icon--${key}`">
              <i :class="getStatIcon(key)"></i>
            </div>
            <div class="stat-body">
              <div class="stat-value" v-if="statsLoaded">{{ formatStatValue(key, stat) }}</div>
              <div class="stat-value stat-value--loading" v-else></div>
              <div class="stat-name">{{ t(`stats.${key}`) }}</div>
            </div>
            <div class="stat-trend" v-if="getStatTrend(key)">
              <i :class="getStatTrend(key).icon"></i>
              <span :class="getStatTrend(key).cls">{{ getStatTrend(key).value }}</span>
            </div>
          </div>
        </div>

        <p class="stats-update-time" v-if="statsLoaded">
          <i class="mdi-refresh"></i> {{ t('updatedAt') }} {{ lastUpdateTime }}
        </p>
      </div>
    </section>

    <!-- ────── 页脚 ────── -->
    <footer class="home-footer" role="contentinfo">
      <div class="footer-inner">
        <div class="footer-brand">
          <i class="mdi-factory"></i>
          <span>{{ t('companyName') }}</span>
        </div>
        <nav class="footer-links" aria-label="页脚导航">
          <a href="#" v-for="(link, i) in t('footerLinks')" :key="i">{{ link }}</a>
        </nav>
        <p class="copyright">&copy; {{ currentYear }} {{ t('copyright') }}</p>
        <div class="footer-meta">
          <span>{{ t('version') }} v2.0.0</span>
          <span>{{ t('updateTime') }} {{ lastUpdateTime }}</span>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'

const router = useRouter()
const route = useRoute()

const isScrolled = ref(false)
const isLoggedIn = ref(false)
const statsLoaded = ref(false)
const featuresLoaded = ref(false)
const mobileMenuOpen = ref(false)
const currentYear = ref(new Date().getFullYear())
const lastUpdateTime = ref('')
const theme = ref('light')
const lang = ref('zh')

// ── Canvas Refs for 动效模块 ─────────────────────
const particleCanvasRef = ref<HTMLCanvasElement | null>(null)
const waveCanvasRef     = ref<HTMLCanvasElement | null>(null)
const pipelineCanvasRef = ref<HTMLCanvasElement | null>(null)
const radarMiniRef      = ref<HTMLCanvasElement | null>(null)
const liveDataPoints    = ref(2048)

// ── RAF 句柄管理 (用于清理) ──────────────────────
const rafHandles: number[] = []
const cancelAll = () => {
  rafHandles.forEach(id => cancelAnimationFrame(id))
  rafHandles.length = 0
}

// 伪数据 - 图表柱
const chartBars = ref([55, 72, 48, 88, 63, 95, 71, 84, 60, 78, 90, 65])

// ──────────────────────────────
// 国际化
// ──────────────────────────────
const translations = {
  zh: {
    companyName: '上海新泉 XinQuan.Inc',
    eyebrow: '智能工厂数字化解决方案',
    heroTitle1: '智能生产',
    heroTitle2: '数据管理平台',
    dashboard: '生产看板', admin: '管理后台', login: '登录', logout: '退出',
    subtitle: '实时监控设备运行状态，智能分析生产数据，全面管控产品质量',
    enterSystem: '进入系统',
   
    featuresTitle: '生产数据管理',
    statsLabel: '实时数据',
    statsTitle: '生产概况一览',
    features: { overview: '生产总览', machine: '设备监控', quality: '质量分析', realtime: '实时数据', data: '数据管理', alarm: '报警管理' },
    featureDesc: {
      overview: '全面展示生产进度、产量统计和设备运行状态，掌握全局动态。',
      machine: '实时监控设备运行参数、状态和报警信息，保障设备稳定运行。',
      quality: '产品质量趋势分析、缺陷统计和质量管控，提升产品合格率。',
      realtime: '实时采集和展示设备传感器数据流，毫秒级响应数据变化。',
      data: '产品、设备、工艺参数等基础数据管理，构建数据资产。',
      alarm: '设备报警记录查询、报警规则配置，快速响应异常事件。'
    },
    viewDashboard: '查看看板', enterAdmin: '进入管理',
    stats: { devices: '在线设备', todayProduction: '今日产量', qualityRate: '合格率', alarms: '待处理报警' },
    updatedAt: '更新于',
    footerLinks: ['关于我们', '服务条款', '隐私政策', '联系我们'],
    copyright: '上海新泉 · 数据采集与监控平台',
    version: '版本', updateTime: '更新时间',
    switchLang: '切换语言', switchTheme: '切换主题'
  },
  en: {
    companyName: 'Shanghai XinQuan Inc.',
    eyebrow: 'Smart Factory Digital Solution',
    heroTitle1: 'Intelligent Production',
    heroTitle2: 'Data Platform',
    dashboard: 'Dashboard', admin: 'Admin', login: 'Login', logout: 'Logout',
    subtitle: 'Monitor equipment in real-time, analyze production data intelligently, and control product quality comprehensively.',
    enterSystem: 'Enter System',
    featuresLabel: 'Core Features',
    featuresTitle: 'All-in-One Production Management',
    statsLabel: 'Live Data',
    statsTitle: 'Production Overview',
    features: { overview: 'Production Overview', machine: 'Device Monitor', quality: 'Quality Analysis', realtime: 'Real-time Data', data: 'Data Management', alarm: 'Alarm Management' },
    featureDesc: {
      overview: 'Comprehensive production progress, yield statistics, and equipment status.',
      machine: 'Real-time monitoring of equipment parameters, status, and alarms.',
      quality: 'Product quality trend analysis, defect statistics, and quality control.',
      realtime: 'Real-time collection and display of equipment sensor data streams.',
      data: 'Basic data management for products, equipment, and process parameters.',
      alarm: 'Equipment alarm record query and alarm rule configuration.'
    },
    viewDashboard: 'View Dashboard', enterAdmin: 'Go to Admin',
    stats: { devices: 'Online Devices', todayProduction: "Today's Output", qualityRate: 'Quality Rate', alarms: 'Pending Alarms' },
    updatedAt: 'Updated at',
    footerLinks: ['About Us', 'Terms of Service', 'Privacy Policy', 'Contact Us'],
    copyright: 'Shanghai XinQuan · Data Acquisition & Monitoring',
    version: 'Version', updateTime: 'Last Updated',
    switchLang: 'Switch Language', switchTheme: 'Toggle Theme'
  }
}

const t = (key: string) => {
  const dict = translations[lang.value] || translations.zh
  const val = key.split('.').reduce((o: any, k: string) => (o && o[k] !== undefined ? o[k] : undefined), dict)
  return val !== undefined ? val : key
}

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('theme', theme.value)
  document.documentElement.setAttribute('data-theme', theme.value)
}

const toggleLang = () => {
  lang.value = lang.value === 'zh' ? 'en' : 'zh'
  localStorage.setItem('lang', lang.value)
}

// ──────────────────────────────
// 功能特性数据
// ──────────────────────────────
const features = ref([
  { id: 'overview', icon: 'mdi-speedometer',    color: 'blue',   type: 'dashboard', new: false },
  { id: 'machine',  icon: 'mdi-cog', color: 'green',  type: 'dashboard', new: false },
  { id: 'quality',  icon: 'mdi-clipboard-text',   color: 'purple', type: 'dashboard', new: true  },
  { id: 'realtime', icon: 'mdi-heart-pulse',         color: 'orange', type: 'dashboard', new: false },
  { id: 'data',     icon: 'mdi-database-cog',    color: 'teal',   type: 'admin',     new: false },
  { id: 'alarm',    icon: 'mdi-bell',        color: 'red',    type: 'admin',     new: false },
])

const stats = ref({ devices: 0, todayProduction: 0, qualityRate: 0, alarms: 0 })

// ──────────────────────────────
// 辅助方法
// ──────────────────────────────
const handleScroll = () => { isScrolled.value = window.scrollY > 60 }
const checkLoginStatus = () => { isLoggedIn.value = !!localStorage.getItem('access_token') }
const goToHome = () => router.push('/')
const goToLogin = () => router.push({ path: '/login', query: { redirect: route.fullPath } })
const handleLogout = () => { localStorage.removeItem('access_token'); isLoggedIn.value = false; router.push('/login') }
const debouncedGoToLogin = useDebounceFn(goToLogin, 300)
const debouncedHandleLogout = useDebounceFn(handleLogout, 300)
const goToDashboard = (module: string) => router.push({ name: `Dashboard${module.charAt(0).toUpperCase() + module.slice(1)}` })
const goToAdmin = (module?: string) => {
  if (!isLoggedIn.value) {
    router.push({ path: '/login', query: { redirect: '/admin' } })
  } else if (module) {
    router.push({ name: `Admin${module.charAt(0).toUpperCase() + module.slice(1)}` })
  } else {
    router.push({ name: 'Admin' })
  }
}
const handleFeatureClick = (f: any) => f.type === 'dashboard' ? goToDashboard(f.id) : goToAdmin()
const trackClick = (a: string) => console.log('Track:', a)

const getStatIcon = (key: string) => ({ 
  devices: 'mdi-cpu-64-bit', 
  todayProduction: 'mdi-package-variant-closed', 
  qualityRate: 'mdi-check-circle', 
  alarms: 'mdi-bell' 
}[key] || 'mdi-information')

const formatStatValue = (key: string, value: number) => key === 'qualityRate' ? `${value}%` : value.toLocaleString()

const getStatTrend = (key: string) => ({
  devices:         { icon: 'mdi-arrow-up',   value: '+2',    cls: 'trend-up'   },
  todayProduction: { icon: 'mdi-arrow-up',   value: '+15%',  cls: 'trend-up'   },
  qualityRate:     { icon: 'mdi-arrow-up',   value: '+0.5%', cls: 'trend-up'   },
  alarms:          { icon: 'mdi-arrow-down', value: '-1',    cls: 'trend-down' },
}[key] as { icon: string; value: string; cls: string } | undefined)

const loadStats = async () => {
  try {
    await new Promise(r => setTimeout(r, 900))
    stats.value = { devices: 12, todayProduction: 15680, qualityRate: 98.5, alarms: 3 }
  } finally {
    statsLoaded.value = true
    lastUpdateTime.value = new Date().toLocaleTimeString(lang.value === 'zh' ? 'zh-CN' : 'en-US')
  }
}

// ════════════════════════════════════════════════
// ✨ 动效模块 1: 粒子流场 (Hero 背景)
// ════════════════════════════════════════════════
function initParticles(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext('2d')!
  let W = 0, H = 0, raf = 0

  interface Particle {
    x: number; y: number; vx: number; vy: number
    r: number; life: number; maxLife: number; hue: number
  }
  let particles: Particle[] = []

  function resize() {
    const rect = canvas.parentElement?.getBoundingClientRect()
    if (!rect) return
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    W = rect.width; H = rect.height
    canvas.width = W * dpr
    canvas.height = H * dpr
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  function spawn(): Particle {
    return {
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.5, vy: (Math.random() - 0.5) * 0.5,
      r: Math.random() * 1.6 + 0.5,
      life: 0, maxLife: 200 + Math.random() * 150,
      hue: Math.random() < 0.6 ? 213 : 265,
    }
  }

  function boot() {
    resize()
    particles = Array.from({ length: 70 }, () => {
      const p = spawn(); p.life = Math.random() * p.maxLife; return p
    })
  }

  function drawEdges() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const a = particles[i], b = particles[j]
        const d = Math.hypot(a.x - b.x, a.y - b.y)
        if (d < 100) {
          const alpha = (1 - d / 100) * 0.15 *
            (a.life / a.maxLife) * (b.life / b.maxLife)
          ctx.strokeStyle = `hsla(213,80%,65%,${alpha})`
          ctx.lineWidth = 0.5
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke()
        }
      }
    }
  }

  function tick() {
    ctx.clearRect(0, 0, W, H)
    drawEdges()
    particles.forEach((p, i) => {
      p.x += p.vx; p.y += p.vy; p.life++
      if (p.x < 0 || p.x > W) p.vx *= -1
      if (p.y < 0 || p.y > H) p.vy *= -1
      if (p.life > p.maxLife) { particles[i] = spawn(); return }
      const t2 = Math.sin(p.life / p.maxLife * Math.PI)
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fillStyle = `hsla(${p.hue},70%,65%,${t2 * 0.65})`
      ctx.fill()
    })
    raf = requestAnimationFrame(tick)
    rafHandles.push(raf)
  }

  boot(); tick()
  window.addEventListener('resize', boot)
  return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', boot) }
}

// ════════════════════════════════════════════════
// ✨ 动效模块 2: 实时传感器波形
// ════════════════════════════════════════════════
function initWaveform(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext('2d')!
  let W = 0, H = 0, t2 = 0, raf = 0
  let dataCount = 2048

  function resize() {
    const rect = canvas.parentElement?.getBoundingClientRect()
    if (!rect) return
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    W = rect.width; H = rect.height
    canvas.width = W * dpr; canvas.height = H * dpr
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  function tick() {
    ctx.clearRect(0, 0, W, H)
    t2 += 0.05
    dataCount += Math.floor(Math.random() * 3)
    liveDataPoints.value = dataCount

    // 主波形
    ctx.beginPath()
    for (let x = 0; x <= W; x += 2) {
      const phase = (x / W) * Math.PI * 7
      const noise = Math.sin(phase * 2.4 + t2 * 1.9) * 0.18
      const y = H / 2 + Math.sin(phase + t2) * (H * 0.28) +
                Math.sin(phase * 1.7 + t2 * 0.8) * (H * 0.1) + noise * 5
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.strokeStyle = 'var(--c-primary, #2563eb)'
    ctx.lineWidth = 1.5
    ctx.stroke()

    // 填充
    ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath()
    ctx.fillStyle = 'rgba(37,99,235,0.06)'
    ctx.fill()

    // 辅助波
    ctx.beginPath()
    for (let x = 0; x <= W; x += 2) {
      const phase = (x / W) * Math.PI * 7
      const y = H / 2 + Math.sin(phase + t2 + 1.3) * (H * 0.14) +
                Math.sin(phase * 2 + t2 * 1.4) * (H * 0.06)
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.strokeStyle = 'rgba(124,58,237,0.4)'
    ctx.lineWidth = 0.8
    ctx.stroke()

    raf = requestAnimationFrame(tick)
  }
  resize(); tick()
  window.addEventListener('resize', resize)
  return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize) }
}

// ════════════════════════════════════════════════
// ✨ 动效模块 3: 生产线传送带
// ════════════════════════════════════════════════
function initPipeline(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext('2d')!
  let W = 0, H = 0, beltOffset = 0, raf = 0

  interface Item { x: number; y: number; w: number; h: number; color: string; label: string; speed: number }
  let items: Item[] = []

  const COLORS = ['#2563eb', '#7c3aed', '#059669', '#d97706', '#dc2626']
  const LABELS = lang.value === 'zh'
    ? ['产品A', '产品B', '产品C', '产品D', 'OK']
    : ['Prod-A', 'Prod-B', 'Prod-C', 'Prod-D', 'OK']

  function spawnItem(x: number): Item {
    const ci = Math.floor(Math.random() * COLORS.length)
    return { x, y: 0, w: 50, h: 30, color: COLORS[ci], label: LABELS[ci], speed: 1.4 + Math.random() * 0.6 }
  }

  function resize() {
    const rect = canvas.parentElement?.getBoundingClientRect()
    if (!rect) return
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    W = rect.width; H = rect.height
    canvas.width = W * dpr; canvas.height = H * dpr
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    items = []
    let sx = -60
    while (sx < W + 80) { items.push(spawnItem(sx)); sx += 90 + Math.random() * 40 }
    items.forEach(it => it.y = H / 2)
  }

  function tick() {
    ctx.clearRect(0, 0, W, H)
    beltOffset = (beltOffset + 1.5) % 20

    // 轨道
    ctx.fillStyle = 'rgba(148,163,184,0.1)'
    ctx.fillRect(0, H / 2 - 22, W, 44)
    ctx.strokeStyle = 'rgba(148,163,184,0.18)'
    ctx.lineWidth = 0.5
    ctx.setLineDash([10, 10])
    ctx.lineDashOffset = -beltOffset * 1.8
    ctx.beginPath(); ctx.moveTo(0, H / 2 - 15); ctx.lineTo(W, H / 2 - 15); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(0, H / 2 + 15); ctx.lineTo(W, H / 2 + 15); ctx.stroke()
    ctx.setLineDash([])

    // 滚轮
    for (let x = -20 + beltOffset; x < W + 20; x += 20) {
      ctx.beginPath(); ctx.arc(x, H / 2, 16, 0, Math.PI * 2)
      ctx.strokeStyle = 'rgba(148,163,184,0.15)'
      ctx.lineWidth = 0.5
      ctx.stroke()
    }

    // 产品块 + 扫描线
    items.forEach((it, i) => {
      it.x += it.speed
      if (it.x > W + 80) items[i] = { ...spawnItem(-80), y: H / 2 }
      const bx = it.x - it.w / 2, by = it.y - it.h / 2

      ctx.fillStyle = it.color + '22'
      ctx.strokeStyle = it.color
      ctx.lineWidth = 1
      ctx.beginPath()
      if ((ctx as any).roundRect) (ctx as any).roundRect(bx, by, it.w, it.h, 4)
      else ctx.rect(bx, by, it.w, it.h)
      ctx.fill(); ctx.stroke()

      // 扫描光柱
      const scanX = bx + ((Date.now() / 6) % it.w)
      ctx.strokeStyle = it.color + 'BB'
      ctx.lineWidth = 1.5
      ctx.beginPath(); ctx.moveTo(scanX, by + 2); ctx.lineTo(scanX, by + it.h - 2); ctx.stroke()

      ctx.fillStyle = it.color
      ctx.font = 'bold 9px system-ui'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(it.label, it.x, it.y)
    })

    raf = requestAnimationFrame(tick)
  }
  resize(); tick()
  window.addEventListener('resize', resize)
  return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize) }
}

// ════════════════════════════════════════════════
// ✨ 动效模块 5: 迷你雷达扫描 (Hero 浮动芯片内)
// ════════════════════════════════════════════════
function initRadarMini(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext('2d')!
  let angle = 0, raf = 0
  const SIZE = 40
  canvas.width = SIZE * 2; canvas.height = SIZE * 2
  ctx.scale(2, 2)
  const cx = SIZE / 2, cy = SIZE / 2, R = SIZE / 2 - 3

  const blips = [
    { a: 0.9, r: 0.6, fade: 0 },
    { a: 2.5, r: 0.4, fade: 0 },
    { a: 4.2, r: 0.7, fade: 0 },
  ]

  function tick() {
    ctx.clearRect(0, 0, SIZE, SIZE)
    ;[1, 0.65, 0.33].forEach(f => {
      ctx.beginPath(); ctx.arc(cx, cy, R * f, 0, Math.PI * 2)
      ctx.strokeStyle = 'rgba(37,99,235,0.2)'
      ctx.lineWidth = 0.5; ctx.stroke()
    })
    ;[0, 1].forEach(d => {
      ctx.beginPath()
      ctx.moveTo(cx - d * R, cy - (1 - d) * R)
      ctx.lineTo(cx + d * R, cy + (1 - d) * R)
      ctx.strokeStyle = 'rgba(37,99,235,0.15)'
      ctx.lineWidth = 0.5; ctx.stroke()
    })

    angle = (angle + 0.04) % (Math.PI * 2)

    // 扫描弧
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.arc(cx, cy, R, angle - Math.PI * 0.3, angle)
    ctx.closePath()
    ctx.fillStyle = 'rgba(37,99,235,0.12)'; ctx.fill()
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + Math.cos(angle) * R, cy + Math.sin(angle) * R)
    ctx.strokeStyle = 'rgba(37,99,235,0.7)'; ctx.lineWidth = 1; ctx.stroke()

    blips.forEach(b => {
      const da = ((angle - b.a) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2)
      if (da < 0.07) b.fade = 1
      if (b.fade > 0) {
        b.fade -= 0.006
        const bx = cx + Math.cos(b.a) * R * b.r
        const by = cy + Math.sin(b.a) * R * b.r
        ctx.beginPath(); ctx.arc(bx, by, 2.5, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(239,68,68,${b.fade})`; ctx.fill()
        ctx.beginPath(); ctx.arc(bx, by, 5, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(239,68,68,${b.fade * 0.25})`; ctx.fill()
      }
    })

    raf = requestAnimationFrame(tick)
  }
  tick()
  return () => cancelAnimationFrame(raf)
}

// ════════════════════════════════════════════════
// ✨ 动效模块 6: 统计数字滚动计数器
// ════════════════════════════════════════════════
function animateCounter(
  el: HTMLElement,
  from: number,
  to: number,
  duration = 1200,
  suffix = ''
) {
  const start = performance.now()
  function step(now: number) {
    const p = Math.min((now - start) / duration, 1)
    const ease = 1 - Math.pow(1 - p, 3) // cubic ease-out
    const val = Math.round(from + (to - from) * ease)
    el.textContent = val.toLocaleString() + suffix
    if (p < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

// ════════════════════════════════════════════════
// 滚动可见性动画 (Intersection Observer)
// ════════════════════════════════════════════════
function initScrollReveal() {
  if (typeof window === 'undefined') return
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
        observer.unobserve(entry.target)
      }
    })
  }, { threshold: 0.1 })
  
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
  return () => observer.disconnect()
}

// ──────────────────────────────
// 生命周期
// ──────────────────────────────
onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  const savedLang = localStorage.getItem('lang') || 'zh'
  theme.value = savedTheme
  lang.value = savedLang
  document.documentElement.setAttribute('data-theme', theme.value)

  checkLoginStatus()
  window.addEventListener('scroll', handleScroll, { passive: true })
  loadStats()
  setTimeout(() => featuresLoaded.value = true, 400)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && !statsLoaded.value) loadStats()
  })

  // ✅ 初始化所有动效模块 (nextTick 确保 DOM 就绪)
  nextTick(() => {
    // 检测移动端降级
    const isMobile = window.innerWidth < 768
    
    if (particleCanvasRef.value && !isMobile) {
      const cleanup = initParticles(particleCanvasRef.value)
      if (typeof cleanup === 'function') {
        // 存储清理函数供卸载时调用
        ;(onBeforeUnmount as any)(cleanup)
      }
    }
    if (waveCanvasRef.value) initWaveform(waveCanvasRef.value)
    if (pipelineCanvasRef.value && !isMobile) initPipeline(pipelineCanvasRef.value)
    if (radarMiniRef.value) initRadarMini(radarMiniRef.value)
    
    // ✅ 启动数字滚动动画
    document.querySelectorAll('.stat-value:not(.stat-value--loading), .hstat-num').forEach(el => {
      const text = el.textContent || ''
      const hasPercent = text.includes('%')
      const numStr = text.replace(/[^0-9.]/g, '')
      const target = parseFloat(numStr) || 0
      animateCounter(el as HTMLElement, 0, target, 1500, hasPercent ? '%' : '')
    })
    
    // ✅ 启动滚动可见性动画
    initScrollReveal()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  cancelAll() // ✅ 清理所有 RAF 动画帧
})

watch(() => route.path, () => { checkLoginStatus(); mobileMenuOpen.value = false })
</script>

<style>
/* ── 字体 ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── 亮色主题 ────────────────────────────────────── */
:root, [data-theme="light"] {
  --c-primary:      #2563eb;
  --c-primary-h:    #1d4ed8;
  --c-primary-s:    #dbeafe;
  --c-accent:       #7c3aed;
  --c-success:      #059669;
  --c-warning:      #d97706;
  --c-danger:       #dc2626;

  --c-bg:           #f8faff;
  --c-surface:      #ffffff;
  --c-surface-2:    #f1f5fb;
  --c-border:       #e2e8f0;
  --c-border-s:     rgba(0,0,0,0.06);

  --c-text-1:       #0f172a;
  --c-text-2:       #475569;
  --c-text-3:       #94a3b8;

  --c-glass:        rgba(255,255,255,0.82);
  --c-glass-border: rgba(255,255,255,0.9);

  --shadow-1: 0 1px 4px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.05);
  --shadow-2: 0 4px 24px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04);
  --shadow-3: 0 12px 48px rgba(0,0,0,0.12), 0 4px 16px rgba(0,0,0,0.06);
  --shadow-primary: 0 8px 24px rgba(37,99,235,0.28);

  --r-sm: 8px;
  --r-md: 12px;
  --r-lg: 18px;
  --r-xl: 24px;
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  --transition: 0.22s var(--ease);

  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
  line-height: 1.6;
}

/* ── 暗色主题 ────────────────────────────────────── */
[data-theme="dark"] {
  --c-primary:      #60a5fa;
  --c-primary-h:    #93c5fd;
  --c-primary-s:    #1e3a5f;
  --c-accent:       #a78bfa;
  --c-success:      #34d399;
  --c-warning:      #fbbf24;
  --c-danger:       #f87171;

  --c-bg:           #090e1a;
  --c-surface:      #121929;
  --c-surface-2:    #1a2438;
  --c-border:       rgba(255,255,255,0.08);
  --c-border-s:     rgba(255,255,255,0.06);

  --c-text-1:       #f1f5f9;
  --c-text-2:       #94a3b8;
  --c-text-3:       #475569;

  --c-glass:        rgba(18,25,41,0.85);
  --c-glass-border: rgba(255,255,255,0.1);

  --shadow-1: 0 1px 4px rgba(0,0,0,0.4), 0 4px 16px rgba(0,0,0,0.3);
  --shadow-2: 0 4px 24px rgba(0,0,0,0.5), 0 1px 4px rgba(0,0,0,0.3);
  --shadow-3: 0 12px 48px rgba(0,0,0,0.6), 0 4px 16px rgba(0,0,0,0.4);
  --shadow-primary: 0 8px 24px rgba(96,165,250,0.22);
}

/* ── 基础重置 ────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: var(--c-bg); color: var(--c-text-1); transition: background 0.3s, color 0.3s; -webkit-font-smoothing: antialiased; }
a { text-decoration: none; color: inherit; }
button { font: inherit; cursor: pointer; border: none; background: none; }
img, svg { display: block; max-width: 100%; }
</style>

<style scoped>
/* ── 布局 ──────────────────────────────────────── */
.home-layout {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--c-bg);
  color: var(--c-text-1);
}

/* ════════════════════════════════════════════════
   HEADER
════════════════════════════════════════════════ */
.home-header {
  position: sticky;
  top: 0;
  z-index: 200;
  background: var(--c-glass);
  backdrop-filter: blur(20px) saturate(1.6);
  -webkit-backdrop-filter: blur(20px) saturate(1.6);
  border-bottom: 1px solid var(--c-border);
  transition: var(--transition);
}
.home-header.header-scrolled {
  background: var(--c-surface);
  box-shadow: var(--shadow-1);
}

.header-inner {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 clamp(16px, 4vw, 48px);
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: var(--transition);
  flex-shrink: 0;
}
.logo:hover, .logo:focus-visible { opacity: 0.8; transform: translateX(2px); }
.logo:focus-visible { outline: 2px solid var(--c-primary); outline-offset: 4px; border-radius: var(--r-sm); }
.logo-icon-wrap {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--c-primary), var(--c-accent));
  border-radius: var(--r-sm);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.logo-icon-wrap i { color: #fff; font-size: 18px; }
.logo-text {
  font-size: clamp(14px, 1.4vw, 16px);
  font-weight: 700;
  color: var(--c-text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: min(260px, 30vw);
}

/* 桌面导航 */
.desktop-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}
@media (max-width: 768px) { .desktop-nav { display: none; } }

.nav-link {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 14px;
  border-radius: var(--r-md);
  font-size: 14px; font-weight: 500;
  color: var(--c-text-2);
  transition: var(--transition);
  position: relative;
}
.nav-link:hover { color: var(--c-primary); background: var(--c-primary-s); }
.nav-link.active { color: var(--c-primary); background: var(--c-primary-s); font-weight: 600; }
.nav-link i { font-size: 15px; }

.nav-divider { width: 1px; height: 24px; background: var(--c-border); margin: 0 8px; }

/* 控制按钮 */
.header-controls { display: flex; align-items: center; gap: 4px; }
.control-btn {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px;
  border-radius: var(--r-md);
  color: var(--c-text-2);
  transition: var(--transition);
}
.control-btn:hover { background: var(--c-surface-2); color: var(--c-primary); }
.lang-badge { font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px; }
.theme-btn i { font-size: 16px; }

/* 认证按钮 */
.auth-btn {
  display: flex; align-items: center; gap: 7px;
  padding: 7px 16px; margin-left: 6px;
  border-radius: var(--r-md);
  font-size: 14px; font-weight: 600;
  transition: var(--transition);
}
.auth-btn:focus-visible { outline: 2px solid var(--c-primary); outline-offset: 2px; }
.login-btn { background: var(--c-primary); color: #fff; box-shadow: var(--shadow-primary); }
.login-btn:hover { background: var(--c-primary-h); transform: translateY(-1px); }
.logout-btn { background: var(--c-surface-2); color: var(--c-text-2); border: 1px solid var(--c-border); }
.logout-btn:hover { background: var(--c-border); color: var(--c-text-1); }
.user-avatar { width: 24px; height: 24px; border-radius: 50%; background: var(--c-primary-s); display: flex; align-items: center; justify-content: center; color: var(--c-primary); }
.user-avatar i { font-size: 14px; }

/* 移动端操作区 */
.mobile-actions {
  display: none;
  align-items: center;
  gap: 4px;
}
@media (max-width: 768px) { .mobile-actions { display: flex; } }

.hamburger {
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  width: 34px; height: 34px; gap: 5px; border-radius: var(--r-md);
  transition: var(--transition);
}
.hamburger:hover { background: var(--c-surface-2); }
.hamburger span { display: block; width: 18px; height: 2px; background: var(--c-text-2); border-radius: 2px; transition: var(--transition); }

/* 移动端菜单 */
.mobile-menu {
  border-top: 1px solid var(--c-border);
  background: var(--c-surface);
  padding: 12px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.mobile-menu-enter-active, .mobile-menu-leave-active { transition: all 0.22s var(--ease); overflow: hidden; }
.mobile-menu-enter-from, .mobile-menu-leave-to { opacity: 0; max-height: 0; padding-block: 0; }
.mobile-menu-enter-to, .mobile-menu-leave-from { opacity: 1; max-height: 300px; }

.mobile-nav-link {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 14px;
  border-radius: var(--r-md);
  font-size: 15px; font-weight: 500;
  color: var(--c-text-2);
  transition: var(--transition);
}
.mobile-nav-link:hover, .mobile-nav-link.router-link-active { background: var(--c-primary-s); color: var(--c-primary); }
.mobile-auth-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 14px; margin-top: 4px;
  border-radius: var(--r-md);
  font-size: 15px; font-weight: 600;
  background: var(--c-primary); color: #fff;
  transition: var(--transition);
  width: 100%; text-align: left;
}
.mobile-auth-btn:hover { background: var(--c-primary-h); }
.mobile-auth-btn--logout { background: var(--c-surface-2); color: var(--c-text-2); border: 1px solid var(--c-border); }
.mobile-auth-btn--logout:hover { background: var(--c-border); }

/* ════════════════════════════════════════════════
   HERO
════════════════════════════════════════════════ */
.hero-section {
  position: relative;
  overflow: hidden;
  padding: clamp(64px, 10vw, 120px) clamp(20px, 5vw, 60px) clamp(64px, 10vw, 100px);
  max-width: 1320px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(32px, 6vw, 80px);
}

/* 背景 */
.hero-mesh {
  position: absolute; inset: -20%; z-index: 0;
  background: radial-gradient(ellipse 80% 60% at 60% 40%, color-mix(in srgb, var(--c-primary) 8%, transparent), transparent),
              radial-gradient(ellipse 60% 50% at 20% 80%, color-mix(in srgb, var(--c-accent) 6%, transparent), transparent);
  pointer-events: none;
}

/* ✨ 粒子画布背景 */
.hero-particle-canvas {
  position: absolute;
  inset: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.7;
}

.hero-orb {
  position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; z-index: 0;
  animation: orbFloat 8s ease-in-out infinite;
}
.hero-orb--1 { width: clamp(200px, 30vw, 400px); height: clamp(200px, 30vw, 400px); top: -10%; right: 5%; background: color-mix(in srgb, var(--c-primary) 12%, transparent); animation-delay: 0s; }
.hero-orb--2 { width: clamp(150px, 20vw, 280px); height: clamp(150px, 20vw, 280px); bottom: 0; left: -5%; background: color-mix(in srgb, var(--c-accent) 10%, transparent); animation-delay: 3s; }
@keyframes orbFloat { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(10px, -20px) scale(1.05); } }

/* Hero 内容 */
.hero-content {
  position: relative; z-index: 2;
  max-width: 580px;
  flex: 1 1 auto;
  animation: fadeUp 0.7s var(--ease) both;
}
@keyframes fadeUp { from { opacity:0; transform:translateY(28px); } to { opacity:1; transform:translateY(0); } }

.hero-eyebrow {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 20px;
  font-size: 13px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
  color: var(--c-primary);
}
.eyebrow-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--c-primary); flex-shrink: 0; }
.eyebrow-line { flex: 1; max-width: 48px; height: 1px; background: var(--c-primary); opacity: 0.4; }

.hero-title { margin-bottom: 16px; }
.hero-title-main {
  display: block;
  font-size: clamp(32px, 5vw, 60px);
  font-weight: 800; line-height: 1.12;
  color: var(--c-text-1);
  letter-spacing: -0.02em;
}
.hero-title-accent {
  display: block;
  font-size: clamp(32px, 5vw, 60px);
  font-weight: 800; line-height: 1.12;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, var(--c-primary) 20%, var(--c-accent));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}

.hero-subtitle {
  font-size: clamp(14px, 1.6vw, 17px);
  color: var(--c-text-2);
  line-height: 1.7;
  margin-bottom: 36px;
  max-width: 460px;
}

/* CTA 按钮 */
.hero-cta { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 40px; }

.cta-primary {
  display: inline-flex; align-items: center; gap: 9px;
  padding: clamp(12px, 1.5vw, 15px) clamp(20px, 2.5vw, 28px);
  background: var(--c-primary); color: #fff;
  border-radius: var(--r-md);
  font-size: clamp(14px, 1.3vw, 16px); font-weight: 600;
  box-shadow: var(--shadow-primary);
  transition: var(--transition);
  position: relative; overflow: hidden;
}
.cta-primary::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(255,255,255,0.15), transparent); opacity: 0; transition: opacity 0.2s; }
.cta-primary:hover { background: var(--c-primary-h); transform: translateY(-2px); box-shadow: 0 12px 32px rgba(37,99,235,0.36); }
.cta-primary:hover::before { opacity: 1; }
.cta-primary:focus-visible { outline: 2px solid var(--c-primary); outline-offset: 3px; }
.cta-arrow { transition: transform 0.2s var(--ease); }
.cta-primary:hover .cta-arrow { transform: translateX(4px); }

.cta-secondary {
  display: inline-flex; align-items: center; gap: 9px;
  padding: clamp(12px, 1.5vw, 15px) clamp(20px, 2.5vw, 28px);
  border: 1.5px solid var(--c-border);
  background: var(--c-surface); color: var(--c-text-1);
  border-radius: var(--r-md);
  font-size: clamp(14px, 1.3vw, 16px); font-weight: 600;
  transition: var(--transition);
}
.cta-secondary:hover { border-color: var(--c-primary); color: var(--c-primary); transform: translateY(-2px); box-shadow: var(--shadow-1); }
.cta-secondary:focus-visible { outline: 2px solid var(--c-primary); outline-offset: 3px; }

/* Hero 数据条 */
.hero-stats-bar {
  display: flex; align-items: center; flex-wrap: wrap; gap: 0;
  padding: 16px 20px;
  background: var(--c-glass);
  border: 1px solid var(--c-glass-border);
  border-radius: var(--r-lg);
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-1);
  position: relative; z-index: 2;
}
.hstat {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 16px;
  flex: 1; min-width: 0;
  justify-content: center;
}
.hstat i { font-size: 15px; color: var(--c-primary); flex-shrink: 0; }
.hstat-alarm { color: var(--c-danger) !important; }
.hstat-num { font-size: clamp(16px, 2vw, 20px); font-weight: 700; font-family: 'JetBrains Mono', monospace; color: var(--c-text-1); }
.hstat-label { font-size: 12px; color: var(--c-text-3); white-space: nowrap; }
.hstat-sep { width: 1px; height: 32px; background: var(--c-border); flex-shrink: 0; }
.hstat-skeleton { flex: 1; height: 40px; border-radius: var(--r-sm); background: var(--c-surface-2); animation: shimmer 1.4s infinite; }

/* Hero 可视化面板 */
.hero-visual {
  position: relative;
  width: clamp(280px, 35vw, 440px);
  height: clamp(280px, 35vw, 380px);
  flex-shrink: 0;
  display: none;
  animation: fadeUp 0.7s 0.2s var(--ease) both;
  z-index: 2;
}
@media (min-width: 960px) { .hero-visual { display: block; } }

.vis-card--main {
  position: absolute;
  inset: 0;
  background: var(--c-surface);
  border: 1px solid var(--c-border-s);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow-3);
  padding: 20px;
  display: flex; flex-direction: column; gap: 16px;
  overflow: hidden;
}
.vis-card--main::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--c-primary), var(--c-accent)); }

.vis-card-header { display: flex; align-items: center; gap: 6px; }
.vis-dot { width: 10px; height: 10px; border-radius: 50%; }
.vis-dot.green { background: #22c55e; }
.vis-dot.yellow { background: #eab308; }
.vis-dot.red { background: #ef4444; }
.vis-title { margin-left: auto; font-size: 12px; font-weight: 600; color: var(--c-text-3); text-transform: uppercase; letter-spacing: 0.8px; }

.vis-chart { display: flex; align-items: flex-end; gap: 5px; flex: 1; padding-top: 8px; }
.vis-bar {
  flex: 1; border-radius: 4px 4px 0 0;
  background: linear-gradient(180deg, var(--c-primary), color-mix(in srgb, var(--c-primary) 40%, transparent));
  animation: barGrow 0.8s var(--ease) both;
  min-height: 8px;
}
@keyframes barGrow { from { transform: scaleY(0); transform-origin: bottom; } to { transform: scaleY(1); } }

/* ✨ 波形画布样式 */
.vis-chart--wave { min-height: 100px; position: relative; }
.wave-canvas {
  position: absolute;
  inset: 0;
  width: 100%; height: 100%;
  border-radius: 8px;
}

.vis-footer { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--c-text-3); }
.vis-status-dot { width: 7px; height: 7px; border-radius: 50%; background: #22c55e; animation: blink 1.5s ease-in-out infinite; }
@keyframes blink { 0%,100%{ opacity:1; } 50%{ opacity:0.3; } }

/* 浮动芯片 */
.floating-chip {
  position: absolute;
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  background: var(--c-surface);
  border: 1px solid var(--c-border-s);
  border-radius: var(--r-md);
  box-shadow: var(--shadow-2);
  font-size: 13px; font-weight: 600; color: var(--c-text-1);
  white-space: nowrap;
  animation: chipFloat 4s ease-in-out infinite;
  z-index: 3;
}
.floating-chip i { font-size: 16px; color: var(--c-primary); }
.chip-1 { top: -16px; right: 24px; animation-delay: 0s; }
.chip-2 { bottom: 60px; right: -20px; animation-delay: 1.5s; }
.chip-3 { bottom: -16px; left: 20px; animation-delay: 3s; }
@keyframes chipFloat { 0%,100%{ transform:translateY(0); } 50%{ transform:translateY(-8px); } }

/* ✨ 芯片扩展样式 */
.chip--network { flex-direction: row; align-items: center; gap: 8px; }
.chip-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  animation: chipPulse 2s ease-in-out infinite;
}
.chip-dot--blue { background: var(--c-primary); }
@keyframes chipPulse { 0%,100%{box-shadow:0 0 0 0 rgba(37,99,235,0.4)} 50%{box-shadow:0 0 0 5px rgba(37,99,235,0)} }

/* ✨ 迷你雷达 */
.chip--radar { gap: 8px; align-items: center; }
.radar-mini {
  width: 40px; height: 40px;
  flex-shrink: 0;
  border-radius: 50%;
  opacity: 0.9;
}

/* Hero 全屏响应 */
@media (max-width: 959px) {
  .hero-section { flex-direction: column; text-align: center; gap: 40px; }
  .hero-content { max-width: 100%; }
  .hero-eyebrow { justify-content: center; }
  .hero-subtitle { margin-inline: auto; }
  .hero-cta { justify-content: center; }
  .hero-stats-bar { justify-content: center; }
}
@media (max-width: 480px) {
  .hero-stats-bar { flex-direction: column; gap: 8px; }
  .hstat { width: 100%; justify-content: flex-start; padding: 4px 8px; }
  .hstat-sep { display: none; }
  .hero-cta { flex-direction: column; align-items: stretch; }
  .cta-primary, .cta-secondary { justify-content: center; }
}

/* ════════════════════════════════════════════════
   ✨ 流水线动态条幅
════════════════════════════════════════════════ */
.pipeline-strip {
  position: relative;
  width: 100%;
  height: clamp(64px, 8vw, 88px);
  overflow: hidden;
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
  background: var(--c-surface);
}
.pipeline-canvas {
  position: absolute;
  inset: 0;
  width: 100%; height: 100%;
}
.pipeline-label {
  position: absolute;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: var(--c-text-3);
  background: var(--c-glass);
  backdrop-filter: blur(8px);
  padding: 4px 10px;
  border-radius: 99px;
  border: 1px solid var(--c-border);
}
.pipeline-live-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #22c55e;
  animation: blink 1.4s ease-in-out infinite;
}

/* ════════════════════════════════════════════════
   FEATURES
════════════════════════════════════════════════ */
.features-section {
  padding: clamp(60px, 8vw, 100px) clamp(20px, 5vw, 60px);
  max-width: 1320px;
  margin: 0 auto;
  width: 100%;
}

.section-header { margin-bottom: clamp(32px, 5vw, 52px); }
.section-header--center { text-align: center; }
.section-label {
  font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
  color: var(--c-primary); margin-bottom: 10px;
}
.section-title {
  font-size: clamp(24px, 3.5vw, 38px); font-weight: 800; letter-spacing: -0.02em;
  color: var(--c-text-1); line-height: 1.2;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(16px, 2.5vw, 24px);
}
@media (max-width: 1024px) { .features-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px)  { .features-grid { grid-template-columns: 1fr; } }

/* 功能卡片 */
.feature-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border-s);
  border-radius: var(--r-xl);
  padding: clamp(24px, 3vw, 32px);
  cursor: pointer;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
  display: flex; flex-direction: column; gap: 12px;
}
.feature-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-3); border-color: transparent; }
.feature-card:focus-visible { outline: 2px solid var(--c-primary); outline-offset: 3px; border-radius: var(--r-xl); }

/* 发光效果 */
.fc-glow {
  position: absolute; inset: 0;
  opacity: 0;
  transition: opacity 0.3s;
  border-radius: inherit;
  pointer-events: none;
}
.feature-card:hover .fc-glow { opacity: 1; }
.feature-card--blue .fc-glow   { background: radial-gradient(circle at 30% 0%, color-mix(in srgb, #2563eb 12%, transparent), transparent 60%); }
.feature-card--green .fc-glow  { background: radial-gradient(circle at 30% 0%, color-mix(in srgb, #059669 12%, transparent), transparent 60%); }
.feature-card--purple .fc-glow { background: radial-gradient(circle at 30% 0%, color-mix(in srgb, #7c3aed 12%, transparent), transparent 60%); }
.feature-card--orange .fc-glow { background: radial-gradient(circle at 30% 0%, color-mix(in srgb, #d97706 12%, transparent), transparent 60%); }
.feature-card--teal .fc-glow   { background: radial-gradient(circle at 30% 0%, color-mix(in srgb, #0891b2 12%, transparent), transparent 60%); }
.feature-card--red .fc-glow    { background: radial-gradient(circle at 30% 0%, color-mix(in srgb, #dc2626 12%, transparent), transparent 60%); }

.fc-top { display: flex; justify-content: space-between; align-items: flex-start; }
.fc-icon {
  width: 52px; height: 52px; border-radius: var(--r-md);
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.25s var(--ease);
}
.feature-card:hover .fc-icon { transform: scale(1.08) rotate(-3deg); }
.fc-icon i { font-size: 24px; color: #fff; }

.feature-card--blue   .fc-icon { background: linear-gradient(135deg, #60a5fa, #2563eb); }
.feature-card--green  .fc-icon { background: linear-gradient(135deg, #34d399, #059669); }
.feature-card--purple .fc-icon { background: linear-gradient(135deg, #a78bfa, #7c3aed); }
.feature-card--orange .fc-icon { background: linear-gradient(135deg, #fb923c, #d97706); }
.feature-card--teal   .fc-icon { background: linear-gradient(135deg, #22d3ee, #0891b2); }
.feature-card--red    .fc-icon { background: linear-gradient(135deg, #f87171, #dc2626); }

.fc-badge {
  background: var(--c-danger); color: #fff;
  padding: 3px 9px; border-radius: 99px;
  font-size: 10px; font-weight: 700; letter-spacing: 0.8px;
}

.fc-title { font-size: clamp(15px, 1.5vw, 17px); font-weight: 700; color: var(--c-text-1); transition: color 0.2s; }
.feature-card:hover .fc-title { color: var(--c-primary); }
.fc-desc { font-size: 13px; color: var(--c-text-2); line-height: 1.6; flex: 1; }
.fc-action {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 600; color: var(--c-primary);
  margin-top: 4px;
}
.fc-action i { transition: transform 0.2s var(--ease); }
.feature-card:hover .fc-action i { transform: translateX(4px); }

/* 骨架屏 */
.feature-card--skeleton { cursor: default; pointer-events: none; border-color: transparent; background: var(--c-surface-2); }
.sk-icon { width: 52px; height: 52px; border-radius: var(--r-md); background: var(--c-border); animation: shimmer 1.5s infinite; }
.sk-line { border-radius: 6px; background: var(--c-border); animation: shimmer 1.5s infinite; }
.sk-line--title { height: 18px; width: 55%; margin-top: 4px; }
.sk-line--desc  { height: 13px; width: 100%; margin-top: 8px; }
.sk-line--action{ height: 13px; width: 38%; margin-top: 12px; }

@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
.sk-icon, .sk-line { background-size: 200% 100%; background-image: linear-gradient(90deg, var(--c-surface-2) 25%, var(--c-border) 50%, var(--c-surface-2) 75%); }

/* ════════════════════════════════════════════════
   STATS
════════════════════════════════════════════════ */
.stats-section {
  background: linear-gradient(160deg, color-mix(in srgb, var(--c-primary) 4%, var(--c-bg)), var(--c-bg));
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
  padding: clamp(60px, 8vw, 100px) clamp(20px, 5vw, 60px);
}
[data-theme="dark"] .stats-section { background: linear-gradient(160deg, color-mix(in srgb, var(--c-primary) 6%, var(--c-bg)), var(--c-bg)); }

.stats-inner { max-width: 1320px; margin: 0 auto; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: clamp(16px, 2.5vw, 24px);
}
@media (max-width: 900px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 440px) { .stats-grid { grid-template-columns: 1fr; } }

.stat-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border-s);
  border-radius: var(--r-lg);
  padding: clamp(20px, 3vw, 28px);
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  text-align: center;
  transition: var(--transition);
  position: relative; overflow: hidden;
}
.stat-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-2); border-color: var(--c-primary-s); }

.stat-icon-wrap {
  width: 52px; height: 52px;
  border-radius: var(--r-md);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 4px;
}
.stat-icon-wrap i { font-size: 22px; color: #fff; }
.stat-icon--devices         { background: linear-gradient(135deg, #60a5fa, #2563eb); }
.stat-icon--todayProduction { background: linear-gradient(135deg, #34d399, #059669); }
.stat-icon--qualityRate     { background: linear-gradient(135deg, #a78bfa, #7c3aed); }
.stat-icon--alarms          { background: linear-gradient(135deg, #f87171, #dc2626); }

.stat-value {
  font-size: clamp(28px, 4vw, 42px); font-weight: 800; line-height: 1;
  font-family: 'JetBrains Mono', monospace;
  color: var(--c-text-1);
  letter-spacing: -0.02em;
}
.stat-value--loading { width: 100px; height: 36px; border-radius: 8px; background: var(--c-surface-2); animation: shimmer 1.5s infinite; background-size: 200% 100%; background-image: linear-gradient(90deg, var(--c-surface-2) 25%, var(--c-border) 50%, var(--c-surface-2) 75%); }
.stat-name { font-size: 13px; color: var(--c-text-2); font-weight: 500; }
.stat-trend {
  display: flex; align-items: center; gap: 2px;
  font-size: 13px; font-weight: 700;
  padding: 3px 10px;
  border-radius: 99px;
}
.trend-up   { color: var(--c-success); background: color-mix(in srgb, var(--c-success) 10%, transparent); }
.trend-down { color: var(--c-danger);  background: color-mix(in srgb, var(--c-danger)  10%, transparent); }
.stat-trend i { font-size: 16px; }

.stats-update-time {
  text-align: center; margin-top: 32px;
  font-size: 12px; color: var(--c-text-3);
  display: flex; align-items: center; justify-content: center; gap: 6px;
}
.stats-update-time i { animation: spin 3s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ════════════════════════════════════════════════
   FOOTER
════════════════════════════════════════════════ */
.home-footer {
  margin-top: auto;
  background: var(--c-surface);
  border-top: 1px solid var(--c-border);
  padding: clamp(40px, 5vw, 60px) clamp(20px, 5vw, 60px) clamp(24px, 3vw, 36px);
}
.footer-inner { max-width: 1320px; margin: 0 auto; text-align: center; }
.footer-brand {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  font-size: 17px; font-weight: 700; color: var(--c-text-1); margin-bottom: 24px;
}
.footer-brand i { color: var(--c-primary); font-size: 20px; }
.footer-links { display: flex; justify-content: center; gap: clamp(8px, 2vw, 24px); flex-wrap: wrap; margin-bottom: 24px; }
.footer-links a {
  color: var(--c-text-2); font-size: 13px;
  padding: 5px 10px; border-radius: var(--r-sm);
  transition: var(--transition);
}
.footer-links a:hover { color: var(--c-primary); background: var(--c-primary-s); }
.copyright { color: var(--c-text-3); font-size: 12px; margin-bottom: 8px; }
.footer-meta { display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; }
.footer-meta span { color: var(--c-text-3); font-size: 11px; font-family: 'JetBrains Mono', monospace; }

/* ════════════════════════════════════════════════
   ✨ 滚动可见性动画 & 入场效果
════════════════════════════════════════════════ */
.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s var(--ease), transform 0.6s var(--ease);
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* 功能卡片入场动画 */
.features-grid .feature-card {
  animation: cardEnter 0.5s var(--ease) both;
}
.features-grid .feature-card:nth-child(1) { animation-delay: 0.05s }
.features-grid .feature-card:nth-child(2) { animation-delay: 0.10s }
.features-grid .feature-card:nth-child(3) { animation-delay: 0.15s }
.features-grid .feature-card:nth-child(4) { animation-delay: 0.20s }
.features-grid .feature-card:nth-child(5) { animation-delay: 0.25s }
.features-grid .feature-card:nth-child(6) { animation-delay: 0.30s }
@keyframes cardEnter {
  from { opacity: 0; transform: translateY(20px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)    scale(1);    }
}

/* Stats 卡片入场 */
.stats-grid .stat-card {
  animation: statEnter 0.6s var(--ease) both;
}
.stats-grid .stat-card:nth-child(1) { animation-delay: 0.0s }
.stats-grid .stat-card:nth-child(2) { animation-delay: 0.1s }
.stats-grid .stat-card:nth-child(3) { animation-delay: 0.2s }
.stats-grid .stat-card:nth-child(4) { animation-delay: 0.3s }
@keyframes statEnter {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0);    }
}

/* Hero 内容入场 (错落时序) */
.hero-eyebrow  { animation: fadeUp 0.6s 0.1s var(--ease) both; }
.hero-title    { animation: fadeUp 0.7s 0.2s var(--ease) both; }
.hero-subtitle { animation: fadeUp 0.7s 0.3s var(--ease) both; }
.hero-cta      { animation: fadeUp 0.7s 0.4s var(--ease) both; }
.hero-stats-bar{ animation: fadeUp 0.8s 0.5s var(--ease) both; }

/* ── 辅助动画 ──────────────────────────────── */
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.25; }
}

/* 数据流向线 (伪元素版，用于卡片装饰) */
.feature-card::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255,255,255,0.06),
    transparent
  );
  transition: none;
}
.feature-card:hover::before {
  left: 140%;
  transition: left 0.6s ease;
}

/* 齿轮旋转 (CSS-only) */
.gear-icon {
  display: inline-block;
  animation: spinGear 6s linear infinite;
  color: var(--c-primary);
}
.gear-icon--ccw { animation-direction: reverse; animation-duration: 4s; }
@keyframes spinGear { to { transform: rotate(360deg); } }

/* ── 移动端优化 ────────────────────────────── */
@media (max-width: 480px) {
  .pipeline-strip { display: none; }
  .hero-particle-canvas { opacity: 0.4; }
  .features-grid .feature-card { animation-duration: 0.3s; }
}

/* ── 减少动画偏好 (无障碍) ─────────────────── */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  .hero-particle-canvas, .wave-canvas, .pipeline-canvas, .radar-mini {
    display: none !important;
  }
}

/* ── 触摸设备 tap 反馈 ───────────────────────── */
@media (hover: none) {
  .feature-card:active { transform: scale(0.98); }
  .cta-primary:active  { opacity: 0.85; }
  .cta-secondary:active{ opacity: 0.75; }
}
</style>