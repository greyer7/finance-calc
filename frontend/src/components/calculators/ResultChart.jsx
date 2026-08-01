import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const CHART_CONFIG = {
  loan: {
    lines: [{ key: 'remaining_balance', label: 'Залишок боргу', color: '#d97757' }],
    xLabel: 'Місяць',
  },
  deposit: {
    lines: [{ key: 'remaining_balance', label: 'Баланс депозиту', color: '#4a90d9' }],
    xLabel: 'Місяць',
  },
  inflation: {
    lines: [{ key: 'remaining_balance', label: 'Купівельна спроможність', color: '#c94f4f' }],
    xLabel: 'Рік',
  },
}

export default function ResultChart({ schedule, type, large = false }) {
  if (!schedule || schedule.length === 0) return null

  const config = CHART_CONFIG[type]

  return (
    <div className={`result-chart${large ? ' result-chart-large' : ''}`}>
      <ResponsiveContainer width="100%" height={large ? 440 : 300}>
        <LineChart data={schedule}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" label={{ value: config.xLabel, position: 'insideBottom', offset: -5 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          {config.lines.map((line) => (
            <Line
              key={line.key}
              type="monotone"
              dataKey={line.key}
              name={line.label}
              stroke={line.color}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}