import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register as registerApi } from '../api/authApi'
import Button from '../components/ui/Button'
import MathBackground from '../components/MathBackground'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await registerApi(email, password)
      setSuccess(true)
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(', '))
      } else {
        setError(detail || 'Помилка реєстрації. Спробуйте ще раз.')
      }
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <>
        <MathBackground />
        <div className="auth-page">
          <h1>Перевірте пошту</h1>
          <p>Ми надіслали лист із посиланням для підтвердження на {email}.</p>
          <Link to="/login">Перейти до входу</Link>
        </div>
      </>
    )
  }

  return (
    <>
      <MathBackground />
      <div className="auth-page">
        <form onSubmit={handleSubmit}>
          <h1>Реєстрація</h1>

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
            placeholder="Пароль (мінімум 8 символів)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <Button type="submit" disabled={loading}>
            {loading ? 'Реєстрація...' : 'Зареєструватись'}
          </Button>

          <p>
            Вже є акаунт? <Link to="/login">Увійти</Link>
          </p>
        </form>
      </div>
    </>
  )
}