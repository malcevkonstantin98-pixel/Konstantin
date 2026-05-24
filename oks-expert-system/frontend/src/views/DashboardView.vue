<template>
  <div class="dashboard-view">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">
        <h1>Панель мониторинга</h1>
        <div class="header-actions">
          <span class="online-status" :class="{ offline: !appStore.isOnline }">
            {{ appStore.isOnline ? 'Онлайн' : 'Офлайн' }}
          </span>
          <button class="btn btn-primary" @click="$router.push('/map')">
            Карта объектов
          </button>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="dashboard-content container">
      <!-- Stats widgets -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🏢</div>
          <div class="stat-info">
            <h3>{{ appStore.stats?.total_objects || 0 }}</h3>
            <p>Всего объектов</p>
          </div>
        </div>

        <div class="stat-card warning">
          <div class="stat-icon">⚠️</div>
          <div class="stat-info">
            <h3>{{ appStore.stats?.open_defects || 0 }}</h3>
            <p>Открытых дефектов</p>
          </div>
        </div>

        <div class="stat-card danger">
          <div class="stat-icon">🔴</div>
          <div class="stat-info">
            <h3>{{ appStore.stats?.critical_defects || 0 }}</h3>
            <p>Критических</p>
          </div>
        </div>

        <div class="stat-card info">
          <div class="stat-icon">📋</div>
          <div class="stat-info">
            <h3>{{ appStore.stats?.overdue_tasks || 0 }}</h3>
            <p>Просрочено задач</p>
          </div>
        </div>

        <div class="stat-card success">
          <div class="stat-icon">⏰</div>
          <div class="stat-info">
            <h3>{{ appStore.stats?.expiring_warranties || 0 }}</h3>
            <p>Истекает гарантия</p>
          </div>
        </div>
      </div>

      <!-- Objects by status -->
      <div class="dashboard-section">
        <h2>Статусы объектов</h2>
        <div class="status-chart">
          <div 
            v-for="(count, status) in appStore.stats?.objects_by_status" 
            :key="status"
            class="status-item"
          >
            <span class="status-badge" :class="`badge-${status}`">
              {{ formatStatus(status) }}
            </span>
            <div class="status-bar">
              <div 
                class="status-fill" 
                :class="`badge-${status}`"
                :style="{ width: getPercentage(count) + '%' }"
              ></div>
            </div>
            <span class="status-count">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- Recent defects -->
      <div class="dashboard-section">
        <h2>Последние дефекты</h2>
        <div class="defects-list">
          <div v-if="loading" class="loading">
            <div class="spinner"></div>
          </div>
          <div v-else-if="recentDefects.length === 0" class="empty-state">
            Нет открытых дефектов
          </div>
          <div v-else v-for="defect in recentDefects" :key="defect.id" class="defect-item card">
            <div class="defect-header">
              <h4>{{ defect.title }}</h4>
              <span class="badge" :class="`badge-${defect.priority}`">
                {{ defect.priority }}
              </span>
            </div>
            <p class="defect-object">Объект: {{ defect.object_name }}</p>
            <p class="defect-date">{{ formatDate(defect.detected_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="dashboard-section">
        <h2>Быстрые действия</h2>
        <div class="quick-actions">
          <button class="action-card" @click="$router.push('/reports')">
            <span class="action-icon">📸</span>
            <span>Создать отчёт</span>
          </button>
          <button class="action-card" @click="$router.push('/tasks')">
            <span class="action-icon">✅</span>
            <span>Задачи</span>
          </button>
          <button class="action-card" @click="$router.push('/map')">
            <span class="action-icon">🗺️</span>
            <span>Карта</span>
          </button>
          <button class="action-card" @click="refreshData">
            <span class="action-icon">🔄</span>
            <span>Обновить</span>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import axios from 'axios'

const appStore = useAppStore()
const loading = ref(false)
const recentDefects = ref([])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Format status for display
const formatStatus = (status) => {
  const statusMap = {
    'строится': 'Строится',
    'сдан': 'Сдан',
    'на_гарантии': 'На гарантии',
    'эксплуатация': 'Эксплуатация',
    'аварийный': 'Аварийный'
  }
  return statusMap[status] || status
}

// Calculate percentage for status bar
const maxObjects = computed(() => {
  if (!appStore.stats?.objects_by_status) return 1
  return Math.max(...Object.values(appStore.stats.objects_by_status))
})

const getPercentage = (count) => {
  return (count / maxObjects.value) * 100
}

// Format date
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Fetch recent defects
const fetchRecentDefects = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/dashboard/recent-defects?limit=5`)
    recentDefects.value = response.data
  } catch (error) {
    console.error('Failed to fetch recent defects:', error)
  }
}

// Refresh all data
const refreshData = async () => {
  loading.value = true
  await Promise.all([
    appStore.fetchStats(),
    fetchRecentDefects()
  ])
  loading.value = false
}

onMounted(async () => {
  await refreshData()
  
  // Listen for online/offline events
  window.addEventListener('online', () => appStore.setOnlineStatus(true))
  window.addEventListener('offline', () => appStore.setOnlineStatus(false))
})
</script>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  background-color: var(--bg-color);
}

.dashboard-header {
  background: white;
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 1.5rem;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.online-status {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  background: #d1fae5;
  color: #065f46;
}

.online-status.offline {
  background: #fef3c7;
  color: #92400e;
}

.dashboard-content {
  padding: 2rem 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-card.warning {
  border-left: 4px solid var(--warning-color);
}

.stat-card.danger {
  border-left: 4px solid var(--danger-color);
}

.stat-card.info {
  border-left: 4px solid var(--info-color);
}

.stat-card.success {
  border-left: 4px solid var(--success-color);
}

.stat-icon {
  font-size: 2rem;
}

.stat-info h3 {
  font-size: 1.5rem;
  color: var(--text-primary);
}

.stat-info p {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.dashboard-section {
  margin-bottom: 2rem;
}

.dashboard-section h2 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.status-chart {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.status-badge {
  min-width: 120px;
}

.status-bar {
  flex: 1;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.status-count {
  min-width: 40px;
  text-align: right;
  font-weight: 600;
}

.defects-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.defect-item {
  padding: 1rem;
}

.defect-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.defect-header h4 {
  font-size: 1rem;
  color: var(--text-primary);
}

.defect-object,
.defect-date {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.loading,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.action-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 2rem;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
