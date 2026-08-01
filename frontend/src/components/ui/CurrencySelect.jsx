const CURRENCIES = ['USD', 'EUR', 'UAH']

export default function CurrencySelect({ value, onChange }) {
  return (
    <label>
      Валюта
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {CURRENCIES.map((currency) => (
          <option key={currency} value={currency}>{currency}</option>
        ))}
      </select>
    </label>
  )
}