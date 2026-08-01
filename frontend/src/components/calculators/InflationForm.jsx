import { useState } from 'react'
import { calculateInflation } from '../../api/calculatorApi'
import CurrencySelect from '../ui/CurrencySelect'
import Button from '../ui/Button'

export default function InflationForm({ onResult }) {
  const [amount, setAmount] = useState(10000)
  const [annualInflationRate, setAnnualInflationRate] = useState(8)
  const [termYears, setTermYears] = useState(5)
  const [currency, setCurrency] = useState('USD')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { data } = await calculateInflation({
        amount,
        annual_inflation_rate: annualInflationRate,
        term_years: termYears,
        currency,
      })
      setResult(data)
      onResult?.(data.yearly_breakdown)
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
          Сума
          <input type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} min="1" required />
        </label>

        <label>
          Рівень інфляції, % на рік
          <input
            type="number"
            value={annualInflationRate}
            onChange={(e) => setAnnualInflationRate(Number(e.target.value))}
            min="0"
            max="100"
            step="0.1"
            required
          />
        </label>

        <label>
          Строк, років
          <select value={termYears} onChange={(e) => setTermYears(Number(e.target.value))}>
            {[1, 2, 3, 5, 10, 15, 20, 25, 30].map((years) => (
              <option key={years} value={years}>{years}</option>
            ))}
          </select>
        </label>

        <CurrencySelect value={currency} onChange={setCurrency} />

        <Button type="submit" disabled={loading}>
            {loading ? 'Розрахунок...' : 'Розрахувати'}
        </Button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <p>Еквівалент через {termYears} р.: <strong>{result.adjusted_value} {currency}</strong></p>
          <p>Втрата купівельної спроможності: <strong>{result.purchasing_power_loss}%</strong></p>
        </div>
      )}
    </div>
  )
}