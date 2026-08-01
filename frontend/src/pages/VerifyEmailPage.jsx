import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { verifyEmail } from '../api/authApi'
import MathBackground from '../components/MathBackground'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('loading') // loading | success | error

  useEffect(() => {
    const token = searchParams.get('token')

    if (!token) {
      setStatus('error')
      return
    }

    verifyEmail(token)
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'))
  }, [searchParams])

  return (
    <>
      <MathBackground />
      <div className="auth-page">
        {status === 'loading' && <p>Підтверджуємо email...</p>}

        {status === 'success' && (
          <>
            <h1>Email підтверджено</h1>
            <Link to="/login">Перейти до входу</Link>
          </>
        )}

        {status === 'error' && (
          <>
            <h1>Посилання недійсне</h1>
            <p>Токен протух або вже використаний. Спробуйте зареєструватись знову або запросіть новий лист.</p>
            <Link to="/login">Повернутись до входу</Link>
          </>
        )}
      </div>
    </>
  )
}