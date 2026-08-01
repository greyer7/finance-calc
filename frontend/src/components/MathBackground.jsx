const FORMULAS = [
  { text: 'M = P × r(1+r)ⁿ / ((1+r)ⁿ−1)', top: '4%', left: '6%', size: '1.6rem', rot: -6, dx: 70, dy: -30 },
  { text: 'A = P(1+r/n)ⁿᵗ', top: '10%', left: '58%', size: '1.1rem', rot: 4, dx: -50, dy: 40 },
  { text: 'FV = PV / (1+i)ⁿ', top: '22%', left: '2%', size: '1.3rem', rot: 3, dx: 60, dy: 50 },
  { text: 'Σ Cₜ / (1+r)ᵗ', top: '18%', left: '80%', size: '1.4rem', rot: -4, dx: -60, dy: -25 },
  { text: 'r = 0.01 · 12 · t', top: '34%', left: '30%', size: '1.2rem', rot: 5, dx: 40, dy: 60 },
  { text: 'Iₜ = P × (1+π)ᵗ', top: '40%', left: '68%', size: '1.5rem', rot: -3, dx: -70, dy: 35 },
  { text: 'D = 100000 / 12', top: '48%', left: '10%', size: '1.1rem', rot: 6, dx: 55, dy: -45 },
  { text: '%', top: '6%', left: '38%', size: '1rem', rot: -8, dx: -30, dy: 30 },
  { text: '₴ $ €', top: '58%', left: '85%', size: '1.3rem', rot: 2, dx: -45, dy: -55 },
  { text: 'NPV = Σ CFₜ / (1+r)ᵗ − C₀', top: '60%', left: '48%', size: '1.15rem', rot: -5, dx: 65, dy: 40 },
  { text: 'CAGR = (Vₑ/Vᵦ)^(1/n) − 1', top: '68%', left: '4%', size: '1.1rem', rot: 4, dx: -55, dy: -35 },
  { text: 'EAR = (1+r/m)ᵐ − 1', top: '72%', left: '65%', size: '1.2rem', rot: -2, dx: 50, dy: 50 },
  { text: 'PMT = Pr / (1−(1+r)⁻ⁿ)', top: '80%', left: '25%', size: '1.05rem', rot: 7, dx: -60, dy: 30 },
  { text: 'I = P × r × t', top: '86%', left: '55%', size: '1.15rem', rot: -6, dx: 40, dy: -50 },
  { text: 'ROI = (Gain − Cost) / Cost', top: '90%', left: '8%', size: '1rem', rot: 3, dx: 60, dy: 25 },
  { text: 'π', top: '2%', left: '75%', size: '1.3rem', rot: -4, dx: -35, dy: 45 },
]

export default function MathBackground() {
  return (
    <div className="math-bg" aria-hidden="true">
      {FORMULAS.map((f, i) => (
        <span
          key={i}
          style={{
            top: f.top,
            left: f.left,
            fontSize: f.size,
            '--fx-rot': `rotate(${f.rot}deg)`,
            '--fx-dx': `${f.dx}px`,
            '--fx-dy': `${f.dy}px`,
            animationDuration: `${28 + (i % 6) * 5}s`,
            animationDelay: `${-(i * 3)}s`,
          }}
        >
          {f.text}
        </span>
      ))}
    </div>
  )
}
