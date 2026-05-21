/* Variação B — Técnica Densa (Linear/Notion)
   Sans geométrica + mono, pipeline da IA como esteira de produção, data-dense. */

const techTheme = {
  light: {
    '--t-bg':       '#fafafa',
    '--t-surface':  '#ffffff',
    '--t-surface-2':'#f4f4f5',
    '--t-surface-3':'#ebebed',
    '--t-ink':      '#0b0d10',
    '--t-ink-2':    '#35383d',
    '--t-muted':    '#8a8e95',
    '--t-mute-2':   '#b4b7bc',
    '--t-rule':     '#e4e4e7',
    '--t-rule-2':   '#d4d4d8',
    '--t-accent':   '#2b5fd9',
    '--t-accent-2': '#1a3f99',
    '--t-ok':       '#2f8f4e',
    '--t-warn':     '#c47013',
    '--t-err':      '#c83a3a',
    '--t-ai':       '#7a42c4',
    '--t-human':    '#2b5fd9',
  },
  dark: {
    '--t-bg':       '#0a0b0d',
    '--t-surface':  '#111214',
    '--t-surface-2':'#17181b',
    '--t-surface-3':'#1e2024',
    '--t-ink':      '#eef0f3',
    '--t-ink-2':    '#c2c6cc',
    '--t-muted':    '#7a7f87',
    '--t-mute-2':   '#55595f',
    '--t-rule':     '#25272b',
    '--t-rule-2':   '#34373c',
    '--t-accent':   '#6b92f5',
    '--t-accent-2': '#94b0f8',
    '--t-ok':       '#5cc47a',
    '--t-warn':     '#e09946',
    '--t-err':      '#e66363',
    '--t-ai':       '#b892f0',
    '--t-human':    '#6b92f5',
  },
};

function applyTechTheme(el, dark) {
  const vars = dark ? techTheme.dark : techTheme.light;
  Object.entries(vars).forEach(([k, v]) => el.style.setProperty(k, v));
}

function TechSidebar({ active }) {
  const sections = [
    { header: 'Workspace' },
    { id: 'painel',      label: 'Painel',      kbd: 'G P' },
    { id: 'buscas',      label: 'Buscas',      kbd: 'G B', badge: '2' },
    { id: 'documentos',  label: 'Documentos',  kbd: 'G D' },
    { id: 'revisao',     label: 'Revisão',     kbd: 'G R', badge: '48', badgeTone: 'warn' },
    { header: 'Corpus' },
    { id: 'timeline',    label: 'Timeline 1961–2008' },
    { id: 'tipos',       label: 'Tipos de ato' },
    { id: 'exports',     label: 'Exports' },
    { header: 'Conta' },
    { id: 'perfil',      label: 'Perfil' },
    { id: 'openai',      label: 'Chave OpenAI', dot: 'ok' },
  ];
  return (
    <aside style={{
      width: 236, flexShrink: 0,
      borderRight: '1px solid var(--t-rule)',
      background: 'var(--t-surface)',
      padding: '12px 8px', display: 'flex', flexDirection: 'column', gap: 2,
      fontFamily: 'var(--t-sans)',
    }}>
      <div style={{
        padding: '6px 10px 10px', display: 'flex', alignItems: 'center', gap: 8,
        borderBottom: '1px solid var(--t-rule)', marginBottom: 8,
      }}>
        <div style={{
          width: 22, height: 22, borderRadius: 5,
          background: 'var(--t-ink)', color: 'var(--t-surface)',
          display: 'grid', placeItems: 'center',
          fontFamily: 'var(--t-mono)', fontSize: 10, fontWeight: 600,
        }}>I</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--t-ink)' }}>IOMAT Mineração</div>
          <div style={{ fontFamily: 'var(--t-mono)', fontSize: 9, color: 'var(--t-muted)', letterSpacing: '0.04em' }}>
            v0.4.2 · ana.p
          </div>
        </div>
      </div>

      {sections.map((s, i) => s.header ? (
        <div key={i} style={{
          fontFamily: 'var(--t-mono)', fontSize: 9, letterSpacing: '0.14em',
          textTransform: 'uppercase', color: 'var(--t-muted)',
          padding: '12px 10px 4px',
        }}>
          {s.header}
        </div>
      ) : (
        <a key={s.id} href="#" style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '6px 10px', borderRadius: 5,
          fontSize: 13, textDecoration: 'none',
          color: active === s.id ? 'var(--t-ink)' : 'var(--t-ink-2)',
          background: active === s.id ? 'var(--t-surface-2)' : 'transparent',
          fontWeight: active === s.id ? 500 : 400,
        }}>
          {s.dot && (
            <span style={{
              width: 6, height: 6, borderRadius: '50%',
              background: s.dot === 'ok' ? 'var(--t-ok)' : 'var(--t-muted)',
            }} />
          )}
          <span style={{ flex: 1 }}>{s.label}</span>
          {s.badge && (
            <span style={{
              fontFamily: 'var(--t-mono)', fontSize: 10,
              padding: '1px 6px', borderRadius: 4,
              background: s.badgeTone === 'warn' ? 'color-mix(in oklab, var(--t-warn) 18%, transparent)' : 'var(--t-surface-3)',
              color: s.badgeTone === 'warn' ? 'var(--t-warn)' : 'var(--t-muted)',
            }}>{s.badge}</span>
          )}
          {s.kbd && !s.badge && (
            <span style={{
              fontFamily: 'var(--t-mono)', fontSize: 9,
              color: 'var(--t-mute-2)', letterSpacing: '0.08em',
            }}>{s.kbd}</span>
          )}
        </a>
      ))}

      <div style={{ flex: 1 }} />
      <div style={{
        padding: '10px', borderTop: '1px solid var(--t-rule)',
        fontFamily: 'var(--t-mono)', fontSize: 9, color: 'var(--t-muted)',
        display: 'flex', justifyContent: 'space-between', letterSpacing: '0.04em',
      }}>
        <span>api: ok</span><span>⌘ K</span>
      </div>
    </aside>
  );
}

function TechTopbar({ title, crumbs, actions }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '10px 20px', borderBottom: '1px solid var(--t-rule)',
      background: 'var(--t-surface)', height: 48, flexShrink: 0,
      fontFamily: 'var(--t-sans)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
        {crumbs.map((c, i) => (
          <React.Fragment key={i}>
            <span style={{
              color: i === crumbs.length - 1 ? 'var(--t-ink)' : 'var(--t-muted)',
              fontWeight: i === crumbs.length - 1 ? 500 : 400,
            }}>{c}</span>
            {i < crumbs.length - 1 && <span style={{ color: 'var(--t-mute-2)' }}>/</span>}
          </React.Fragment>
        ))}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        {actions}
      </div>
    </div>
  );
}

function TechButton({ variant = 'secondary', children, icon }) {
  const st = variant === 'primary' ? {
    background: 'var(--t-ink)', color: 'var(--t-surface)',
    border: '1px solid var(--t-ink)',
  } : variant === 'danger' ? {
    background: 'transparent', color: 'var(--t-err)',
    border: '1px solid color-mix(in oklab, var(--t-err) 40%, transparent)',
  } : {
    background: 'var(--t-surface)', color: 'var(--t-ink-2)',
    border: '1px solid var(--t-rule-2)',
  };
  return (
    <button style={{
      ...st, padding: '5px 10px', borderRadius: 6, fontSize: 12, fontWeight: 500,
      cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6,
      fontFamily: 'var(--t-sans)',
    }}>
      {icon}{children}
    </button>
  );
}

/* Dashboard */

function TechKpiRow() {
  const kpis = [
    { label: 'Documentos processados', value: '12,847', delta: '+213', deltaTone: 'ok',   sub: '7d' },
    { label: 'Relevantes · IA',        value: '1,206',  delta: '9.4%', deltaTone: 'ai',   sub: 'do corpus' },
    { label: 'Fila de revisão',        value: '87',     delta: '+12',  deltaTone: 'warn', sub: '24h' },
    { label: 'Aprovados',              value: '734',    delta: '78%',  deltaTone: 'ok',   sub: 'taxa' },
    { label: 'Custo IA · mês',         value: 'US$ 42,1', delta: '−8%',  deltaTone: 'ok',   sub: 'vs mar' },
  ];
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)',
      border: '1px solid var(--t-rule)', borderRadius: 8, overflow: 'hidden',
      background: 'var(--t-surface)',
    }}>
      {kpis.map((k, i) => (
        <div key={k.label} style={{
          padding: '14px 16px',
          borderRight: i < kpis.length - 1 ? '1px solid var(--t-rule)' : 'none',
        }}>
          <div style={{
            fontFamily: 'var(--t-mono)', fontSize: 10, letterSpacing: '0.06em',
            color: 'var(--t-muted)', textTransform: 'uppercase', marginBottom: 8,
          }}>{k.label}</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
            <span style={{
              fontFamily: 'var(--t-mono)', fontSize: 24, fontWeight: 500,
              color: 'var(--t-ink)', letterSpacing: '-0.02em',
            }}>{k.value}</span>
            <span style={{
              fontFamily: 'var(--t-mono)', fontSize: 11, fontWeight: 500,
              color: k.deltaTone === 'ok' ? 'var(--t-ok)'
                   : k.deltaTone === 'warn' ? 'var(--t-warn)'
                   : k.deltaTone === 'ai' ? 'var(--t-ai)'
                   : 'var(--t-muted)',
            }}>{k.delta}</span>
            <span style={{ fontSize: 10, color: 'var(--t-muted)' }}>{k.sub}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function TechHeatmap() {
  // heatmap 48 anos × 4 tipos
  const types = ['Decreto', 'Portaria', 'Resolução', 'Parecer', 'Lei'];
  const years = Array.from({ length: 48 }, (_, i) => 1961 + i);
  const data = types.map((_, ti) => years.map((_, yi) => {
    const y = 1961 + yi;
    let base = 0.1;
    if (y >= 1968 && y <= 1975) base += 0.4;
    if (y >= 1996 && y <= 2008) base += 0.5;
    if (ti === 1 && y >= 1996) base += 0.25;
    return Math.min(1, base + Math.random() * 0.4 - 0.1);
  }));

  return (
    <div style={{
      background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
      borderRadius: 8, padding: '16px 18px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14 }}>
        <div>
          <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>
            Densidade de relevantes por ano × tipo
          </h3>
          <p style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)', margin: '3px 0 0', letterSpacing: '0.04em' }}>
            n=1,206 · 1961–2008
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>
          <span>0</span>
          {[0.2, 0.4, 0.6, 0.8, 1].map(v => (
            <span key={v} style={{
              width: 14, height: 10,
              background: `color-mix(in oklab, var(--t-accent) ${v * 100}%, transparent)`,
              border: '1px solid var(--t-rule)',
            }} />
          ))}
          <span>max</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '70px 1fr', gap: 4 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {types.map(t => (
            <div key={t} style={{
              height: 18, fontSize: 11, color: 'var(--t-ink-2)',
              display: 'flex', alignItems: 'center',
            }}>{t}</div>
          ))}
        </div>
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: `repeat(48, 1fr)`, gap: 2 }}>
            {data.map((row, ri) => row.map((v, ci) => (
              <div key={`${ri}-${ci}`} style={{
                height: 18, borderRadius: 2,
                background: `color-mix(in oklab, var(--t-accent) ${Math.round(v * 100)}%, var(--t-surface-2))`,
              }} title={`${types[ri]} · ${1961 + ci}: ${Math.round(v * 30)} doc`} />
            )))}
          </div>
          <div style={{
            display: 'flex', justifyContent: 'space-between',
            fontFamily: 'var(--t-mono)', fontSize: 9, color: 'var(--t-muted)',
            marginTop: 6, letterSpacing: '0.04em',
          }}>
            <span>1961</span><span>1970</span><span>1980</span><span>1990</span><span>2000</span><span>2008</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function TechSearchesTable() {
  const rows = [
    { id: 417, term: 'tecnólogo',            years: '1961–2008', user: 'ana.p',    when: '14:03', status: 'running',  ex: 2840, rel: 312, db: 48, cost: 4.12 },
    { id: 416, term: 'escola técnica federal', years: '1961–1978', user: 'ana.p',    when: '09:12', status: 'done',     ex: 1120, rel: 201, db: 19, cost: 1.87 },
    { id: 415, term: '"curso superior de tecnologia"', years: '1996–2008', user: 'carlos.m', when: 'ontem', status: 'done', ex: 430,  rel: 88,  db: 14, cost: 0.74 },
    { id: 414, term: 'CEFET',                years: '1978–2008', user: 'ana.p',    when: '3d',    status: 'done',     ex: 980,  rel: 176, db: 22, cost: 1.64 },
    { id: 413, term: 'instituto federal',    years: '2008–2008', user: 'bolsa.j',  when: '4d',    status: 'failed',   ex: 0,    rel: 0,   db: 0,  cost: 0.00 },
    { id: 412, term: 'parecer CFE',          years: '1962–1996', user: 'ana.p',    when: '5d',    status: 'done',     ex: 1560, rel: 245, db: 31, cost: 2.30 },
  ];

  const statusChip = (s) => {
    const m = {
      running: { color: 'var(--t-accent)', label: 'em andamento', pulse: true },
      done:    { color: 'var(--t-ok)',    label: 'concluído' },
      failed:  { color: 'var(--t-err)',   label: 'falhou' },
    }[s];
    return (
      <span style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        fontFamily: 'var(--t-mono)', fontSize: 10, letterSpacing: '0.04em',
        color: m.color,
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: '50%', background: m.color,
          animation: m.pulse ? 'techPulse 1.6s ease-in-out infinite' : 'none',
        }} />
        {m.label}
      </span>
    );
  };

  return (
    <div style={{
      background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
      borderRadius: 8, overflow: 'hidden',
    }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '12px 16px', borderBottom: '1px solid var(--t-rule)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>Buscas</h3>
          <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>
            6 registros · filtro: 7d
          </span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <TechButton>Filtro</TechButton>
          <TechButton variant="primary">+ Nova</TechButton>
        </div>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr style={{
            fontFamily: 'var(--t-mono)', fontSize: 9, letterSpacing: '0.06em',
            textTransform: 'uppercase', color: 'var(--t-muted)',
            background: 'var(--t-surface-2)',
          }}>
            <th style={thStyle}>#</th>
            <th style={thStyle}>termo</th>
            <th style={thStyle}>período</th>
            <th style={thStyle}>status</th>
            <th style={{ ...thStyle, textAlign: 'right' }}>extr.</th>
            <th style={{ ...thStyle, textAlign: 'right' }}>rel.</th>
            <th style={{ ...thStyle, textAlign: 'right' }}>dúv.</th>
            <th style={{ ...thStyle, textAlign: 'right' }}>custo</th>
            <th style={thStyle}>por</th>
            <th style={{ ...thStyle, textAlign: 'right' }}>qnd</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.id} style={{ borderTop: '1px solid var(--t-rule)' }}>
              <td style={{ ...tdStyle, fontFamily: 'var(--t-mono)', color: 'var(--t-muted)' }}>{r.id}</td>
              <td style={{ ...tdStyle, fontWeight: 500, color: 'var(--t-ink)' }}>{r.term}</td>
              <td style={{ ...tdStyle, fontFamily: 'var(--t-mono)', color: 'var(--t-ink-2)' }}>{r.years}</td>
              <td style={tdStyle}>{statusChip(r.status)}</td>
              <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-ink-2)' }}>{r.ex.toLocaleString()}</td>
              <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-ok)' }}>{r.rel}</td>
              <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-warn)' }}>{r.db || '—'}</td>
              <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-muted)' }}>${r.cost.toFixed(2)}</td>
              <td style={{ ...tdStyle, color: 'var(--t-ink-2)' }}>{r.user}</td>
              <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-muted)' }}>{r.when}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const thStyle = { padding: '8px 12px', textAlign: 'left', fontWeight: 500 };
const tdStyle = { padding: '10px 12px' };

function TechPipelineCard() {
  const stages = [
    { label: 'Coleta',    ai: false, done: 47,  total: 47,  unit: 'anos' },
    { label: 'Extração',  ai: false, done: 2840, total: 2840, unit: 'pág' },
    { label: 'OCR',       ai: false, done: 2840, total: 2840, unit: 'txt' },
    { label: 'Classif.',  ai: true,  done: 1847, total: 2840, unit: 'doc', active: true },
    { label: 'Revisão',   ai: false, human: true, done: 0, total: 48, unit: 'doc' },
  ];
  return (
    <div style={{
      background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
      borderRadius: 8, padding: '16px 18px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14 }}>
        <div>
          <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>Pipeline ativa · #417</h3>
          <p style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)', margin: '3px 0 0', letterSpacing: '0.04em' }}>
            busca: "tecnólogo" · 1961–2008
          </p>
        </div>
        <span style={{
          fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-accent)',
          display: 'flex', alignItems: 'center', gap: 6,
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: 'var(--t-accent)',
            animation: 'techPulse 1.6s ease-in-out infinite',
          }} />
          em execução
        </span>
      </div>

      <div style={{ display: 'flex', gap: 4, marginBottom: 12 }}>
        {stages.map((s, i) => {
          const pct = s.total ? Math.round((s.done / s.total) * 100) : 0;
          const color = s.ai ? 'var(--t-ai)' : s.human ? 'var(--t-human)' : 'var(--t-ok)';
          return (
            <div key={i} style={{ flex: 1 }}>
              <div style={{
                height: 6, borderRadius: 3, overflow: 'hidden',
                background: 'var(--t-surface-3)',
              }}>
                <div style={{
                  height: '100%', width: `${pct}%`,
                  background: pct === 0 ? 'transparent' : color,
                }} />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 6 }}>
                {s.ai && <TagAI />}
                {s.human && <TagHuman />}
                <span style={{
                  fontSize: 11, color: s.active ? 'var(--t-ink)' : 'var(--t-ink-2)',
                  fontWeight: s.active ? 600 : 500,
                }}>{s.label}</span>
              </div>
              <div style={{
                fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)',
                marginTop: 2, letterSpacing: '0.04em',
              }}>
                {s.done}/{s.total} {s.unit}
              </div>
            </div>
          );
        })}
      </div>

      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10,
        paddingTop: 12, borderTop: '1px dashed var(--t-rule)',
        fontFamily: 'var(--t-mono)', fontSize: 11,
      }}>
        <div><span style={{ color: 'var(--t-muted)' }}>elapsed</span> <span style={{ color: 'var(--t-ink)' }}>24:51</span></div>
        <div><span style={{ color: 'var(--t-muted)' }}>eta</span> <span style={{ color: 'var(--t-ink)' }}>13:20</span></div>
        <div><span style={{ color: 'var(--t-muted)' }}>rate</span> <span style={{ color: 'var(--t-ink)' }}>1.2 doc/s</span></div>
        <div><span style={{ color: 'var(--t-muted)' }}>cost</span> <span style={{ color: 'var(--t-ink)' }}>$4.12</span></div>
      </div>
    </div>
  );
}

function TagAI() {
  return (
    <span style={{
      fontFamily: 'var(--t-mono)', fontSize: 8, letterSpacing: '0.1em',
      padding: '1px 4px', borderRadius: 3, color: 'var(--t-ai)',
      background: 'color-mix(in oklab, var(--t-ai) 12%, transparent)',
      fontWeight: 600,
    }}>AI</span>
  );
}
function TagHuman() {
  return (
    <span style={{
      fontFamily: 'var(--t-mono)', fontSize: 8, letterSpacing: '0.1em',
      padding: '1px 4px', borderRadius: 3, color: 'var(--t-human)',
      background: 'color-mix(in oklab, var(--t-human) 12%, transparent)',
      fontWeight: 600,
    }}>HUMAN</span>
  );
}

function TechActivity() {
  const events = [
    { t: '14:28:03', who: 'ai',    msg: 'classificou 32 docs em 7.4s',              hl: '1997' },
    { t: '14:27:12', who: 'human', msg: 'ana.p aprovou parecer CFE 987/71',         hl: null },
    { t: '14:25:44', who: 'ai',    msg: 'marcou 2 docs como duvidosos',             hl: null },
    { t: '14:24:01', who: 'system', msg: 'OCR concluído para edição 14.312/1996',   hl: null },
    { t: '14:22:58', who: 'human', msg: 'carlos.m rejeitou duplicata #9023',        hl: null },
    { t: '14:20:12', who: 'ai',    msg: 'iniciou classificação do ano 1996',        hl: null },
  ];
  const whoColor = { ai: 'var(--t-ai)', human: 'var(--t-human)', system: 'var(--t-muted)' };
  const whoLabel = { ai: 'AI',          human: 'HUM',             system: 'SYS' };
  return (
    <div style={{
      background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
      borderRadius: 8, padding: '16px 18px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 12 }}>
        <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>Atividade ao vivo</h3>
        <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>stream</span>
      </div>
      <div style={{ fontFamily: 'var(--t-mono)', fontSize: 11, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {events.map((e, i) => (
          <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'baseline' }}>
            <span style={{ color: 'var(--t-muted)', width: 60 }}>{e.t}</span>
            <span style={{
              color: whoColor[e.who], width: 32,
              fontWeight: 600, letterSpacing: '0.08em',
            }}>{whoLabel[e.who]}</span>
            <span style={{ color: 'var(--t-ink-2)', flex: 1 }}>
              {e.msg}
              {e.hl && <span style={{ color: 'var(--t-accent)', marginLeft: 6 }}>[{e.hl}]</span>}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TechDashboard({ dark, density }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) applyTechTheme(ref.current, dark); }, [dark]);
  const pad = density === 'compact' ? 16 : 24;
  return (
    <div ref={ref} style={{
      display: 'flex', minHeight: '100%', background: 'var(--t-bg)',
      color: 'var(--t-ink)',
      '--t-sans': '"Inter", "Geist", system-ui, sans-serif',
      '--t-mono': '"JetBrains Mono", "Geist Mono", ui-monospace, monospace',
      fontFamily: 'var(--t-sans)',
    }}>
      <TechSidebar active="painel" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TechTopbar
          crumbs={['Workspace', 'Painel']}
          actions={<>
            <TechButton>Exportar CSV</TechButton>
            <TechButton variant="primary">+ Nova busca</TechButton>
          </>}
        />
        <div style={{ padding: pad, display: 'flex', flexDirection: 'column', gap: pad, overflow: 'auto' }}>
          <div>
            <h1 style={{
              fontSize: 20, fontWeight: 600, color: 'var(--t-ink)', margin: 0,
              letterSpacing: '-0.01em',
            }}>
              Painel
            </h1>
            <p style={{ fontSize: 12, color: 'var(--t-muted)', margin: '4px 0 0' }}>
              Corpus IOMAT 1961–2008 · atualizado há 2s
            </p>
          </div>
          <TechKpiRow />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: pad }}>
            <TechPipelineCard />
            <TechActivity />
          </div>
          <TechHeatmap />
          <TechSearchesTable />
        </div>
      </div>
      <style>{`
        @keyframes techPulse {
          0%, 100% { opacity: 1; }
          50%      { opacity: 0.35; }
        }
      `}</style>
    </div>
  );
}

/* Progresso da busca */

function TechProgress({ dark, density }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) applyTechTheme(ref.current, dark); }, [dark]);
  const pad = density === 'compact' ? 16 : 24;

  const phases = [
    { k: 'coleta',   label: 'Coleta no IOMAT',     who: 'system', status: 'done',    done: 47,   total: 47,   unit: 'anos',    dur: '04:12', start: '13:38:12' },
    { k: 'extr',     label: 'Extração de páginas', who: 'system', status: 'done',    done: 2840, total: 2840, unit: 'páginas', dur: '08:47', start: '13:42:24' },
    { k: 'ocr',      label: 'OCR + limpeza',       who: 'system', status: 'done',    done: 2840, total: 2840, unit: 'textos',  dur: '12:03', start: '13:51:11' },
    { k: 'cls',      label: 'Classificação IA',    who: 'ai',     status: 'active',  done: 1847, total: 2840, unit: 'docs',    dur: '—',     start: '14:03:14', detail: 'gpt-4o-mini · batch size 8 · ano atual: 1997' },
    { k: 'rev',      label: 'Revisão humana',      who: 'human',  status: 'queued',  done: 0,    total: 48,   unit: 'docs',    dur: '—',     start: '—' },
    { k: 'cons',     label: 'Consolidação',        who: 'system', status: 'queued',  done: 0,    total: 1,    unit: '',        dur: '—',     start: '—' },
  ];

  return (
    <div ref={ref} style={{
      display: 'flex', minHeight: '100%', background: 'var(--t-bg)',
      color: 'var(--t-ink)',
      '--t-sans': '"Inter", "Geist", system-ui, sans-serif',
      '--t-mono': '"JetBrains Mono", "Geist Mono", ui-monospace, monospace',
      fontFamily: 'var(--t-sans)',
    }}>
      <TechSidebar active="buscas" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TechTopbar
          crumbs={['Workspace', 'Buscas', '#417']}
          actions={<>
            <TechButton>Ver documentos</TechButton>
            <TechButton variant="danger">Cancelar</TechButton>
          </>}
        />
        <div style={{ padding: pad, display: 'flex', flexDirection: 'column', gap: pad, overflow: 'auto' }}>

          {/* Header */}
          <div style={{
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8, padding: '18px 20px',
          }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6 }}>
              <span style={{
                fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-muted)',
                letterSpacing: '0.04em',
              }}>BUSCA #417</span>
              <span style={{
                display: 'inline-flex', alignItems: 'center', gap: 6,
                fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-accent)',
              }}>
                <span style={{
                  width: 6, height: 6, borderRadius: '50%', background: 'var(--t-accent)',
                  animation: 'techPulse 1.6s ease-in-out infinite',
                }} />
                em execução
              </span>
            </div>
            <h1 style={{
              fontSize: 22, fontWeight: 600, color: 'var(--t-ink)', margin: '0 0 6px',
              letterSpacing: '-0.01em',
              fontFamily: 'var(--t-mono)',
            }}>
              "tecnólogo" <span style={{ color: 'var(--t-muted)', fontWeight: 400 }}>· 1961–2008</span>
            </h1>
            <div style={{ fontSize: 12, color: 'var(--t-ink-2)' }}>
              iniciada por <span style={{ fontWeight: 500 }}>ana.p</span> às 13:38:12
              {' · '}modelo <span style={{ fontFamily: 'var(--t-mono)', color: 'var(--t-ai)' }}>gpt-4o-mini</span>
              {' · '}busca exata: <span style={{ fontFamily: 'var(--t-mono)' }}>false</span>
            </div>

            {/* KPIs inline */}
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 0,
              marginTop: 16, border: '1px solid var(--t-rule)', borderRadius: 6,
              overflow: 'hidden',
            }}>
              {[
                ['progresso',  '65%',       'accent'],
                ['decorrido',  '24:51',     'ink'],
                ['eta',        '13:20',     'ink'],
                ['taxa',       '1.2 doc/s', 'ink'],
                ['tokens',     '2.1M',      'muted'],
                ['custo',      '$4.12',     'ok'],
              ].map(([k, v, tone], i, a) => (
                <div key={k} style={{
                  padding: '10px 14px', background: 'var(--t-surface-2)',
                  borderRight: i < a.length - 1 ? '1px solid var(--t-rule)' : 'none',
                }}>
                  <div style={{
                    fontFamily: 'var(--t-mono)', fontSize: 9, letterSpacing: '0.08em',
                    color: 'var(--t-muted)', textTransform: 'uppercase', marginBottom: 4,
                  }}>{k}</div>
                  <div style={{
                    fontFamily: 'var(--t-mono)', fontSize: 16, fontWeight: 500,
                    color: tone === 'accent' ? 'var(--t-accent)'
                         : tone === 'ok' ? 'var(--t-ok)'
                         : tone === 'muted' ? 'var(--t-muted)'
                         : 'var(--t-ink)',
                  }}>{v}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Pipeline stages — como cards em esteira */}
          <div style={{
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8,
          }}>
            <div style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '12px 18px', borderBottom: '1px solid var(--t-rule)',
            }}>
              <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>
                Pipeline
              </h3>
              <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>
                3/6 concluídas
              </span>
            </div>
            <div>
              {phases.map((p, i) => {
                const done   = p.status === 'done';
                const active = p.status === 'active';
                const whoColor = p.who === 'ai' ? 'var(--t-ai)'
                               : p.who === 'human' ? 'var(--t-human)'
                               : 'var(--t-muted)';
                const pct = p.total ? Math.round((p.done / p.total) * 100) : 0;
                return (
                  <div key={p.k} style={{
                    display: 'grid',
                    gridTemplateColumns: '32px 180px 1fr 110px 70px',
                    gap: 16, padding: '14px 18px',
                    borderTop: i === 0 ? 'none' : '1px solid var(--t-rule)',
                    background: active ? 'color-mix(in oklab, var(--t-accent) 4%, transparent)' : 'transparent',
                    alignItems: 'center',
                  }}>
                    {/* step index */}
                    <div style={{
                      fontFamily: 'var(--t-mono)', fontSize: 11,
                      color: done ? 'var(--t-ok)' : active ? 'var(--t-accent)' : 'var(--t-mute-2)',
                      fontWeight: 600, textAlign: 'center',
                    }}>
                      {done ? '✓' : String(i + 1).padStart(2, '0')}
                    </div>

                    {/* label + who tag */}
                    <div>
                      <div style={{
                        fontSize: 13,
                        fontWeight: active ? 600 : 500,
                        color: done || active ? 'var(--t-ink)' : 'var(--t-muted)',
                        display: 'flex', alignItems: 'center', gap: 6,
                      }}>
                        {p.who === 'ai' && <TagAI />}
                        {p.who === 'human' && <TagHuman />}
                        {p.label}
                      </div>
                      {p.detail && (
                        <div style={{
                          fontFamily: 'var(--t-mono)', fontSize: 10,
                          color: 'var(--t-muted)', marginTop: 3, letterSpacing: '0.03em',
                        }}>
                          {p.detail}
                        </div>
                      )}
                    </div>

                    {/* progress bar */}
                    <div>
                      <div style={{
                        height: 6, borderRadius: 3, overflow: 'hidden',
                        background: 'var(--t-surface-3)',
                      }}>
                        <div style={{
                          height: '100%', width: `${done ? 100 : active ? pct : 0}%`,
                          background: done ? 'var(--t-ok)' : active ? whoColor : 'transparent',
                          transition: 'width 0.3s',
                        }} />
                      </div>
                      <div style={{
                        display: 'flex', justifyContent: 'space-between',
                        fontFamily: 'var(--t-mono)', fontSize: 10,
                        color: 'var(--t-muted)', marginTop: 5, letterSpacing: '0.03em',
                      }}>
                        <span>{p.done.toLocaleString()} / {p.total.toLocaleString()} {p.unit}</span>
                        <span style={{ color: done ? 'var(--t-ok)' : active ? 'var(--t-accent)' : 'var(--t-muted)' }}>
                          {done ? '100%' : active ? `${pct}%` : '—'}
                        </span>
                      </div>
                    </div>

                    <div style={{
                      fontFamily: 'var(--t-mono)', fontSize: 11,
                      color: 'var(--t-muted)', textAlign: 'right',
                    }}>
                      {p.start}
                    </div>
                    <div style={{
                      fontFamily: 'var(--t-mono)', fontSize: 11,
                      color: done || active ? 'var(--t-ink-2)' : 'var(--t-muted)',
                      textAlign: 'right',
                    }}>
                      {p.dur}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* resultado parcial + log */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: pad }}>
            {/* classificação parcial */}
            <div style={{
              background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
              borderRadius: 8, padding: '16px 18px',
            }}>
              <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: '0 0 14px' }}>
                Resultado parcial
              </h3>
              {[
                { label: 'Relevantes',  v: 312,  total: 1847, color: 'var(--t-ok)' },
                { label: 'Duvidosos',   v: 48,   total: 1847, color: 'var(--t-warn)' },
                { label: 'Descartados', v: 1487, total: 1847, color: 'var(--t-muted)' },
                { label: 'Erros IA',    v: 0,    total: 1847, color: 'var(--t-err)' },
              ].map(r => {
                const pct = r.total ? (r.v / r.total) * 100 : 0;
                return (
                  <div key={r.label} style={{ marginBottom: 10 }}>
                    <div style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
                      fontSize: 12, marginBottom: 4,
                    }}>
                      <span style={{ color: 'var(--t-ink-2)' }}>{r.label}</span>
                      <span style={{ fontFamily: 'var(--t-mono)', color: 'var(--t-ink)' }}>
                        {r.v.toLocaleString()}
                        <span style={{ color: 'var(--t-muted)', marginLeft: 6 }}>
                          {pct.toFixed(1)}%
                        </span>
                      </span>
                    </div>
                    <div style={{ height: 4, background: 'var(--t-surface-3)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${pct}%`, background: r.color }} />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* log ao vivo */}
            <div style={{
              background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
              borderRadius: 8, padding: '16px 18px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
                <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>
                  Log ao vivo
                </h3>
                <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-ok)' }}>
                  ● streaming
                </span>
              </div>
              <div style={{
                fontFamily: 'var(--t-mono)', fontSize: 11, lineHeight: 1.7,
                background: 'var(--t-bg)', border: '1px solid var(--t-rule)',
                borderRadius: 6, padding: '10px 12px',
                maxHeight: 260, overflow: 'hidden', position: 'relative',
              }}>
                {[
                  ['14:28:03', 'AI',  'classify', 'batch=8 ok · 1997/14312 p.4 → relevante (decreto)'],
                  ['14:28:02', 'AI',  'classify', 'batch=8 ok · 1997/14312 p.3 → irrelevante'],
                  ['14:28:02', 'AI',  'classify', 'batch=8 ok · 1997/14312 p.2 → duvidoso (parecer)'],
                  ['14:28:01', 'SYS', 'fetch',    'doc 1997/14312 p.2-9 loaded (7 pages)'],
                  ['14:27:58', 'AI',  'classify', 'batch=8 ok · 1996/13998 p.11 → relevante (lei)'],
                  ['14:27:44', 'HUM', 'review',   'ana.p approved doc#8234 → CFE 987/71'],
                  ['14:27:12', 'AI',  'classify', 'rate=1.2/s · tokens=12,405'],
                  ['14:26:50', 'SYS', 'checkpt',  'saved at 1996/13998'],
                ].map((l, i) => (
                  <div key={i} style={{
                    display: 'flex', gap: 10,
                    opacity: 1 - i * 0.08,
                  }}>
                    <span style={{ color: 'var(--t-muted)' }}>{l[0]}</span>
                    <span style={{
                      color: l[1] === 'AI' ? 'var(--t-ai)'
                           : l[1] === 'HUM' ? 'var(--t-human)' : 'var(--t-muted)',
                      width: 32, fontWeight: 600,
                    }}>{l[1]}</span>
                    <span style={{ color: 'var(--t-ink-2)', width: 64 }}>{l[2]}</span>
                    <span style={{ color: 'var(--t-ink)', flex: 1 }}>{l[3]}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>
      <style>{`
        @keyframes techPulse {
          0%, 100% { opacity: 1; }
          50%      { opacity: 0.35; }
        }
      `}</style>
    </div>
  );
}

Object.assign(window, { TechDashboard, TechProgress });
