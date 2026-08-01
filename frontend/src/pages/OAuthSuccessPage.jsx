import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getMe } from '../api/authApi'
import { useAuth } from '../context/AuthContext'
import MathBackground from '../components/MathBackground'

export default function OAuthSuccessPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login, setUser } = useAuth()

  useEffect(() => {
    const accessToken = searchParams.get('access_token')
    const refreshToken = searchParams.get('refresh_token')

    if (!accessToken || !refreshToken) {
      navigate('/login')
      return
    }

    const finishLogin = async () => {
      login({ access_token: accessToken, refresh_token: refreshToken }, null)
      try {
        const { data: userData } = await getMe()
        setUser(userData)
        navigate('/dashboard')
      } catch {
        navigate('/login')
      }
    }

    finishLogin()
  }, [])

  return (
    <>
      <MathBackground />
      <div className="auth-page">
        <p>Завершуємо вхід...</p>
      </div>
    </>
  )
}