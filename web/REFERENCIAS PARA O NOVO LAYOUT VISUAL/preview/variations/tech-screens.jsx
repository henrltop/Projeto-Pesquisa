/* Variação B — Telas adicionais
   Mesmo sistema visual de tech.jsx: sidebar, sans+mono, tags AI/HUM. */

/* ============================================================
   LISTA DE BUSCAS
   ============================================================ */

function TechSearchesList({ dark, density }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) applyTechTheme(ref.current, dark); }, [dark]);
  const pad = density === 'compact' ? 16 : 24;

  const rows = [
    { id: 417, term: 'tecnólogo',                   years: '1961–2008', user: 'ana.p',    when: 'há 12min', status: 'running',  ex: 2840, rel: 312, db: 48, desc: 1487, err: 0, cost: 4.12, progress: 65 },
    { id: 416, term: 'escola técnica federal',      years: '1961–1978', user: 'ana.p',    when: '09:12',    status: 'done',     ex: 1120, rel: 201, db: 19, desc: 900,  err: 0, cost: 1.87 },
    { id: 415, term: '"curso superior de tecnologia"', years: '1996–2008', user: 'carlos.m', when: 'ontem',    status: 'done',     ex: 430,  rel: 88,  db: 14, desc: 328,  err: 0, cost: 0.74 },
    { id: 414, term: 'CEFET',                       years: '1978–2008', user: 'ana.p',    when: '3d',       status: 'done',     ex: 980,  rel: 176, db: 22, desc: 782,  err: 0, cost: 1.64 },
    { id: 413, term: 'instituto federal',           years: '2008–2008', user: 'bolsa.j',  when: '4d',       status: 'failed',   ex: 0,    rel: 0,   db: 0,  desc: 0,    err: 1, cost: 0.00 },
    { id: 412, term: 'parecer CFE',                 years: '1962–1996', user: 'ana.p',    when: '5d',       status: 'done',     ex: 1560, rel: 245, db: 31, desc: 1284, err: 0, cost: 2.30 },
    { id: 411, term: '"ensino profissionalizante"', years: '1971–1996', user: 'carlos.m', when: '6d',       status: 'done',     ex: 892,  rel: 142, db: 18, desc: 732,  err: 0, cost: 1.42 },
    { id: 410, term: 'decreto-lei 464',             years: '1969–1971', user: 'ana.p',    when: '8d',       status: 'done',     ex: 78,   rel: 34,  db: 4,  desc: 40,   err: 0, cost: 0.18 },
    { id: 409, term: 'habilitação profissional',    years: '1971–1996', user: 'bolsa.j',  when: '10d',      status: 'done',     ex: 654,  rel: 98,  db: 12, desc: 544,  err: 0, cost: 1.08 },
  ];

  const totals = rows.reduce((acc, r) => ({
    ex: acc.ex + r.ex, rel: acc.rel + r.rel, db: acc.db + r.db, cost: acc.cost + r.cost,
  }), { ex: 0, rel: 0, db: 0, cost: 0 });

  const statusChip = (s) => {
    const m = {
      running: { color: 'var(--t-accent)', label: 'em andamento', pulse: true },
      done:    { color: 'var(--t-ok)',     label: 'concluído' },
      failed:  { color: 'var(--t-err)',    label: 'falhou' },
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
    <div ref={ref} style={{
      display: 'flex', minHeight: '100%', background: 'var(--t-bg)',
      color: 'var(--t-ink)',
      '--t-sans': '"Inter", system-ui, sans-serif',
      '--t-mono': '"JetBrains Mono", ui-monospace, monospace',
      fontFamily: 'var(--t-sans)',
    }}>
      <TechSidebar active="buscas" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TechTopbar
          crumbs={['Workspace', 'Buscas']}
          actions={<>
            <TechButton>Exportar CSV</TechButton>
            <TechButton variant="primary">+ Nova busca</TechButton>
          </>}
        />
        <div style={{ padding: pad, display: 'flex', flexDirection: 'column', gap: pad }}>

          {/* header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div>
              <h1 style={{ fontSize: 20, fontWeight: 600, color: 'var(--t-ink)', margin: 0, letterSpacing: '-0.01em' }}>
                Buscas
              </h1>
              <p style={{ fontSize: 12, color: 'var(--t-muted)', margin: '4px 0 0' }}>
                Todas as buscas executadas pela equipe · {rows.length} registros
              </p>
            </div>
            <div style={{
              fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-muted)',
              display: 'flex', gap: 16, letterSpacing: '0.04em',
            }}>
              <span>extraídos: <span style={{ color: 'var(--t-ink)' }}>{totals.ex.toLocaleString()}</span></span>
              <span>relevantes: <span style={{ color: 'var(--t-ok)' }}>{totals.rel.toLocaleString()}</span></span>
              <span>dúvidas: <span style={{ color: 'var(--t-warn)' }}>{totals.db}</span></span>
              <span>custo: <span style={{ color: 'var(--t-ink)' }}>${totals.cost.toFixed(2)}</span></span>
            </div>
          </div>

          {/* filter bar */}
          <div style={{
            display: 'flex', gap: 8, alignItems: 'center',
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8, padding: '10px 14px',
          }}>
            <input placeholder="Buscar por termo…" style={{
              flex: 1, border: 'none', outline: 'none', background: 'transparent',
              color: 'var(--t-ink)', fontSize: 13, fontFamily: 'var(--t-sans)',
            }} />
            <span style={{ width: 1, height: 16, background: 'var(--t-rule)' }} />
            {['Todos', 'Em andamento', 'Concluído', 'Falhou'].map((f, i) => (
              <button key={f} style={{
                fontFamily: 'var(--t-sans)', fontSize: 11,
                padding: '4px 10px', borderRadius: 4,
                border: '1px solid ' + (i === 0 ? 'var(--t-rule-2)' : 'transparent'),
                background: i === 0 ? 'var(--t-surface-2)' : 'transparent',
                color: i === 0 ? 'var(--t-ink)' : 'var(--t-muted)',
                cursor: 'pointer',
              }}>{f}</button>
            ))}
            <span style={{ width: 1, height: 16, background: 'var(--t-rule)' }} />
            <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>⌘F</span>
          </div>

          {/* table */}
          <div style={{
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8, overflow: 'hidden',
          }}>
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
                  <th style={{ ...thStyle, textAlign: 'right' }}>extraídos</th>
                  <th style={{ ...thStyle, textAlign: 'right' }}>relev.</th>
                  <th style={{ ...thStyle, textAlign: 'right' }}>dúvid.</th>
                  <th style={{ ...thStyle, textAlign: 'right' }}>descart.</th>
                  <th style={{ ...thStyle, textAlign: 'right' }}>erros</th>
                  <th style={{ ...thStyle, textAlign: 'right' }}>custo</th>
                  <th style={thStyle}>por</th>
                  <th style={{ ...thStyle, textAlign: 'right' }}>qnd</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.id} style={{ borderTop: '1px solid var(--t-rule)' }}>
                    <td style={{ ...tdStyle, fontFamily: 'var(--t-mono)', color: 'var(--t-muted)' }}>{r.id}</td>
                    <td style={{ ...tdStyle, fontWeight: 500, color: 'var(--t-ink)' }}>
                      {r.term}
                      {r.status === 'running' && (
                        <div style={{ marginTop: 4, height: 2, background: 'var(--t-surface-3)', borderRadius: 1, width: 140 }}>
                          <div style={{ height: '100%', width: `${r.progress}%`, background: 'var(--t-accent)', borderRadius: 1 }} />
                        </div>
                      )}
                    </td>
                    <td style={{ ...tdStyle, fontFamily: 'var(--t-mono)', color: 'var(--t-ink-2)' }}>{r.years}</td>
                    <td style={tdStyle}>{statusChip(r.status)}</td>
                    <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-ink-2)' }}>{r.ex.toLocaleString()}</td>
                    <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: r.rel ? 'var(--t-ok)' : 'var(--t-muted)' }}>{r.rel || '—'}</td>
                    <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: r.db ? 'var(--t-warn)' : 'var(--t-muted)' }}>{r.db || '—'}</td>
                    <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-muted)' }}>{r.desc || '—'}</td>
                    <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: r.err ? 'var(--t-err)' : 'var(--t-muted)' }}>{r.err || '—'}</td>
                    <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-muted)' }}>${r.cost.toFixed(2)}</td>
                    <td style={{ ...tdStyle, color: 'var(--t-ink-2)' }}>{r.user}</td>
                    <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'var(--t-mono)', color: 'var(--t-muted)' }}>{r.when}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{
            display: 'flex', justifyContent: 'space-between',
            fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)',
          }}>
            <span>mostrando 1–{rows.length} de {rows.length}</span>
            <span>⌘K para buscar · N para nova busca</span>
          </div>
        </div>
      </div>
      <style>{`
        @keyframes techPulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }
      `}</style>
    </div>
  );
}

/* ============================================================
   NOVA BUSCA
   ============================================================ */

function TechNewSearch({ dark, density }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) applyTechTheme(ref.current, dark); }, [dark]);
  const pad = density === 'compact' ? 16 : 24;

  const Field = ({ label, hint, children }) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={{
        fontFamily: 'var(--t-mono)', fontSize: 10, letterSpacing: '0.08em',
        textTransform: 'uppercase', color: 'var(--t-muted)',
      }}>{label}</label>
      {children}
      {hint && <div style={{ fontSize: 11, color: 'var(--t-muted)' }}>{hint}</div>}
    </div>
  );

  const inputSt = {
    background: 'var(--t-surface-2)', border: '1px solid var(--t-rule-2)',
    borderRadius: 6, padding: '9px 12px', fontSize: 13,
    color: 'var(--t-ink)', fontFamily: 'var(--t-sans)', outline: 'none',
  };

  return (
    <div ref={ref} style={{
      display: 'flex', minHeight: '100%', background: 'var(--t-bg)',
      color: 'var(--t-ink)',
      '--t-sans': '"Inter", system-ui, sans-serif',
      '--t-mono': '"JetBrains Mono", ui-monospace, monospace',
      fontFamily: 'var(--t-sans)',
    }}>
      <TechSidebar active="buscas" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TechTopbar
          crumbs={['Workspace', 'Buscas', 'Nova']}
          actions={<><TechButton>Cancelar</TechButton></>}
        />
        <div style={{ padding: pad, display: 'flex', justifyContent: 'center' }}>
          <div style={{ width: '100%', maxWidth: 720, display: 'flex', flexDirection: 'column', gap: pad }}>

            <div>
              <h1 style={{ fontSize: 22, fontWeight: 600, color: 'var(--t-ink)', margin: 0, letterSpacing: '-0.01em' }}>
                Nova busca
              </h1>
              <p style={{ fontSize: 13, color: 'var(--t-muted)', margin: '6px 0 0' }}>
                Define o termo e o recorte temporal. A pipeline coleta do IOMAT,
                executa OCR e envia à IA para classificação.
              </p>
            </div>

            {/* form card */}
            <div style={{
              background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
              borderRadius: 8, padding: 20, display: 'flex', flexDirection: 'column', gap: 18,
            }}>
              <Field label="Termo de busca" hint="Palavra ou expressão. Aceita acentuação. Sensível à configuração de busca exata abaixo.">
                <input defaultValue="tecnólogo" style={inputSt} />
              </Field>

              <label style={{
                display: 'flex', alignItems: 'flex-start', gap: 10, cursor: 'pointer',
                background: 'var(--t-surface-2)', border: '1px solid var(--t-rule)',
                borderRadius: 6, padding: '10px 12px',
              }}>
                <input type="checkbox" style={{ marginTop: 2, accentColor: 'var(--t-accent)' }} />
                <div>
                  <div style={{ fontSize: 13, color: 'var(--t-ink)', fontWeight: 500 }}>Busca exata (frase entre aspas)</div>
                  <div style={{ fontSize: 11, color: 'var(--t-muted)', marginTop: 2 }}>
                    Só retorna páginas que contenham a expressão literal, sem flexões.
                  </div>
                </div>
              </label>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                <Field label="Ano inicial">
                  <input type="number" defaultValue={1961} min={1961} max={2030} style={inputSt} />
                </Field>
                <Field label="Ano final">
                  <input type="number" defaultValue={2008} min={1961} max={2030} style={inputSt} />
                </Field>
              </div>

              {/* cobertura preview */}
              <div style={{
                background: 'var(--t-surface-2)', border: '1px solid var(--t-rule)',
                borderRadius: 6, padding: '12px 14px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'var(--t-muted)', textTransform: 'uppercase' }}>
                    Cobertura temporal
                  </span>
                  <span style={{ fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-ink)' }}>
                    48 anos · 1961–2008
                  </span>
                </div>
                <div style={{ display: 'flex', gap: 2 }}>
                  {Array.from({ length: 48 }).map((_, i) => (
                    <div key={i} style={{
                      flex: 1, height: 18,
                      background: 'var(--t-accent)', opacity: 0.6,
                      borderRadius: 1,
                    }} />
                  ))}
                </div>
                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  fontFamily: 'var(--t-mono)', fontSize: 9,
                  color: 'var(--t-muted)', marginTop: 4, letterSpacing: '0.04em',
                }}>
                  <span>1961</span><span>1970</span><span>1980</span><span>1990</span><span>2000</span><span>2008</span>
                </div>
              </div>

              {/* estimativa */}
              <div style={{
                background: 'color-mix(in oklab, var(--t-ai) 6%, transparent)',
                border: '1px solid color-mix(in oklab, var(--t-ai) 30%, var(--t-rule))',
                borderRadius: 6, padding: '12px 14px',
                display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10,
              }}>
                {[
                  ['Docs estim.', '~2.400'],
                  ['Tempo estim.', '~38 min'],
                  ['Tokens estim.', '~1.8M'],
                  ['Custo estim.', 'US$ 3,60'],
                ].map(([k, v]) => (
                  <div key={k}>
                    <div style={{ fontFamily: 'var(--t-mono)', fontSize: 9, letterSpacing: '0.08em', color: 'var(--t-muted)', textTransform: 'uppercase', marginBottom: 3 }}>{k}</div>
                    <div style={{ fontFamily: 'var(--t-mono)', fontSize: 14, fontWeight: 500, color: 'var(--t-ink)' }}>{v}</div>
                  </div>
                ))}
              </div>

              <div style={{
                fontSize: 11, color: 'var(--t-muted)',
                fontFamily: 'var(--t-mono)', letterSpacing: '0.03em',
                paddingTop: 10, borderTop: '1px dashed var(--t-rule)',
              }}>
                modelo: <span style={{ color: 'var(--t-ai)' }}>gpt-4o-mini</span>
                {' · '}chave OpenAI: <span style={{ color: 'var(--t-ok)' }}>● configurada</span>
                {' · '}fila: <span style={{ color: 'var(--t-ink)' }}>classificacao</span>
              </div>

              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <TechButton>Cancelar</TechButton>
                <TechButton variant="primary">Iniciar pipeline →</TechButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   LISTA DE DOCUMENTOS
   ============================================================ */

function TechDocuments({ dark, density }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) applyTechTheme(ref.current, dark); }, [dark]);
  const pad = density === 'compact' ? 16 : 24;

  const docs = [
    { id: 8234, ano: 1971, ed: '14.032', pag: 4,  estado: 'aprovado_manual', tipo: 'Parecer CFE',   just: 'Parecer do Conselho Federal sobre reconhecimento de cursos de tecnólogos em processamento de dados.' },
    { id: 8233, ano: 1971, ed: '14.032', pag: 3,  estado: 'relevante_ia',    tipo: 'Decreto',       just: 'Decreto nº 68.908 estabelece normas para concessão de bolsas em nível de tecnólogo.' },
    { id: 8232, ano: 1971, ed: '14.031', pag: 12, estado: 'duvidoso_ia',     tipo: 'Portaria',      just: 'Menciona "tecnólogo" em contexto industrial; possível referência a formação de nível técnico.' },
    { id: 8231, ano: 1969, ed: '13.890', pag: 7,  estado: 'relevante_ia',    tipo: 'Decreto-Lei',   just: 'Decreto-Lei nº 464/69 fixa normas complementares à Reforma Universitária.' },
    { id: 8230, ano: 1996, ed: '15.412', pag: 2,  estado: 'relevante_ia',    tipo: 'Lei',           just: 'Lei nº 9.394/96 (LDB) estabelece diretrizes e bases da educação nacional.' },
    { id: 8229, ano: 1996, ed: '15.412', pag: 3,  estado: 'rejeitado_manual',tipo: 'Despacho',      just: 'Despacho de rotina sem conteúdo regulatório relevante para o tema.' },
    { id: 8228, ano: 2004, ed: '16.987', pag: 5,  estado: 'relevante_ia',    tipo: 'Decreto',       just: 'Decreto nº 5.154/2004 regulamenta § 2º do art. 36 e arts. 39 a 41 da LDB.' },
    { id: 8227, ano: 2008, ed: '17.442', pag: 1,  estado: 'aprovado_manual', tipo: 'Lei',           just: 'Lei nº 11.892/2008 institui a Rede Federal de Educação Profissional, Científica e Tecnológica.' },
    { id: 8226, ano: 1978, ed: '14.998', pag: 8,  estado: 'relevante_ia',    tipo: 'Lei',           just: 'Transformação dos CEFETs: criação dos Centros Federais de Educação Tecnológica.' },
    { id: 8225, ano: 1963, ed: '12.102', pag: 11, estado: 'irrelevante_ia',  tipo: '—',             just: 'Publicação administrativa não relacionada a ensino técnico ou tecnológico.' },
    { id: 8224, ano: 1997, ed: '15.501', pag: 6,  estado: 'duvidoso_ia',     tipo: 'Portaria',      just: 'Contexto ambíguo; cita tecnólogo mas em seção de licitação pública.' },
    { id: 8223, ano: 2001, ed: '16.332', pag: 14, estado: 'relevante_ia',    tipo: 'Parecer CNE',   just: 'Parecer CNE/CP nº 29/2002 sobre Diretrizes Curriculares Nacionais para Educação Profissional.' },
  ];

  const estadoChip = (estado) => {
    const map = {
      aprovado_manual:  { color: 'var(--t-ok)',     bg: 'color-mix(in oklab, var(--t-ok) 14%, transparent)',    icon: '✓', label: 'Aprovado',      hum: true },
      rejeitado_manual: { color: 'var(--t-err)',    bg: 'color-mix(in oklab, var(--t-err) 14%, transparent)',   icon: '✕', label: 'Rejeitado',     hum: true },
      relevante_ia:     { color: 'var(--t-ai)',     bg: 'color-mix(in oklab, var(--t-ai) 14%, transparent)',    icon: '●', label: 'Relevante',     ai: true },
      duvidoso_ia:      { color: 'var(--t-warn)',   bg: 'color-mix(in oklab, var(--t-warn) 14%, transparent)',  icon: '?', label: 'Duvidoso',      ai: true },
      irrelevante_ia:   { color: 'var(--t-muted)',  bg: 'var(--t-surface-3)',                                    icon: '○', label: 'Descartado',    ai: true },
    };
    const m = map[estado];
    return (
      <span style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        padding: '2px 8px', borderRadius: 4, fontSize: 11,
        color: m.color, background: m.bg, fontWeight: 500,
        fontFamily: 'var(--t-sans)',
      }}>
        <span style={{ fontSize: 10 }}>{m.icon}</span>
        {m.label}
        {m.ai && <span style={{ fontFamily: 'var(--t-mono)', fontSize: 8, opacity: 0.75 }}>IA</span>}
        {m.hum && <span style={{ fontFamily: 'var(--t-mono)', fontSize: 8, opacity: 0.75 }}>HUM</span>}
      </span>
    );
  };

  return (
    <div ref={ref} style={{
      display: 'flex', minHeight: '100%', background: 'var(--t-bg)',
      color: 'var(--t-ink)',
      '--t-sans': '"Inter", system-ui, sans-serif',
      '--t-mono': '"JetBrains Mono", ui-monospace, monospace',
      fontFamily: 'var(--t-sans)',
    }}>
      <TechSidebar active="documentos" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TechTopbar
          crumbs={['Workspace', 'Documentos']}
          actions={<>
            <TechButton>Exportar</TechButton>
            <TechButton variant="primary">Visão por ano</TechButton>
          </>}
        />
        <div style={{ padding: pad, display: 'flex', flexDirection: 'column', gap: pad }}>

          {/* header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div>
              <h1 style={{ fontSize: 20, fontWeight: 600, color: 'var(--t-ink)', margin: 0, letterSpacing: '-0.01em' }}>
                Documentos
              </h1>
              <p style={{ fontSize: 12, color: 'var(--t-muted)', margin: '4px 0 0' }}>
                12.847 documentos no corpus · 1.206 relevantes · 87 em revisão
              </p>
            </div>
          </div>

          {/* filter bar avançada */}
          <div style={{
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8, padding: 14,
            display: 'grid', gridTemplateColumns: '2fr 1fr 1.5fr 1fr', gap: 10,
          }}>
            <div style={{
              background: 'var(--t-surface-2)', border: '1px solid var(--t-rule-2)',
              borderRadius: 6, padding: '7px 10px', display: 'flex', alignItems: 'center', gap: 6,
            }}>
              <span style={{ color: 'var(--t-muted)' }}>⌕</span>
              <input placeholder="Buscar no texto ou termo…" style={{
                flex: 1, border: 'none', background: 'transparent', outline: 'none',
                fontSize: 12, color: 'var(--t-ink)', fontFamily: 'var(--t-sans)',
              }} />
            </div>
            <div style={{
              background: 'var(--t-surface-2)', border: '1px solid var(--t-rule-2)',
              borderRadius: 6, padding: '7px 10px',
            }}>
              <input type="number" placeholder="Ano" style={{
                width: '100%', border: 'none', background: 'transparent', outline: 'none',
                fontSize: 12, color: 'var(--t-ink)', fontFamily: 'var(--t-mono)',
              }} />
            </div>
            <select style={{
              background: 'var(--t-surface-2)', border: '1px solid var(--t-rule-2)',
              borderRadius: 6, padding: '7px 10px', fontSize: 12, color: 'var(--t-ink)',
              fontFamily: 'var(--t-sans)', outline: 'none',
            }}>
              <option>Todas as classificações</option>
              <option>Relevante (IA)</option>
              <option>Duvidoso</option>
              <option>Aprovado</option>
              <option>Rejeitado</option>
              <option>Descartado</option>
            </select>
            <TechButton variant="primary">Aplicar filtros</TechButton>
          </div>

          {/* quick filters */}
          <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
            {[
              ['Todos',          '12.847', true],
              ['Relevante (IA)', '1.206',  false, 'ai'],
              ['Duvidoso',       '87',     false, 'warn'],
              ['Aprovado',       '734',    false, 'ok'],
              ['Rejeitado',      '208',    false, 'err'],
              ['Descartado',     '10.612', false, 'muted'],
            ].map(([label, count, active, tone]) => (
              <button key={label} style={{
                fontFamily: 'var(--t-sans)', fontSize: 11,
                padding: '5px 10px', borderRadius: 14,
                border: '1px solid ' + (active ? 'var(--t-ink)' : 'var(--t-rule-2)'),
                background: active ? 'var(--t-ink)' : 'var(--t-surface)',
                color: active ? 'var(--t-surface)' : 'var(--t-ink-2)',
                cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6,
              }}>
                {tone && !active && (
                  <span style={{
                    width: 6, height: 6, borderRadius: '50%',
                    background: tone === 'ai' ? 'var(--t-ai)'
                              : tone === 'warn' ? 'var(--t-warn)'
                              : tone === 'ok' ? 'var(--t-ok)'
                              : tone === 'err' ? 'var(--t-err)'
                              : 'var(--t-muted)',
                  }} />
                )}
                {label}
                <span style={{
                  fontFamily: 'var(--t-mono)', fontSize: 10,
                  color: active ? 'var(--t-surface)' : 'var(--t-muted)',
                  opacity: 0.8,
                }}>{count}</span>
              </button>
            ))}
          </div>

          {/* table */}
          <div style={{
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8, overflow: 'hidden',
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <thead>
                <tr style={{
                  fontFamily: 'var(--t-mono)', fontSize: 9, letterSpacing: '0.06em',
                  textTransform: 'uppercase', color: 'var(--t-muted)',
                  background: 'var(--t-surface-2)',
                }}>
                  <th style={thStyle}>id</th>
                  <th style={thStyle}>ano</th>
                  <th style={thStyle}>edição</th>
                  <th style={thStyle}>pág</th>
                  <th style={thStyle}>estado</th>
                  <th style={thStyle}>tipo de ato</th>
                  <th style={thStyle}>justificativa</th>
                  <th style={thStyle}></th>
                </tr>
              </thead>
              <tbody>
                {docs.map(d => (
                  <tr key={d.id} style={{ borderTop: '1px solid var(--t-rule)' }}>
                    <td style={{ ...tdStyle, fontFamily: 'var(--t-mono)', color: 'var(--t-muted)' }}>{d.id}</td>
                    <td style={{ ...tdStyle, fontFamily: 'var(--t-mono)', color: 'var(--t-ink)', fontWeight: 500 }}>{d.ano}</td>
                    <td style={{ ...tdStyle, fontFamily: 'var(--t-mono)', color: 'var(--t-ink-2)' }}>{d.ed}</td>
                    <td style={{ ...tdStyle, fontFamily: 'var(--t-mono)', color: 'var(--t-ink-2)' }}>{d.pag}</td>
                    <td style={tdStyle}>{estadoChip(d.estado)}</td>
                    <td style={{ ...tdStyle, color: 'var(--t-ink-2)' }}>{d.tipo}</td>
                    <td style={{ ...tdStyle, color: 'var(--t-muted)', maxWidth: 420, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={d.just}>{d.just}</td>
                    <td style={{ ...tdStyle, textAlign: 'right' }}>
                      <a href="#" style={{ fontSize: 11, color: 'var(--t-accent)', textDecoration: 'none', fontFamily: 'var(--t-sans)' }}>abrir →</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* pagination */}
          <div style={{
            display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 12,
            fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-muted)',
          }}>
            <TechButton>← anterior</TechButton>
            <span>página <span style={{ color: 'var(--t-ink)' }}>1</span> de 247</span>
            <TechButton>próxima →</TechButton>
          </div>

        </div>
      </div>
    </div>
  );
}

/* ============================================================
   DETALHE DO DOCUMENTO
   ============================================================ */

function TechDocumentDetail({ dark, density }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) applyTechTheme(ref.current, dark); }, [dark]);
  const pad = density === 'compact' ? 16 : 24;

  const textoBruto = `PARECER Nº 87/71

Considerando a necessidade de regulamentar a formação de tecnólogos em áreas estratégicas para o desenvolvimento industrial do país; considerando o disposto na Lei nº 5.540/68 e no Decreto-Lei nº 464/69; considerando, ainda, as deliberações do Conselho Federal de Educação em sua sessão plenária de 15 de março de 1971;

O CONSELHO FEDERAL DE EDUCAÇÃO, no uso de suas atribuições legais, DELIBERA:

Art. 1º - Ficam aprovadas as normas para autorização e reconhecimento de cursos superiores de tecnologia, de curta duração, a serem ministrados por estabelecimentos de ensino superior.

Art. 2º - Os cursos de que trata o artigo anterior deverão ter duração mínima de dois anos e máxima de três anos, totalizando entre 1.800 e 2.700 horas-aula.

§ 1º - A grade curricular deverá contemplar, além das disciplinas específicas da habilitação, formação geral em ciências exatas e aplicadas.

§ 2º - O estabelecimento de ensino deverá comprovar infraestrutura laboratorial compatível com a área do curso.

Art. 3º - O reconhecimento dos cursos far-se-á após inspeção por comissão designada pela Secretaria de Ensino Superior do MEC…`;

  const classificacoes = [
    { id: 3, clase: 'aprovado_manual', tipo: 'Parecer CFE', just: 'Documento regulatório central sobre cursos de tecnólogo. Revisão humana confirmou relevância.', modelo: 'ana.p',      when: '22/04 15:40', hum: true },
    { id: 2, clase: 'relevante_ia',    tipo: 'Parecer CFE', just: 'Menção direta a "cursos superiores de tecnologia" em ato regulatório. Alta confiança.',         modelo: 'gpt-4o-mini', when: '22/04 14:22', score: 0.94 },
    { id: 1, clase: 'duvidoso_ia',     tipo: 'Parecer',     just: 'Contém o termo mas em contexto de parecer amplo. Revisão sugerida.',                              modelo: 'gpt-4o-mini', when: '22/04 14:18', score: 0.61 },
  ];

  const claseStyle = (c) => {
    const m = {
      aprovado_manual: { color: 'var(--t-ok)',   label: 'APROVADO',   icon: '✓' },
      relevante_ia:    { color: 'var(--t-ai)',   label: 'RELEVANTE',  icon: '●' },
      duvidoso_ia:     { color: 'var(--t-warn)', label: 'DUVIDOSO',   icon: '?' },
    };
    return m[c];
  };

  return (
    <div ref={ref} style={{
      display: 'flex', minHeight: '100%', background: 'var(--t-bg)',
      color: 'var(--t-ink)',
      '--t-sans': '"Inter", system-ui, sans-serif',
      '--t-mono': '"JetBrains Mono", ui-monospace, monospace',
      fontFamily: 'var(--t-sans)',
    }}>
      <TechSidebar active="documentos" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TechTopbar
          crumbs={['Workspace', 'Documentos', '#8234']}
          actions={<>
            <TechButton>Ver no IOMAT ↗</TechButton>
            <TechButton>Abrir PDF</TechButton>
            <TechButton variant="primary">Revisar →</TechButton>
          </>}
        />
        <div style={{ padding: pad, display: 'flex', flexDirection: 'column', gap: pad }}>

          {/* header card */}
          <div style={{
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8, padding: 18,
          }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6 }}>
              <span style={{ fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-muted)', letterSpacing: '0.04em' }}>DOC #8234</span>
              <span style={{
                display: 'inline-flex', alignItems: 'center', gap: 4,
                padding: '2px 8px', borderRadius: 3, fontSize: 10,
                background: 'color-mix(in oklab, var(--t-ok) 14%, transparent)',
                color: 'var(--t-ok)', fontWeight: 500,
              }}>✓ APROVADO</span>
            </div>
            <h1 style={{
              fontSize: 20, fontWeight: 600, color: 'var(--t-ink)', margin: '0 0 8px',
              letterSpacing: '-0.01em',
            }}>
              Parecer CFE nº 87/71 · IOMAT edição 14.032, página 4
            </h1>
            <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--t-ink-2)', flexWrap: 'wrap' }}>
              <span><span style={{ color: 'var(--t-muted)' }}>ano:</span> <span style={{ fontFamily: 'var(--t-mono)' }}>1971</span></span>
              <span><span style={{ color: 'var(--t-muted)' }}>publicado em:</span> <span style={{ fontFamily: 'var(--t-mono)' }}>18/03/1971</span></span>
              <span><span style={{ color: 'var(--t-muted)' }}>OCR:</span> <span style={{ color: 'var(--t-ok)' }}>● 98% conf.</span></span>
              <span><span style={{ color: 'var(--t-muted)' }}>tokens:</span> <span style={{ fontFamily: 'var(--t-mono)' }}>1.842</span></span>
              <span><span style={{ color: 'var(--t-muted)' }}>custo IA:</span> <span style={{ fontFamily: 'var(--t-mono)' }}>$0.0031</span></span>
            </div>
          </div>

          {/* 2 columns */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: pad, alignItems: 'flex-start' }}>

            {/* col esquerda: texto + pdf */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: pad }}>
              {/* texto bruto */}
              <div style={{ background: 'var(--t-surface)', border: '1px solid var(--t-rule)', borderRadius: 8 }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 16px', borderBottom: '1px solid var(--t-rule)',
                }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>Texto extraído (OCR)</h3>
                  <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>1.842 tokens</span>
                </div>
                <div style={{
                  padding: '16px 20px', maxHeight: 440, overflow: 'auto',
                  fontFamily: '"Source Serif 4", Georgia, serif', fontSize: 13,
                  color: 'var(--t-ink-2)', lineHeight: 1.65,
                  whiteSpace: 'pre-wrap',
                }}>
                  {textoBruto.split(/(tecnólog\w+|Tecnológic\w+|Parecer|Conselho Federal de Educação|CFE|Lei nº \d+[\/\d]*|Decreto-Lei nº \d+[\/\d]*)/g).map((part, i) => {
                    if (/tecnólog|tecnológic/i.test(part)) {
                      return <mark key={i} style={{ background: 'color-mix(in oklab, var(--t-accent) 25%, transparent)', color: 'var(--t-ink)', padding: '0 2px', borderRadius: 2 }}>{part}</mark>;
                    }
                    if (/Lei nº|Decreto-Lei nº|CFE|Conselho Federal/i.test(part)) {
                      return <span key={i} style={{ color: 'var(--t-accent)', fontWeight: 500 }}>{part}</span>;
                    }
                    return part;
                  })}
                </div>
              </div>

              {/* pdf preview placeholder */}
              <div style={{ background: 'var(--t-surface)', border: '1px solid var(--t-rule)', borderRadius: 8 }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 16px', borderBottom: '1px solid var(--t-rule)',
                }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>Preview do PDF original</h3>
                  <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>IOMAT_14032.pdf · p. 4</span>
                </div>
                <div style={{
                  height: 340, background: 'var(--t-surface-2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--t-muted)', fontSize: 12, fontFamily: 'var(--t-mono)',
                  backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, var(--t-surface-3) 10px, var(--t-surface-3) 11px)',
                }}>
                  [ preview do PDF carregado via iframe ]
                </div>
              </div>
            </div>

            {/* col direita: classificações */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: pad }}>

              {/* histórico de classificações */}
              <div style={{ background: 'var(--t-surface)', border: '1px solid var(--t-rule)', borderRadius: 8 }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 16px', borderBottom: '1px solid var(--t-rule)',
                }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>Histórico de classificação</h3>
                  <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>{classificacoes.length} eventos</span>
                </div>
                <div style={{ padding: '4px 0' }}>
                  {classificacoes.map((c, i) => {
                    const s = claseStyle(c.clase);
                    return (
                      <div key={c.id} style={{
                        padding: '14px 16px',
                        borderTop: i === 0 ? 'none' : '1px solid var(--t-rule)',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <span style={{
                              fontFamily: 'var(--t-mono)', fontSize: 10, fontWeight: 600,
                              letterSpacing: '0.06em', color: s.color,
                            }}>{s.icon} {s.label}</span>
                            {c.hum ? <TagHuman /> : <TagAI />}
                          </div>
                          <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>{c.when}</span>
                        </div>
                        <div style={{ fontSize: 12, color: 'var(--t-ink)', fontWeight: 500, marginBottom: 4 }}>
                          {c.tipo}
                        </div>
                        <div style={{ fontSize: 11, color: 'var(--t-ink-2)', lineHeight: 1.55, marginBottom: 6 }}>
                          {c.just}
                        </div>
                        <div style={{ display: 'flex', gap: 10, fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>
                          <span>{c.hum ? 'revisor' : 'modelo'}: <span style={{ color: 'var(--t-ink-2)' }}>{c.modelo}</span></span>
                          {c.score !== undefined && (
                            <span>score: <span style={{ color: c.score > 0.8 ? 'var(--t-ok)' : c.score > 0.5 ? 'var(--t-warn)' : 'var(--t-err)' }}>{c.score.toFixed(2)}</span></span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* metadados */}
              <div style={{ background: 'var(--t-surface)', border: '1px solid var(--t-rule)', borderRadius: 8, padding: '14px 16px' }}>
                <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: '0 0 12px' }}>Metadados</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontFamily: 'var(--t-mono)', fontSize: 11 }}>
                  {[
                    ['busca', '#417 · "tecnólogo"'],
                    ['edicao_id', '14.032'],
                    ['pagina', '4'],
                    ['data_pub', '1971-03-18'],
                    ['ano', '1971'],
                    ['arquivo', 'iomat_14032_p4.pdf'],
                    ['tamanho', '142 KB'],
                    ['hash_sha1', 'a1f2…9c7e'],
                  ].map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--t-muted)' }}>{k}</span>
                      <span style={{ color: 'var(--t-ink)' }}>{v}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   FILA DE REVISÃO
   ============================================================ */

function TechReviewQueue({ dark, density }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) applyTechTheme(ref.current, dark); }, [dark]);
  const pad = density === 'compact' ? 16 : 24;

  const fila = [
    { id: 8232, ano: 1971, ed: '14.031', pag: 12, tipo: 'Portaria',      just: 'Menciona "tecnólogo" em contexto industrial; possível referência a formação de nível técnico.', score: 0.61, tempo: 'há 12min' },
    { id: 8224, ano: 1997, ed: '15.501', pag: 6,  tipo: 'Portaria',      just: 'Contexto ambíguo; cita tecnólogo mas em seção de licitação pública.',                          score: 0.54, tempo: 'há 15min' },
    { id: 8218, ano: 1984, ed: '15.102', pag: 3,  tipo: 'Despacho',      just: 'Trecho incompleto por falha de OCR; possível referência a curso técnico federal.',             score: 0.48, tempo: 'há 22min' },
    { id: 8212, ano: 1976, ed: '14.782', pag: 9,  tipo: 'Parecer',       just: 'Parecer sobre equivalência de diplomas; menciona tecnólogo mas não é o foco do ato.',           score: 0.58, tempo: 'há 28min' },
    { id: 8209, ano: 2002, ed: '16.512', pag: 7,  tipo: 'Portaria',      just: 'Portaria ministerial que autoriza cursos; precisa confirmar se inclui tecnólogo.',              score: 0.67, tempo: 'há 34min' },
    { id: 8201, ano: 1969, ed: '13.870', pag: 2,  tipo: 'Despacho',      just: 'Despacho administrativo com menção colateral ao ensino tecnológico.',                           score: 0.44, tempo: 'há 42min' },
    { id: 8195, ano: 1998, ed: '15.702', pag: 14, tipo: 'Resolução',     just: 'Resolução CNE/CEB trata de educação profissional em geral; relevância a confirmar.',           score: 0.71, tempo: 'há 1h' },
    { id: 8188, ano: 1965, ed: '12.442', pag: 5,  tipo: 'Decreto',       just: 'Decreto antigo sobre escolas técnicas federais; possível precursor histórico relevante.',      score: 0.63, tempo: 'há 1h' },
  ];

  return (
    <div ref={ref} style={{
      display: 'flex', minHeight: '100%', background: 'var(--t-bg)',
      color: 'var(--t-ink)',
      '--t-sans': '"Inter", system-ui, sans-serif',
      '--t-mono': '"JetBrains Mono", ui-monospace, monospace',
      fontFamily: 'var(--t-sans)',
    }}>
      <TechSidebar active="revisao" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TechTopbar
          crumbs={['Workspace', 'Revisão']}
          actions={<>
            <TechButton>Ordenar por score</TechButton>
            <TechButton variant="primary">Revisar próximo →</TechButton>
          </>}
        />
        <div style={{ padding: pad, display: 'flex', flexDirection: 'column', gap: pad }}>

          {/* header + stats */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div>
              <h1 style={{ fontSize: 20, fontWeight: 600, color: 'var(--t-ink)', margin: 0, letterSpacing: '-0.01em' }}>
                Fila de revisão
              </h1>
              <p style={{ fontSize: 12, color: 'var(--t-muted)', margin: '4px 0 0' }}>
                Documentos classificados como <span style={{ color: 'var(--t-warn)' }}>duvidosos</span> pela IA aguardando avaliação humana.
              </p>
            </div>
          </div>

          {/* stats strip */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 0,
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8, overflow: 'hidden',
          }}>
            {[
              ['NA FILA',       '87',    'warn',   'Duvidosos aguardando'],
              ['REVISADOS HOJE','12',    'ok',     'Por você · ana.p'],
              ['APROVADOS',     '734',   'ok',     'Taxa histórica: 78%'],
              ['TEMPO MÉDIO',   '1m 42s','ink',    'Por documento'],
            ].map(([k, v, tone, sub], i, a) => (
              <div key={k} style={{
                padding: '14px 18px',
                borderRight: i < a.length - 1 ? '1px solid var(--t-rule)' : 'none',
              }}>
                <div style={{ fontFamily: 'var(--t-mono)', fontSize: 9, letterSpacing: '0.1em', color: 'var(--t-muted)', marginBottom: 6 }}>{k}</div>
                <div style={{
                  fontFamily: 'var(--t-mono)', fontSize: 22, fontWeight: 500,
                  color: tone === 'warn' ? 'var(--t-warn)' : tone === 'ok' ? 'var(--t-ok)' : 'var(--t-ink)',
                  letterSpacing: '-0.01em',
                }}>{v}</div>
                <div style={{ fontSize: 10, color: 'var(--t-muted)', marginTop: 2 }}>{sub}</div>
              </div>
            ))}
          </div>

          {/* fila list */}
          <div style={{ background: 'var(--t-surface)', border: '1px solid var(--t-rule)', borderRadius: 8 }}>
            <div style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '12px 16px', borderBottom: '1px solid var(--t-rule)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>Aguardando avaliação</h3>
                <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>
                  mostrando 8 de 87
                </span>
              </div>
              <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>
                ordenado por: <span style={{ color: 'var(--t-ink)' }}>mais antigos primeiro</span>
              </span>
            </div>
            {fila.map((d, i) => (
              <div key={d.id} style={{
                padding: '16px 18px',
                borderTop: i === 0 ? 'none' : '1px solid var(--t-rule)',
                display: 'grid', gridTemplateColumns: '80px 1fr 160px 120px', gap: 16,
                alignItems: 'center',
                cursor: 'pointer',
              }}>
                <div>
                  <div style={{ fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-muted)' }}>#{d.id}</div>
                  <div style={{ fontFamily: 'var(--t-mono)', fontSize: 15, fontWeight: 500, color: 'var(--t-ink)', marginTop: 2 }}>{d.ano}</div>
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 4,
                      padding: '2px 7px', borderRadius: 3, fontSize: 10,
                      background: 'color-mix(in oklab, var(--t-warn) 14%, transparent)',
                      color: 'var(--t-warn)', fontWeight: 500, fontFamily: 'var(--t-sans)',
                    }}>? DUVIDOSO</span>
                    <TagAI />
                    <span style={{ fontSize: 12, color: 'var(--t-ink)', fontWeight: 500 }}>{d.tipo}</span>
                    <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>
                      ed. {d.ed} · p. {d.pag}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--t-ink-2)', lineHeight: 1.5 }}>{d.just}</div>
                </div>
                <div>
                  <div style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)', marginBottom: 4 }}>
                    CONFIANÇA IA
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ flex: 1, height: 4, background: 'var(--t-surface-3)', borderRadius: 2 }}>
                      <div style={{
                        height: '100%', width: `${d.score * 100}%`,
                        background: d.score > 0.65 ? 'var(--t-warn)' : 'var(--t-err)',
                        borderRadius: 2,
                      }} />
                    </div>
                    <span style={{ fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-ink)' }}>
                      {d.score.toFixed(2)}
                    </span>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)', marginBottom: 6 }}>{d.tempo}</div>
                  <a href="#" style={{ fontSize: 11, color: 'var(--t-accent)', textDecoration: 'none', fontFamily: 'var(--t-sans)', fontWeight: 500 }}>
                    revisar →
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   REVISÃO INDIVIDUAL
   ============================================================ */

function TechReviewDetail({ dark, density }) {
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) applyTechTheme(ref.current, dark); }, [dark]);
  const pad = density === 'compact' ? 16 : 24;

  return (
    <div ref={ref} style={{
      display: 'flex', minHeight: '100%', background: 'var(--t-bg)',
      color: 'var(--t-ink)',
      '--t-sans': '"Inter", system-ui, sans-serif',
      '--t-mono': '"JetBrains Mono", ui-monospace, monospace',
      fontFamily: 'var(--t-sans)',
    }}>
      <TechSidebar active="revisao" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TechTopbar
          crumbs={['Workspace', 'Revisão', '#8232']}
          actions={<>
            <TechButton>← Anterior</TechButton>
            <TechButton>Pular →</TechButton>
          </>}
        />
        <div style={{ padding: pad, display: 'flex', flexDirection: 'column', gap: pad }}>

          {/* progresso da fila */}
          <div style={{
            background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
            borderRadius: 8, padding: '12px 16px',
            display: 'flex', alignItems: 'center', gap: 16,
          }}>
            <span style={{ fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-muted)' }}>FILA</span>
            <div style={{ flex: 1, height: 4, background: 'var(--t-surface-3)', borderRadius: 2 }}>
              <div style={{ height: '100%', width: '14%', background: 'var(--t-accent)', borderRadius: 2 }} />
            </div>
            <span style={{ fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-ink)' }}>
              12 / 87 revisados hoje
            </span>
            <span style={{ fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-muted)' }}>· tempo médio 1m 42s</span>
          </div>

          {/* split: doc | review */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: pad, alignItems: 'flex-start' }}>

            {/* doc column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: pad }}>
              {/* doc header */}
              <div style={{
                background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
                borderRadius: 8, padding: 18,
              }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6 }}>
                  <span style={{ fontFamily: 'var(--t-mono)', fontSize: 11, color: 'var(--t-muted)' }}>DOC #8232</span>
                  <span style={{
                    display: 'inline-flex', alignItems: 'center', gap: 4,
                    padding: '2px 8px', borderRadius: 3, fontSize: 10,
                    background: 'color-mix(in oklab, var(--t-warn) 14%, transparent)',
                    color: 'var(--t-warn)', fontWeight: 500, fontFamily: 'var(--t-sans)',
                  }}>? DUVIDOSO <TagAI /></span>
                </div>
                <h2 style={{
                  fontSize: 17, fontWeight: 600, color: 'var(--t-ink)', margin: '0 0 8px',
                }}>
                  Portaria · IOMAT edição 14.031, página 12 · ano 1971
                </h2>
                <div style={{
                  padding: 12, borderRadius: 6,
                  background: 'color-mix(in oklab, var(--t-ai) 6%, transparent)',
                  border: '1px solid color-mix(in oklab, var(--t-ai) 25%, var(--t-rule))',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <TagAI />
                    <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'var(--t-ai)' }}>
                      JUSTIFICATIVA DA IA · score 0.61
                    </span>
                  </div>
                  <p style={{ fontSize: 13, color: 'var(--t-ink-2)', margin: 0, lineHeight: 1.55 }}>
                    Menciona "tecnólogo" em contexto industrial; possível referência a formação de
                    nível técnico, mas o ato principal trata de regulamentação de atividade profissional
                    e não de criação de curso. Precisa de avaliação humana para confirmar relevância.
                  </p>
                </div>
              </div>

              {/* text */}
              <div style={{ background: 'var(--t-surface)', border: '1px solid var(--t-rule)', borderRadius: 8 }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 16px', borderBottom: '1px solid var(--t-rule)',
                }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: 0 }}>Texto extraído</h3>
                  <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)' }}>892 tokens · OCR 94%</span>
                </div>
                <div style={{
                  padding: '16px 20px', maxHeight: 380, overflow: 'auto',
                  fontFamily: '"Source Serif 4", Georgia, serif', fontSize: 13,
                  color: 'var(--t-ink-2)', lineHeight: 1.7,
                }}>
                  <p>PORTARIA Nº 182, DE 14 DE MAIO DE 1971.</p>
                  <p>
                    O Ministro de Estado dos Transportes, no uso de suas atribuições, considerando
                    a necessidade de regulamentar o exercício profissional nas empresas de transporte
                    rodoviário de cargas, e considerando o disposto no Decreto-Lei nº 512/69,
                  </p>
                  <p><strong>RESOLVE:</strong></p>
                  <p>
                    Art. 1º - Fica estabelecido que os cargos técnicos nas empresas sob jurisdição
                    deste Ministério deverão ser ocupados por profissionais com formação de engenheiro,
                    <mark style={{ background: 'color-mix(in oklab, var(--t-accent) 30%, transparent)', color: 'var(--t-ink)', padding: '0 3px', borderRadius: 2 }}>tecnólogo</mark>
                    {' '}ou técnico de nível médio, conforme a complexidade da função.
                  </p>
                  <p>
                    Art. 2º - As empresas terão prazo de 180 dias, a contar da publicação desta
                    Portaria, para adequar seus quadros funcionais.
                  </p>
                  <p>
                    Art. 3º - A Secretaria de Transportes Rodoviários emitirá instrução normativa
                    complementar detalhando as atribuições de cada categoria.
                  </p>
                  <p>Art. 4º - Esta Portaria entra em vigor na data de sua publicação.</p>
                </div>
              </div>
            </div>

            {/* review column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: pad, position: 'sticky', top: pad }}>
              <div style={{ background: 'var(--t-surface)', border: '1px solid var(--t-rule)', borderRadius: 8, padding: 18 }}>
                <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--t-ink)', margin: '0 0 4px' }}>Sua decisão</h3>
                <p style={{ fontSize: 11, color: 'var(--t-muted)', margin: '0 0 16px' }}>
                  Este documento é relevante para o mapeamento da legislação do ensino superior tecnológico?
                </p>

                {/* decision buttons */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 16 }}>
                  <button style={{
                    padding: '12px 10px', borderRadius: 6,
                    border: '1px solid color-mix(in oklab, var(--t-ok) 35%, var(--t-rule))',
                    background: 'color-mix(in oklab, var(--t-ok) 10%, transparent)',
                    color: 'var(--t-ok)', cursor: 'pointer',
                    fontFamily: 'var(--t-sans)', fontSize: 13, fontWeight: 600,
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                  }}>
                    ✓ Aprovar
                    <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, opacity: 0.7 }}>A</span>
                  </button>
                  <button style={{
                    padding: '12px 10px', borderRadius: 6,
                    border: '1px solid color-mix(in oklab, var(--t-err) 35%, var(--t-rule))',
                    background: 'color-mix(in oklab, var(--t-err) 10%, transparent)',
                    color: 'var(--t-err)', cursor: 'pointer',
                    fontFamily: 'var(--t-sans)', fontSize: 13, fontWeight: 600,
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                  }}>
                    ✕ Rejeitar
                    <span style={{ fontFamily: 'var(--t-mono)', fontSize: 10, opacity: 0.7 }}>R</span>
                  </button>
                </div>

                {/* tipo de ato */}
                <div style={{ marginBottom: 14 }}>
                  <label style={{
                    fontFamily: 'var(--t-mono)', fontSize: 10, letterSpacing: '0.08em',
                    textTransform: 'uppercase', color: 'var(--t-muted)',
                    display: 'block', marginBottom: 6,
                  }}>Tipo de ato (opcional)</label>
                  <select style={{
                    width: '100%', padding: '8px 10px', borderRadius: 6,
                    border: '1px solid var(--t-rule-2)', background: 'var(--t-surface-2)',
                    fontSize: 12, color: 'var(--t-ink)', fontFamily: 'var(--t-sans)', outline: 'none',
                  }}>
                    <option>Portaria</option>
                    <option>Decreto</option>
                    <option>Lei</option>
                    <option>Parecer CFE/CNE</option>
                    <option>Resolução</option>
                    <option>Despacho</option>
                  </select>
                </div>

                {/* comentário */}
                <div style={{ marginBottom: 14 }}>
                  <label style={{
                    fontFamily: 'var(--t-mono)', fontSize: 10, letterSpacing: '0.08em',
                    textTransform: 'uppercase', color: 'var(--t-muted)',
                    display: 'block', marginBottom: 6,
                  }}>Comentário (opcional)</label>
                  <textarea rows={4} placeholder="Justificativa para a equipe e para auditoria futura…" style={{
                    width: '100%', padding: '10px 12px', borderRadius: 6,
                    border: '1px solid var(--t-rule-2)', background: 'var(--t-surface-2)',
                    fontSize: 12, color: 'var(--t-ink)', fontFamily: 'var(--t-sans)',
                    outline: 'none', resize: 'vertical',
                  }} />
                </div>

                <button style={{
                  width: '100%', padding: '10px', borderRadius: 6,
                  border: 'none', background: 'var(--t-ink)',
                  color: 'var(--t-surface)', cursor: 'pointer',
                  fontFamily: 'var(--t-sans)', fontSize: 13, fontWeight: 600,
                }}>
                  Salvar e ir para o próximo →
                </button>
                <div style={{ fontFamily: 'var(--t-mono)', fontSize: 10, color: 'var(--t-muted)', textAlign: 'center', marginTop: 8 }}>
                  atalho: <span style={{ color: 'var(--t-ink)' }}>Enter</span>
                </div>
              </div>

              {/* atalhos */}
              <div style={{
                background: 'var(--t-surface)', border: '1px solid var(--t-rule)',
                borderRadius: 8, padding: '12px 16px',
              }}>
                <div style={{ fontFamily: 'var(--t-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'var(--t-muted)', marginBottom: 10 }}>ATALHOS</div>
                {[
                  ['A', 'aprovar'],
                  ['R', 'rejeitar'],
                  ['→', 'próximo'],
                  ['←', 'anterior'],
                  ['S', 'pular'],
                ].map(([k, v]) => (
                  <div key={k} style={{
                    display: 'flex', justifyContent: 'space-between',
                    fontSize: 11, padding: '3px 0',
                  }}>
                    <span style={{ color: 'var(--t-ink-2)' }}>{v}</span>
                    <kbd style={{
                      fontFamily: 'var(--t-mono)', fontSize: 10,
                      padding: '1px 6px', borderRadius: 3,
                      background: 'var(--t-surface-2)', border: '1px solid var(--t-rule-2)',
                      color: 'var(--t-ink)',
                    }}>{k}</kbd>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, {
  TechSearchesList, TechNewSearch, TechDocuments,
  TechDocumentDetail, TechReviewQueue, TechReviewDetail,
});
