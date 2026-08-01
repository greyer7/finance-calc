import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login as loginApi, getMe } from '../api/authApi'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import MathBackground from '../components/MathBackground'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login, setUser } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { data: tokens } = await loginApi(email, password)
      login(tokens, null)

      const { data: userData } = await getMe()
      setUser(userData)

      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(detail || 'Помилка входу. Спробуйте ще раз.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <MathBackground />
      <div className="auth-page">
        <form onSubmit={handleSubmit}>
          <h1>Вхід</h1>

          {error && <p className="error">{error}</p>}

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <Button type="submit" disabled={loading}>
            {loading ? 'Вхід...' : 'Увійти'}
          </Button>

          <div className="oauth-buttons">
            <a href="http://localhost:8000/api/v1/oauth/google/login">Увійти через Google</a>
            <a href="http://localhost:8000/api/v1/oauth/github/login">Увійти через GitHub</a>
          </div>

          <p>
            Немає акаунту? <Link to="/register">Зареєструватись</Link>
          </p>
        </form>
      </div>
    </>
  )
}