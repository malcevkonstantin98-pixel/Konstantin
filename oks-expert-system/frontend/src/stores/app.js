import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const useAppStore = defineStore('app', {
  state: () => ({
    user: null,
    objects: [],
    stats: null,
    loading: false,
    error: null,
    isOnline: navigator.onLine
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.user,
    totalObjects: (state) => state.objects.length,
    openDefects: (state) => state.stats?.open_defects || 0,
    criticalDefects: (state) => state.stats?.critical_defects || 0
  },
  
  actions: {
    async login(email, password) {
      try {
        this.loading = true
        const response = await api.post('/api/auth/login', null, {
          params: { email, password }
        })
        
        this.user = response.data.user
        localStorage.setItem('access_token', response.data.access_token)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    logout() {
      this.user = null
      localStorage.removeItem('access_token')
    },
    
    async fetchStats() {
      try {
        const response = await api.get('/api/dashboard/stats')
        this.stats = response.data
        return response.data
      } catch (error) {
        console.error('Failed to fetch stats:', error)
        throw error
      }
    },
    
    async fetchObjects(filters = {}) {
      try {
        this.loading = true
        const params = new URLSearchParams()
        
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, value)
        })
        
        const response = await api.get(`/api/objects?${params}`)
        this.objects = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchMapObjects() {
      try {
        const response = await api.get('/api/dashboard/map-objects')
        return response.data
      } catch (error) {
        console.error('Failed to fetch map objects:', error)
        throw error
      }
    },
    
    setOnlineStatus(status) {
      this.isOnline = status
    }
  }
})
