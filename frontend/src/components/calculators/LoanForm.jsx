import { useState } from 'react'
import { calculateLoanAnnuity, calculateLoanDifferentiated } from '../../api/calculatorApi'
import CurrencySelect from '../ui/CurrencySelect'
import TermSelect from '../ui/TermSelect'
import Button from '../ui/Button'

export default function LoanForm({ variant, onResult }) {
  const [principal, setPrincipal] = useState(100000)
  const [annualRate, setAnnualRate] = useState(12)
  const [termMonths, setTermMonths] = useState(12)
  const [currency, setCurrency] = useState('USD')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const payload = { principal, annual_rate: annualRate, term_months: termMonths, currency }
    const calculateFn = variant === 'annuity' ? calculateLoanAnnuity : calculateLoanDifferentiated

    try {
      const { data } = await calculateFn(payload)
      setResult(data)
      onResult?.(data.schedule)
    } catch (err) {
      setError(err.response?.data?.detail || 'Помилка розрахунку')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          Сума кредиту
          <input type="number" value={principal} onChange={(e) => setPrincipal(Number(e.target.value))} min="1" required />
        </label>

        <label>
          Річна ставка, %
          <input type="number" value={annualRate} onChange={(e) => setAnnualRate(Number(e.target.value))} min="0" max="100" step="0.1" required />
        </label>

        <TermSelect value={termMonths} onChange={setTermMonths} />
        <CurrencySelect value={currency} onChange={setCurrency} />

        <Button type="submit" disabled={loading}>
            {loading ? 'Розрахунок...' : 'Розрахувати'}
        </Button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          {variant === 'annuity' ? (
            <p>Щомісячний платіж: <strong>{result.monthly_payment} {currency}</strong></p>
          ) : (
            <p>
              Перший платіж: <strong>{result.first_payment} {currency}</strong> —
              Останній: <strong>{result.last_payment} {currency}</strong>
            </p>
          )}
          <p>Загальна переплата: <strong>{result.total_interest} {currency}</strong></p>
          <p>Загалом до сплати: <strong>{result.total_payment} {currency}</strong></p>
        </div>
      )}
    </div>
  )
}