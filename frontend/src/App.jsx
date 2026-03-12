import { useState } from 'react'

const EXAMPLE = `76 year old male with NSCLC stage IV, prior chemoradiation, no brain metastasis. Patient was a parking attendant with long-term exposure to automobile exhaust fumes. Diagnosed with adenocarcinoma treated with stereotactic radiosurgery, later developed small cell lung cancer.`

function Header() {
  return (
    <header style={{
      background: 'var(--navy)',
      padding: '0 32px',
      height: 56,
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      borderBottom: '1px solid rgba(255,255,255,0.08)'
    }}>
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#85B7EB" strokeWidth="1.8" strokeLinecap="round">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
      </svg>
      <span style={{ color: '#fff', fontWeight: 600, fontSize: 16, letterSpacing: '-0.01em' }}>
        Clinical Trial Matcher
      </span>
      <span style={{
        marginLeft: 'auto',
        fontSize: 12,
        color: 'var(--pale2)',
        background: 'rgba(255,255,255,0.07)',
        padding: '3px 10px',
        borderRadius: 20,
        border: '0.5px solid rgba(255,255,255,0.12)'
      }}>
        3,600+ trials indexed
      </span>
    </header>
  )
}

function PatientForm({ onResult, loading, setLoading }) {
  const [text, setText] = useState(EXAMPLE)

  async function handleSubmit() {
    if (!text.trim()) return
    setLoading(true)
    onResult(null)
    try {
      const res = await fetch('/analyze-patient', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      const data = await res.json()
      onResult(data)
    } catch (e) {
      onResult({ error: 'API bağlantı hatası. FastAPI çalışıyor mu?' })
    }
    setLoading(false)
  }

  return (
    <div style={{
      background: 'var(--white)',
      borderRadius: 12,
      border: '0.5px solid var(--border)',
      padding: 20
    }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--mid)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8 }}>
        Patient Case
      </div>
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Paste free-text patient case here..."
        style={{
          width: '100%',
          minHeight: 140,
          border: '0.5px solid var(--border)',
          borderRadius: 8,
          padding: '12px 14px',
          fontSize: 14,
          color: 'var(--text)',
          fontFamily: 'inherit',
          resize: 'vertical',
          outline: 'none',
          lineHeight: 1.6
        }}
        onFocus={e => e.target.style.borderColor = 'var(--light)'}
        onBlur={e => e.target.style.borderColor = 'var(--border)'}
      />
      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{
          marginTop: 12,
          width: '100%',
          background: loading ? 'var(--mid)' : 'var(--blue)',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          padding: '11px 20px',
          fontSize: 14,
          fontWeight: 500,
          cursor: loading ? 'not-allowed' : 'pointer',
          fontFamily: 'inherit',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          transition: 'background 0.15s'
        }}
      >
        {loading ? (
          <>
            <Spinner /> Analyzing...
          </>
        ) : (
          <>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            Analyze Patient
          </>
        )}
      </button>
    </div>
  )
}

function Spinner() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ animation: 'spin 0.8s linear infinite' }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
    </svg>
  )
}

function PatientProfile({ patient }) {
  const fields = [
    { label: 'Age', value: patient.age ?? '—' },
    { label: 'Gender', value: patient.gender ?? '—' },
    { label: 'Cancer type', value: patient.cancer_type?.join(', ') || '—' },
    { label: 'Stage', value: patient.stage ?? '—' },
    { label: 'ECOG', value: patient.ecog ?? '—' },
    { label: 'Brain metastasis', value: patient.brain_metastasis === true ? 'Yes' : patient.brain_metastasis === false ? 'No' : '—' },
  ]

  return (
    <div style={{
      background: 'var(--white)',
      borderRadius: 12,
      border: '0.5px solid var(--border)',
      padding: 20
    }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--mid)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 14 }}>
        Extracted Profile
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        {fields.map(f => (
          <div key={f.label} style={{ background: 'var(--surface)', borderRadius: 8, padding: '9px 12px' }}>
            <div style={{ fontSize: 11, color: 'var(--mid)', fontWeight: 500, marginBottom: 2 }}>{f.label}</div>
            <div style={{ fontSize: 14, color: 'var(--navy)', fontWeight: 600 }}>{String(f.value)}</div>
          </div>
        ))}
      </div>
      {patient.treatments?.length > 0 && (
        <div style={{ background: 'var(--surface)', borderRadius: 8, padding: '9px 12px', marginTop: 8 }}>
          <div style={{ fontSize: 11, color: 'var(--mid)', fontWeight: 500, marginBottom: 4 }}>Prior treatments</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {patient.treatments.map(t => (
              <span key={t} style={{
                fontSize: 12,
                background: 'var(--pale)',
                color: 'var(--blue)',
                padding: '2px 8px',
                borderRadius: 20,
                fontWeight: 500
              }}>{t}</span>
            ))}
          </div>
        </div>
      )}
      {patient.mutations?.length > 0 && (
        <div style={{ background: 'var(--surface)', borderRadius: 8, padding: '9px 12px', marginTop: 8 }}>
          <div style={{ fontSize: 11, color: 'var(--mid)', fontWeight: 500, marginBottom: 4 }}>Mutations</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {patient.mutations.map(m => (
              <span key={m} style={{
                fontSize: 12,
                background: 'var(--amber-bg)',
                color: 'var(--amber-text)',
                padding: '2px 8px',
                borderRadius: 20,
                fontWeight: 500
              }}>{m}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function TrialCard({ match }) {
  const eligible = match.decision?.eligible
  const failed = match.decision?.failed_rules || []

  return (
    <div style={{
      border: `0.5px solid ${eligible ? '#c0d8b0' : 'var(--border)'}`,
      borderLeft: `3px solid ${eligible ? '#639922' : '#E24B4A'}`,
      borderRadius: 10,
      padding: '14px 16px',
      background: 'var(--white)',
      marginBottom: 10
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10, marginBottom: 8 }}>
        <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--navy)', lineHeight: 1.4, flex: 1 }}>
          {match.title}
        </div>
        <span style={{
          flexShrink: 0,
          fontSize: 11,
          fontWeight: 600,
          padding: '4px 10px',
          borderRadius: 20,
          background: eligible ? 'var(--green-bg)' : 'var(--red-bg)',
          color: eligible ? 'var(--green-text)' : 'var(--red-text)'
        }}>
          {eligible ? 'Eligible' : 'Not eligible'}
        </span>
      </div>
      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
        <span style={{
          fontSize: 11,
          background: 'var(--pale)',
          color: 'var(--blue)',
          padding: '3px 8px',
          borderRadius: 4,
          fontFamily: 'DM Mono, monospace',
          fontWeight: 500
        }}>
          {match.nct_id}
        </span>
        <span style={{ fontSize: 11, color: 'var(--muted)', background: 'var(--surface)', padding: '3px 8px', borderRadius: 4 }}>
          Score {match.score?.toFixed(3)}
        </span>
      </div>
      {failed.length > 0 && (
        <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {failed.map((f, i) => (
            <span key={i} style={{
              fontSize: 11,
              background: 'var(--red-bg)',
              color: 'var(--red-text)',
              padding: '2px 8px',
              borderRadius: 4
            }}>
              {f}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

function MatchResults({ matches }) {
  const eligible = matches.filter(m => m.decision?.eligible)
  const ineligible = matches.filter(m => !m.decision?.eligible)

  return (
    <div style={{
      background: 'var(--white)',
      borderRadius: 12,
      border: '0.5px solid var(--border)',
      padding: 20
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--mid)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          Trial Matches
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <span style={{ fontSize: 11, background: 'var(--green-bg)', color: 'var(--green-text)', padding: '2px 10px', borderRadius: 20, fontWeight: 600 }}>
            {eligible.length} eligible
          </span>
          <span style={{ fontSize: 11, background: 'var(--red-bg)', color: 'var(--red-text)', padding: '2px 10px', borderRadius: 20, fontWeight: 600 }}>
            {ineligible.length} not eligible
          </span>
        </div>
      </div>
      {matches.map(m => <TrialCard key={m.trial_id} match={m} />)}
    </div>
  )
}

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 16px', width: '100%' }}>
        <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: 20, marginBottom: 20 }}>
          <PatientForm onResult={setResult} loading={loading} setLoading={setLoading} />
          {result?.patient && <PatientProfile patient={result.patient} />}
        </div>
        {result?.error && (
          <div style={{ background: 'var(--red-bg)', color: 'var(--red-text)', padding: '12px 16px', borderRadius: 8, fontSize: 14 }}>
            {result.error}
          </div>
        )}
        {result?.matches && <MatchResults matches={result.matches} />}
      </div>
    </div>
  )
}
