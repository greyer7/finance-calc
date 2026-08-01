import { useState } from 'react'
import { calculateDeposit } from '../../api/calculatorApi'
import CurrencySelect from '../ui/CurrencySelect'
import TermSelect from '../ui/TermSelect'
import Button from '../ui/Button'

export default function DepositForm({ onResult }) {
  const [principal, setPrincipal] = useState(100000)
  const [annualRate, setAnnualRate] = useState(12)
  const [termMonths, setTermMonths] = useState(12)
  const [compoundingFrequency, setCompoundingFrequency] = useState('monthly')
  const [currency, setCurrency] = useState('USD')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { data } = await calculateDeposit({
        principal,
        annual_rate: annualRate,
        term_months: termMonths,
        compounding_frequency: compoundingFrequency,
        currency,
      })
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
          Сума депозиту
          <input type="number" value={principal} onChange={(e) => setPrincipal(Number(e.target.value))} min="1" required />
        </label>

        <label>
          Річна ставка, %
          <input type="number" value={annualRate} onChange={(e) => setAnnualRate(Number(e.target.value))} min="0" max="100" step="0.1" required />
        </label>

        <label>
          Капіталізація
          <select value={compoundingFrequency} onChange={(e) => setCompoundingFrequency(e.target.value)}>
            <option value="monthly">Щомісячна</option>
            <option value="quarterly">Щоквартальна</option>
            <option value="annually">Щорічна</option>
          </select>
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
          <p>Фінальна сума: <strong>{result.final_amount} {currency}</strong></p>
          <p>Зароблено на відсотках: <strong>{result.total_interest_earned} {currency}</strong></p>
        </div>
      )}
    </div>
  )
}