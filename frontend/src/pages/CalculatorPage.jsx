import { useParams } from 'react-router-dom'
import LoanForm from '../components/calculators/LoanForm'
import DepositForm from '../components/calculators/DepositForm'
import InflationForm from '../components/calculators/InflationForm'

const CALCULATOR_CONFIG = {
  'loan-annuity': { title: 'Кредит (ануїтет)', type: 'annuity' },
  'loan-differentiated': { title: 'Кредит (диференційований)', type: 'differentiated' },
  'deposit': { title: 'Депозит', type: 'deposit' },
  'inflation': { title: 'Інфляція', type: 'inflation' },
}

export default function CalculatorPage() {
  const { calculatorType } = useParams()
  const config = CALCULATOR_CONFIG[calculatorType]

  if (!config) {
    return <p>Невідомий тип калькулятора</p>
  }

  return (
    <div className="calculator-page">
      <h1>{config.title}</h1>

      {(config.type === 'annuity' || config.type === 'differentiated') && (
        <LoanForm variant={config.type} />
      )}
      {config.type === 'deposit' && <DepositForm />}
      {config.type === 'inflation' && <InflationForm />}
    </div>
  )
}