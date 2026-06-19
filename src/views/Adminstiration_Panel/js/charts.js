// ── charts.js — lightweight SVG chart components (no external library) ────

// Sparkline — small inline trend line used on stat cards
const Sparkline = ({ data, color = '#2a85ff', height = 40 }) => {
  const w = 120, h = height;
  const max = Math.max(...data), min = Math.min(...data);
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / (max - min + 1)) * (h - 4) - 2;
    return `${x},${y}`;
  }).join(' ');
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="sparkline">
      <polyline
        points={pts}
        fill="none"
        stroke={color}
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

// BarChart — weekly query volume histogram on the Dashboard
const BarChart = ({ data }) => {
  const max = Math.max(...data.map(d => d.v));
  const chartH = 160; // total chart height
  const barAreaH = 130; // height available for bars

  return (
    <div style={{ padding: '8px 4px 0' }}>
      {/* Bars + value labels */}
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '10px', height: `${chartH}px` }}>
        {data.map((d, i) => {
          const barH = Math.max(4, (d.v / max) * barAreaH);
          return (
            <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', height: '100%', justifyContent: 'flex-end' }}>
              {/* value on top */}
              <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-2)' }}>{d.v}</span>
              {/* bar */}
              <div style={{
                width: '100%',
                background: 'var(--accent)',
                borderRadius: '6px 6px 0 0',
                height: `${barH}px`,
                transition: 'height 0.6s ease',
                minHeight: '4px',
              }} />
              {/* day label */}
              <span style={{ fontSize: '11px', color: 'var(--text-3)', whiteSpace: 'nowrap', marginTop: '4px' }}>{d.l}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// DonutChart — coverage overview on the Gap Analysis page
const DonutChart = ({ segments }) => {
  let offset = 0;
  const r = 46, cx = 60, cy = 60, stroke = 14;
  const circ = 2 * Math.PI * r;
  return (
    <svg width="120" height="120" viewBox="0 0 120 120">
      {segments.map((s, i) => {
        const dash = (s.pct / 100) * circ;
        const el = (
          <circle
            key={i} cx={cx} cy={cy} r={r}
            fill="none" stroke={s.color} strokeWidth={stroke}
            strokeDasharray={`${dash} ${circ - dash}`}
            strokeDashoffset={-offset * circ / 100}
            strokeLinecap="butt"
            transform="rotate(-90 60 60)"
          />
        );
        offset += s.pct;
        return el;
      })}
      <text x={cx} y={cy - 4} textAnchor="middle"
        style={{ fontSize: '16px', fontWeight: 600, fill: 'var(--text)', fontFamily: 'Space Grotesk' }}>
        {segments[0]?.pct}%
      </text>
      <text x={cx} y={cy + 14} textAnchor="middle"
        style={{ fontSize: '10px', fill: 'var(--text-3)' }}>
        covered
      </text>
    </svg>
  );
};
