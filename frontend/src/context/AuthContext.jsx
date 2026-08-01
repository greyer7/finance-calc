import { createContext, useContext, useState, useEffect } from 'react'
import { setAuthToken, refreshAccessToken } from '../api/authApi'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'))
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const login = (tokens, userData) => {
    setAccessToken(tokens.access_token)
    setRefreshToken(tokens.refresh_token)
    setUser(userData)
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    setAuthToken(tokens.access_token)
  }

  const logout = () => {
    setAccessToken(null)
    setRefreshToken(null)
    setUser(null)
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setAuthToken(null)
  }

  useEffect(() => {
    const initAuth = async () => {
      if (accessToken) {
        setAuthToken(accessToken)
      }
      setLoading(false)
    }
    initAuth()
  }, [])

  return (
    <AuthContext.Provider value={{ accessToken, refreshToken, user, setUser, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}