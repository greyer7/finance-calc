import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'

import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import OAuthSuccessPage from './pages/OAuthSuccessPage'
import DashboardPage from './pages/DashboardPage'
import CalculatorPage from './pages/CalculatorPage'

function ProtectedRoute({ children }) {
  const { accessToken, loading } = useAuth()

  if (loading) return <p>Завантаження...</p>
  if (!accessToken) return <Navigate to="/login" replace />

  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/oauth-success" element={<OAuthSuccessPage />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/calculator/:calculatorType"
        element={
          <ProtectedRoute>
            <CalculatorPage />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}