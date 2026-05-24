<template>
  <div class="map-view">
    <!-- Map container -->
    <div ref="mapContainer" class="map-container"></div>

    <!-- Sidebar -->
    <aside class="map-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h2>Объекты на карте</h2>
        <button class="btn-collapse" @click="sidebarCollapsed = !sidebarCollapsed">
          {{ sidebarCollapsed ? '▶' : '◀' }}
        </button>
      </div>

      <div class="sidebar-content" v-if="!sidebarCollapsed">
        <!-- Filters -->
        <div class="filters-section">
          <h3>Фильтры</h3>
          
          <div class="filter-group">
            <label>Статус:</label>
            <select v-model="filters.status" @change="applyFilters">
              <option value="">Все статусы</option>
              <option value="строится">Строится</option>
              <option value="сдан">Сдан</option>
              <option value="на_гарантии">На гарантии</option>
              <option value="эксплуатация">Эксплуатация</option>
              <option value="аварийный">Аварийный</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Тип объекта:</label>
            <select v-model="filters.objectType" @change="applyFilters">
              <option value="">Все типы</option>
              <option value="жилой комплекс">Жилой комплекс</option>
              <option value="бизнес-центр">Бизнес-центр</option>
              <option value="торговый центр">Торговый центр</option>
              <option value="образование">Образование</option>
              <option value="медицинское учреждение">Медицинское</option>
              <option value="спортивный объект">Спортивный</option>
            </select>
          </div>

          <button class="btn btn-secondary" @click="resetFilters">
            Сбросить фильтры
          </button>
        </div>

        <!-- Objects list -->
        <div class="objects-list">
          <h3>Объекты ({{ filteredObjects.length }})</h3>
          
          <div v-if="loading" class="loading">
            <div class="spinner"></div>
          </div>
          
          <div v-else v-for="obj in filteredObjects" :key="obj.id" 
               class="object-item card"
               @click="selectObject(obj)"
               :class="{ active: selectedObject?.id === obj.id }">
            <div class="object-header">
              <h4>{{ obj.name }}</h4>
              <span class="badge" :class="`badge-${obj.status}`">
                {{ formatStatus(obj.status) }}
              </span>
            </div>
            <p class="object-address">{{ obj.address }}</p>
            <div class="object-meta">
              <span v-if="obj.area_sqm">{{ obj.area_sqm.toLocaleString() }} м²</span>
              <span v-if="obj.floor_count">{{ obj.floor_count }} эт.</span>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Object popup -->
    <div v-if="selectedObject" class="object-popup card">
      <button class="btn-close" @click="selectedObject = null">×</button>
      <h3>{{ selectedObject.name }}</h3>
      <p class="popup-address">{{ selectedObject.address }}</p>
      
      <div class="popup-info">
        <div class="info-row">
          <span>Статус:</span>
          <span class="badge" :class="`badge-${selectedObject.status}`">
            {{ formatStatus(selectedObject.status) }}
          </span>
        </div>
        <div class="info-row">
          <span>Тип:</span>
          <span>{{ selectedObject.object_type }}</span>
        </div>
        <div class="info-row">
          <span>Площадь:</span>
          <span>{{ selectedObject.area_sqm?.toLocaleString() || '—' }} м²</span>
        </div>
        <div class="info-row">
          <span>Этажность:</span>
          <span>{{ selectedObject.floor_count || '—' }}</span>
        </div>
        <div class="info-row">
          <span>Год постройки:</span>
          <span>{{ selectedObject.build_year || '—' }}</span>
        </div>
        <div v-if="selectedObject.warranty_until" class="info-row">
          <span>Гарантия до:</span>
          <span>{{ formatDate(selectedObject.warranty_until) }}</span>
        </div>
      </div>

      <div class="popup-actions">
        <button class="btn btn-primary" @click="viewObjectDetails">
          Подробнее
        </button>
        <button class="btn btn-secondary" @click="centerOnObject">
          Показать на карте
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import axios from 'axios'

const router = useRouter()
const appStore = useAppStore()

const mapContainer = ref(null)
const map = ref(null)
const ymaps = ref(null)
const objectClusters = ref([])
const sidebarCollapsed = ref(false)
const loading = ref(true)
const selectedObject = ref(null)

const filters = ref({
  status: '',
  objectType: ''
})

const allObjects = ref([])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Filtered objects based on current filters
const filteredObjects = computed(() => {
  return allObjects.value.filter(obj => {
    if (filters.value.status && obj.status !== filters.value.status) return false
    if (filters.value.objectType && obj.object_type !== filters.value.objectType) return false
    return true
  })
})

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

// Format date
const formatDate = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU')
}

// Get marker color based on status
const getStatusColor = (status) => {
  const colors = {
    'строится': '#f59e0b',
    'сдан': '#16a34a',
    'на_гарантии': '#0ea5e9',
    'эксплуатация': '#8b5cf6',
    'аварийный': '#dc2626'
  }
  return colors[status] || '#64748b'
}

// Initialize Yandex Maps
const initMap = async () => {
  try {
    // Wait for ymaps to be available
    await waitForYmaps()
    
    // Create map centered on Moscow
    map.value = new ymaps.value.Map(mapContainer.value, {
      center: [55.7558, 37.6173], // Moscow coordinates
      zoom: 10,
      controls: ['zoomControl', 'fullscreenControl', 'typeSelector']
    })

    // Load objects and create markers
    await loadObjects()
    
    loading.value = false
  } catch (error) {
    console.error('Failed to initialize map:', error)
    loading.value = false
  }
}

// Wait for Yandex Maps API to load
const waitForYmaps = () => {
  return new Promise((resolve) => {
    const checkYmaps = () => {
      if (window.ymaps && window.ymaps.ready) {
        window.ymaps.ready(() => {
          ymaps.value = window.ymaps
          resolve()
        })
      } else {
        setTimeout(checkYmaps, 100)
      }
    }
    checkYmaps()
  })
}

// Load objects from API
const loadObjects = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/dashboard/map-objects`)
    allObjects.value = response.data
    createMarkers(response.data)
  } catch (error) {
    console.error('Failed to load objects:', error)
  }
}

// Create markers with clustering
const createMarkers = (objects) => {
  // Clear existing markers
  objectClusters.value.forEach(cluster => {
    if (cluster.destroy) {
      cluster.destroy()
    }
  })
  objectClusters.value = []

  // Create clusterer for Moscow region
  const clusterer = new ymaps.value.Clusterer({
    preset: 'islands#invertedVioletClusterIcons',
    groupByCoordinates: false,
    clusterDisableClickZoom: false,
    clusterHideIconOnBalloonOpen: false,
    geoObjectHideIconOnBalloonOpen: false
  })

  const geoObjects = objects.map(obj => {
    if (!obj.latitude || !obj.longitude) return null

    const placemark = new ymaps.value.Placemark(
      [obj.latitude, obj.longitude],
      {
        balloonContentHeader: obj.name,
        balloonContentBody: `
          <div style="padding: 10px;">
            <p><strong>Адрес:</strong> ${obj.address}</p>
            <p><strong>Статус:</strong> ${formatStatus(obj.status)}</p>
            <p><strong>Площадь:</strong> ${obj.area_sqm?.toLocaleString() || '—'} м²</p>
          </div>
        `,
        hintContent: obj.name
      },
      {
        preset: `islands#${getStatusColor(obj.status).replace('#', '')}CircleIcon`
      }
    )

    placemark.properties.set('objectId', obj.id)
    placemark.events.add('click', () => {
      selectObject(obj)
    })

    return placemark
  }).filter(Boolean)

  clusterer.add(geoObjects)
  map.value.geoObjects.add(clusterer)
  objectClusters.value.push(clusterer)
}

// Apply filters
const applyFilters = () => {
  createMarkers(filteredObjects.value)
}

// Reset filters
const resetFilters = () => {
  filters.value.status = ''
  filters.value.objectType = ''
  createMarkers(allObjects.value)
}

// Select object
const selectObject = (obj) => {
  selectedObject.value = obj
}

// View object details
const viewObjectDetails = () => {
  if (selectedObject.value) {
    router.push(`/objects/${selectedObject.value.id}`)
  }
}

// Center map on selected object
const centerOnObject = () => {
  if (selectedObject.value && selectedObject.value.latitude && selectedObject.value.longitude) {
    map.value.setCenter([selectedObject.value.latitude, selectedObject.value.longitude], 15, {
      duration: 500
    })
  }
}

onMounted(() => {
  initMap()
})
</script>

<style scoped>
.map-view {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-sidebar {
  position: absolute;
  top: 0;
  left: 0;
  width: 350px;
  height: 100%;
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  transition: transform 0.3s ease;
  overflow-y: auto;
}

.map-sidebar.collapsed {
  transform: translateX(-320px);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--primary-color);
  color: white;
}

.sidebar-header h2 {
  font-size: 1.25rem;
}

.btn-collapse {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
}

.sidebar-content {
  padding: 1rem;
}

.filters-section {
  margin-bottom: 1.5rem;
}

.filters-section h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.filter-group {
  margin-bottom: 1rem;
}

.filter-group label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.filter-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.objects-list h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.object-item {
  padding: 1rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.object-item:hover {
  border-color: var(--primary-color);
}

.object-item.active {
  border-color: var(--primary-color);
  background: #eff6ff;
}

.object-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.object-header h4 {
  font-size: 1rem;
  color: var(--text-primary);
}

.object-address {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.object-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.loading {
  text-align: center;
  padding: 2rem;
}

.object-popup {
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  width: 350px;
  max-height: 80vh;
  overflow-y: auto;
  z-index: 1001;
  padding: 1.5rem;
}

.btn-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.popup-address {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.popup-info {
  margin-bottom: 1.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.875rem;
}

.info-row:last-child {
  border-bottom: none;
}

.popup-actions {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .map-sidebar {
    width: 100%;
    height: 50%;
    top: auto;
    bottom: 0;
    transform: translateY(0);
  }
  
  .map-sidebar.collapsed {
    transform: translateY(45%);
  }
  
  .object-popup {
    width: calc(100% - 2rem);
    right: 1rem;
    bottom: 1rem;
  }
}
</style>
