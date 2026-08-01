const TERMS_MONTHS = [6, 12, 24, 36, 60, 120, 180, 240, 360]

export default function TermSelect({ value, onChange }) {
  return (
    <label>
      Строк
      <select value={value} onChange={(e) => onChange(Number(e.target.value))}>
        {TERMS_MONTHS.map((months) => (
          <option key={months} value={months}>
            {months < 12 ? `${months} міс.` : `${months / 12} р.`}
          </option>
        ))}
      </select>
    </label>
  )
}