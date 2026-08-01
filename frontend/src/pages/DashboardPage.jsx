import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { getCalculationHistory, deleteCalculation } from '../api/calculatorApi'
import Button from '../components/ui/Button'
import LoanForm from '../components/calculators/LoanForm'
import DepositForm from '../components/calculators/DepositForm'
import InflationForm from '../components/calculators/InflationForm'
import ResultChart from '../components/calculators/ResultChart'

const CALCULATORS = [
  { key: 'annuity', label: 'Кредит (ануїтет)', chartType: 'loan' },
  { key: 'differentiated', label: 'Кредит (диференційований)', chartType: 'loan' },
  { key: 'deposit', label: 'Депозит', chartType: 'deposit' },
  { key: 'inflation', label: 'Інфляція', chartType: 'inflation' },
]

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeCalc, setActiveCalc] = useState('annuity')
  const [chartSchedule, setChartSchedule] = useState(null)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const { data } = await getCalculationHistory()
      setHistory(data)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    await deleteCalculation(id)
    setHistory((prev) => prev.filter((item) => item.id !== id))
  }

  const handleSelectCalc = (key) => {
    setActiveCalc(key)
    setChartSchedule(null)
  }

  const handleResult = (schedule) => {
    setChartSchedule(schedule)
    loadHistory()
  }

  const activeConfig = CALCULATORS.find((c) => c.key === activeCalc)

  const renderForm = () => {
    switch (activeCalc) {
      case 'annuity':
        return <LoanForm variant="annuity" onResult={handleResult} />
      case 'differentiated':
        return <LoanForm variant="differentiated" onResult={handleResult} />
      case 'deposit':
        return <DepositForm onResult={handleResult} />
      case 'inflation':
        return <InflationForm onResult={handleResult} />
      default:
        return null
    }
  }

  return (
    <div className="dashboard">
      <header>
        <h1>Фінансовий калькулятор</h1>
        <div className="dashboard-user">
          <span className="dashboard-user-email">{user?.email}</span>
          <Button variant="secondary" onClick={logout}>Вийти</Button>
        </div>
      </header>

      <div className="dashboard-grid">
        <aside className="calc-sidebar">
          <nav className="calculator-links">
            {CALCULATORS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                className={`calc-nav-btn${activeCalc === key ? ' active' : ''}`}
                onClick={() => handleSelectCalc(key)}
              >
                {label}
              </button>
            ))}
          </nav>

          <div className="calc-form-panel">
            {renderForm()}
          </div>
        </aside>

        <section className="calc-chart-panel">
          {chartSchedule ? (
            <ResultChart schedule={chartSchedule} type={activeConfig.chartType} large />
          ) : (
            <p className="chart-placeholder">
              Заповніть форму зліва і натисніть «Розрахувати» —{'\u00A0'}графік з'явиться тут.
            </p>
          )}
        </section>
      </div>

      <section className="history-section">
        <h2>Історія розрахунків</h2>

        {loading && <p>Завантаження...</p>}

        {!loading && history.length === 0 && <p>Ще немає збережених розрахунків.</p>}

        <ul className="history-list">
          {history.map((item) => (
            <li key={item.id}>
              <span>{item.title || item.calculation_type}</span>
              <span>{item.principal} {item.currency}</span>
              <span>{new Date(item.created_at).toLocaleDateString('uk-UA')}</span>
              <Button variant="danger" onClick={() => handleDelete(item.id)}>Видалити</Button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
