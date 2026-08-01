import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
})

export function setAuthToken(token) {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete apiClient.defaults.headers.common['Authorization']
  }
}

// Автоматичне оновлення access token при 401 і повторна спроба запиту
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_URL}/api/v1/auth/refresh`, { refresh_token: refreshToken })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          setAuthToken(data.access_token)
          originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`
          return apiClient(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export const register = (email, password) =>
  apiClient.post('/auth/register', { email, password })

export const login = (email, password) =>
  apiClient.post('/auth/login', { email, password })

export const verifyEmail = (token) =>
  apiClient.post('/auth/verify-email', { token })

export const resendVerification = (email) =>
  apiClient.post('/auth/resend-verification', { email })

export const refreshAccessToken = (refreshToken) =>
  apiClient.post('/auth/refresh', { refresh_token: refreshToken })

export const logout = (refreshToken) =>
  apiClient.post('/auth/logout', { refresh_token: refreshToken })

export const getMe = () =>
  apiClient.get('/auth/me')

export default apiClient